import json
import tempfile
import unittest
from pathlib import Path

from src.cadical_portfolio import build_command, select_variants, write_manifest


class CadicalPortfolioTests(unittest.TestCase):
    def test_select_variants_can_limit_and_skip_baseline(self):
        variants = select_variants(max_jobs=3, skip_baseline=True)

        self.assertEqual([variant.label for variant in variants], ["preprocess1", "preprocess2", "optimize1"])
        self.assertEqual(variants[0].options, ("-P1",))

    def test_select_variants_can_start_after_existing_portfolio(self):
        variants = select_variants(max_jobs=2, skip_baseline=True, start_index=3)

        self.assertEqual([variant.label for variant in variants], ["optimize2", "local1"])

    def test_build_command_wraps_cadical_with_timeout_and_time(self):
        command = build_command(
            solver="artifacts/solvers/cadical_pkg/usr/bin/cadical",
            input_path="artifacts/problem835_e1.cnf",
            time_limit=3600,
            options=("-P1", "-O1"),
            time_bin="/usr/bin/time",
            timeout_bin="timeout",
        )

        self.assertEqual(
            command,
            [
                "/usr/bin/time",
                "-v",
                "timeout",
                "3600",
                "artifacts/solvers/cadical_pkg/usr/bin/cadical",
                "-P1",
                "-O1",
                "artifacts/problem835_e1.cnf",
            ],
        )

    def test_write_manifest_records_json_lines(self):
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "portfolio.jsonl"
            write_manifest(
                path,
                [
                    {
                        "label": "preprocess1",
                        "pid": 123,
                        "log": "logs/preprocess1.log",
                        "options": ["-P1"],
                        "command": ["cadical", "-P1", "problem.cnf"],
                    }
                ],
            )

            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0])["label"], "preprocess1")


if __name__ == "__main__":
    unittest.main()
