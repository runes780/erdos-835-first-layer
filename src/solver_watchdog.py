from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence

from src.roundingsat_portfolio import VARIANTS, build_command, write_manifest


DEFAULT_LOG_GLOBS = (
    "augmented_dlower_one_colour_roundingsat_lp0_6h.log",
    "portfolio_extra_6h_*.log",
    "portfolio_extra2_6h_*.log",
    "auto_followup_*.log",
)

DEFAULT_COMBO_LABELS = (
    "count0_luby50",
    "luby50_bumpfalse",
    "count0_bumpfalse",
    "count1_cancel0",
)

CONFLICT_RE = re.compile(r"#Conflicts:\s*(\d+)")
CONSTRAINT_RE = re.compile(r"#Constraints:\s*(\d+)")
STATUS_RE = re.compile(r"^s\s+.+$", re.MULTILINE)


@dataclass(frozen=True)
class LogSummary:
    label: str
    path: str
    status: str = ""
    conflicts: int = 0
    constraints: int = 0
    size_bytes: int = 0
    modified_time: str = ""


def detect_label(log_name: str) -> str:
    if log_name == "augmented_dlower_one_colour_roundingsat_lp0_6h.log":
        return "baseline"
    known_labels = sorted((variant.label for variant in VARIANTS), key=len, reverse=True)
    for label in known_labels:
        if log_name == f"{label}.log" or log_name.endswith(f"_{label}.log"):
            return label
    return Path(log_name).stem


def parse_log_text(
    log_name: str,
    text: str,
    *,
    size_bytes: int = 0,
    modified_time: str = "",
) -> LogSummary:
    statuses = STATUS_RE.findall(text)
    conflict_matches = CONFLICT_RE.findall(text)
    constraint_matches = CONSTRAINT_RE.findall(text)
    return LogSummary(
        label=detect_label(log_name),
        path=log_name,
        status=statuses[-1].strip() if statuses else "",
        conflicts=int(conflict_matches[-1]) if conflict_matches else 0,
        constraints=int(constraint_matches[-1]) if constraint_matches else 0,
        size_bytes=size_bytes,
        modified_time=modified_time,
    )


def parse_log_file(path: Path) -> LogSummary:
    text = path.read_text(encoding="utf-8", errors="ignore")
    stat = path.stat()
    return parse_log_text(
        path.name,
        text,
        size_bytes=stat.st_size,
        modified_time=datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
    )


def choose_followup_labels(summaries: Sequence[LogSummary], max_jobs: int) -> list[str]:
    if max_jobs <= 0:
        raise ValueError("max_jobs must be positive")

    ranked = sorted(
        (summary for summary in summaries if summary.conflicts > 0 and summary.label != "baseline"),
        key=lambda summary: summary.conflicts,
        reverse=True,
    )
    labels: list[str] = []
    available = {variant.label for variant in VARIANTS}

    for summary in ranked:
        if summary.label in available and summary.label not in labels:
            labels.append(summary.label)
        if len(labels) >= min(2, max_jobs):
            break

    for label in DEFAULT_COMBO_LABELS:
        if label in available and label not in labels:
            labels.append(label)
        if len(labels) >= max_jobs:
            break

    if not labels:
        labels.extend(["lubybase15", "luby200", "count0_luby50", "luby50_bumpfalse"][:max_jobs])

    return labels[:max_jobs]


def decisive_status(status: str) -> bool:
    upper = status.upper()
    return "UNSAT" in upper or "SATISFIABLE" in upper or upper.strip() == "S SAT"


def decide_next_action(
    *,
    summaries: Sequence[LogSummary],
    running_process_count: int,
    completed_followups: int,
    max_followups: int,
    followup_enabled: bool,
) -> str:
    if any(decisive_status(summary.status) for summary in summaries):
        return "stop_result"
    if running_process_count > 0:
        return "wait"
    if not followup_enabled or completed_followups >= max_followups:
        return "stop_no_result"
    return "launch_followup"


def load_state(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"completed_followups": 0, "launches": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def collect_logs(log_dir: Path, patterns: Sequence[str]) -> list[Path]:
    paths: dict[str, Path] = {}
    for pattern in patterns:
        for path in log_dir.glob(pattern):
            if path.is_file():
                paths[str(path)] = path
    return sorted(paths.values(), key=lambda path: path.name)


def collect_process_lines() -> list[str]:
    result = subprocess.run(
        ["ps", "-C", "roundingsat", "-o", "pid=,ppid=,%mem=,%cpu=,rss=,etime=,args="],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return [line.rstrip() for line in result.stdout.splitlines() if line.strip()]


def collect_command_output(command: Sequence[str]) -> str:
    result = subprocess.run(
        list(command),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result.stdout.strip()


def variant_options(label: str) -> tuple[str, ...]:
    for variant in VARIANTS:
        if variant.label == label:
            return variant.options
    raise ValueError(f"unknown variant label: {label}")


def launch_followup(args: argparse.Namespace, labels: Sequence[str]) -> dict[str, object]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = f"{args.followup_prefix}_{timestamp}"
    manifest = Path(args.log_dir) / f"{prefix}.jsonl"
    records: list[dict[str, object]] = []

    for label in labels:
        log_path = Path(args.log_dir) / f"{prefix}_{label}.log"
        command = build_command(
            args.solver,
            args.input,
            args.followup_time_limit,
            variant_options(label),
            time_bin=args.time_bin or None,
        )
        with log_path.open("wb") as log_file:
            process = subprocess.Popen(
                command,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        records.append(
            {
                "label": label,
                "pid": process.pid,
                "log": str(log_path),
                "options": list(variant_options(label)),
                "command": command,
            }
        )

    write_manifest(manifest, records)
    return {"prefix": prefix, "manifest": str(manifest), "records": records}


def write_report(
    path: Path,
    *,
    action: str,
    summaries: Sequence[LogSummary],
    process_lines: Sequence[str],
    state: dict[str, object],
    resource_text: str,
    launch: dict[str, object] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ranked = sorted(summaries, key=lambda summary: summary.conflicts, reverse=True)
    lines = [
        "# Solver watchdog report",
        "",
        f"- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Action: `{action}`",
        f"- Running roundingsat processes: {len(process_lines)}",
        f"- Completed followups: {state.get('completed_followups', 0)}",
        "",
        "## Logs",
        "",
        "| label | status | conflicts | constraints | modified | size KB |",
        "|---|---|---:|---:|---|---:|",
    ]
    for summary in ranked:
        status = summary.status or "RUNNING/NO_STATUS"
        lines.append(
            "| {label} | {status} | {conflicts} | {constraints} | {modified} | {size:.1f} |".format(
                label=summary.label,
                status=status.replace("|", "\\|"),
                conflicts=summary.conflicts,
                constraints=summary.constraints,
                modified=summary.modified_time,
                size=summary.size_bytes / 1024,
            )
        )

    lines.extend(["", "## Processes", ""])
    if process_lines:
        lines.append("```text")
        lines.extend(process_lines)
        lines.append("```")
    else:
        lines.append("No active `roundingsat` processes found.")

    if resource_text:
        lines.extend(["", "## Resources", "", "```text", resource_text, "```"])

    if launch is not None:
        lines.extend(["", "## Followup launch", "", f"- Prefix: `{launch['prefix']}`"])
        lines.append(f"- Manifest: `{launch['manifest']}`")
        lines.append("")
        lines.append("| label | pid | log |")
        lines.append("|---|---:|---|")
        for record in launch["records"]:
            lines.append(f"| {record['label']} | {record['pid']} | `{record['log']}` |")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_once(args: argparse.Namespace) -> str:
    log_dir = Path(args.log_dir)
    state_path = Path(args.state)
    state = load_state(state_path)
    summaries = [parse_log_file(path) for path in collect_logs(log_dir, args.log_glob)]
    process_lines = collect_process_lines()
    action = decide_next_action(
        summaries=summaries,
        running_process_count=len(process_lines),
        completed_followups=int(state.get("completed_followups", 0)),
        max_followups=args.max_followups,
        followup_enabled=not args.disable_followup,
    )

    resource_text = ""
    if args.include_resources:
        resource_text = collect_command_output(["bash", "-lc", "free -h && df -h /mnt/e"])

    launch: dict[str, object] | None = None
    if action == "launch_followup":
        labels = args.followup_labels or choose_followup_labels(summaries, args.followup_jobs)
        launch = launch_followup(args, labels)
        state["completed_followups"] = int(state.get("completed_followups", 0)) + 1
        launches = list(state.get("launches", []))
        launches.append(launch)
        state["launches"] = launches
        save_state(state_path, state)
        action = "launched_followup"

    write_report(
        Path(args.report),
        action=action,
        summaries=summaries,
        process_lines=process_lines,
        state=state,
        resource_text=resource_text,
        launch=launch,
    )
    return action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Watch RoundingSat logs and launch one focused follow-up round.")
    parser.add_argument("--log-dir", default="artifacts/solver_logs")
    parser.add_argument("--log-glob", action="append", default=list(DEFAULT_LOG_GLOBS))
    parser.add_argument("--report", default="artifacts/solver_logs/solver_watchdog_report.md")
    parser.add_argument("--state", default="artifacts/solver_logs/solver_watchdog_state.json")
    parser.add_argument("--interval-seconds", type=int, default=300)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--disable-followup", action="store_true")
    parser.add_argument("--max-followups", type=int, default=1)
    parser.add_argument("--followup-jobs", type=int, default=4)
    parser.add_argument("--followup-labels", default="")
    parser.add_argument("--followup-prefix", default="auto_followup")
    parser.add_argument("--followup-time-limit", type=int, default=21600)
    parser.add_argument("--solver", default="artifacts/solvers/roundingsat")
    parser.add_argument("--input", default="artifacts/problem835_one_color_augmented.opb")
    parser.add_argument("--time-bin", default="/usr/bin/time")
    parser.add_argument("--include-resources", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if isinstance(args.followup_labels, str):
        args.followup_labels = [label.strip() for label in args.followup_labels.split(",") if label.strip()]

    while True:
        action = run_once(args)
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t{action}", flush=True)
        if args.once or action in {"stop_result", "stop_no_result"}:
            return 0
        time.sleep(args.interval_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
