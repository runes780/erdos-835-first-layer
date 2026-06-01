import json
import tempfile
import unittest
from pathlib import Path

from src.roundingsat_portfolio import build_command, select_variants, write_manifest


class RoundingSatPortfolioTests(unittest.TestCase):
    def test_select_variants_can_skip_baseline_and_limit_count(self):
        variants = select_variants(max_jobs=3, skip_baseline=True)

        self.assertEqual([variant.label for variant in variants], ["count0", "count1", "luby50"])
        self.assertEqual(variants[0].options, ("--prop-counting=0",))

    def test_select_variants_can_start_after_existing_portfolio(self):
        variants = select_variants(max_jobs=4, skip_baseline=True, start_index=5)

        self.assertEqual(
            [variant.label for variant in variants],
            ["lubybase3", "bumpfalse", "cancel0", "bumplits0"],
        )

    def test_build_command_keeps_variant_options_as_separate_arguments(self):
        command = build_command(
            solver="artifacts/solvers/roundingsat",
            input_path="artifacts/problem835_one_color_augmented.opb",
            time_limit=1800,
            options=("--prop-counting=0", "--luby-mult=50"),
            time_bin="/usr/bin/time",
        )

        self.assertEqual(
            command,
            [
                "/usr/bin/time",
                "-v",
                "artifacts/solvers/roundingsat",
                "--lp=0",
                "--prop-counting=0",
                "--luby-mult=50",
                "--time-limit=1800",
                "--print-sol=1",
                "artifacts/problem835_one_color_augmented.opb",
            ],
        )

    def test_write_manifest_records_commands_as_json_lines(self):
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "portfolio.jsonl"
            write_manifest(
                path,
                [
                    {
                        "label": "count0",
                        "pid": 123,
                        "log": "logs/count0.log",
                        "options": ["--prop-counting=0"],
                        "command": ["roundingsat", "--lp=0"],
                    }
                ],
            )

            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0])["label"], "count0")


if __name__ == "__main__":
    unittest.main()
