import json
import subprocess
import sys
import unittest

from src.erdos835_one_color import OneColorConfig
from src.extension_ladder_cnf import (
    compute_extension_ladder_cnf_stats,
    export_extension_ladder_cnf,
)


class ExtensionLadderCnfStatsTests(unittest.TestCase):
    def test_e1_toy_cnf_counts_pairwise_exact_one_clauses(self):
        stats = compute_extension_ladder_cnf_stats(OneColorConfig(v=4, t=1, extension_count=1))

        self.assertEqual(stats.variables, 10)
        self.assertEqual(stats.exact_one_constraints, 10)
        self.assertEqual(stats.exact_one_clauses, 40)
        self.assertEqual(stats.disjointness_clauses, 0)
        self.assertEqual(stats.symmetry_unit_clauses, 0)
        self.assertEqual(stats.total_clauses, 40)

    def test_e2_toy_cnf_counts_disjointness_pairs(self):
        stats = compute_extension_ladder_cnf_stats(OneColorConfig(v=4, t=1, extension_count=2))

        self.assertEqual(stats.variables, 14)
        self.assertEqual(stats.exact_one_constraints, 16)
        self.assertEqual(stats.exact_one_clauses, 64)
        self.assertEqual(stats.disjointness_clauses, 4)
        self.assertEqual(stats.total_clauses, 68)

    def test_problem_e1_cnf_counts(self):
        stats = compute_extension_ladder_cnf_stats(
            OneColorConfig(v=21, t=4, extension_count=1),
            symmetry_break="triple-matching-off-triple",
        )

        self.assertEqual(stats.variables, 74613)
        self.assertEqual(stats.exact_one_constraints, 26334)
        self.assertEqual(stats.exact_one_clauses, 3607758)
        self.assertEqual(stats.symmetry_unit_clauses, 10)
        self.assertEqual(stats.total_clauses, 3607768)


class ExtensionLadderCnfExportTests(unittest.TestCase):
    def test_e1_toy_cnf_exports_dimacs_clauses(self):
        config = OneColorConfig(v=4, t=1, extension_count=1)

        text = export_extension_ladder_cnf(config)

        lines = text.splitlines()
        self.assertEqual(lines[0], "p cnf 10 40")
        self.assertIn("1 2 3 0", lines)
        self.assertIn("-1 -2 0", lines)
        self.assertIn("1 7 8 0", lines)

    def test_e2_toy_cnf_exports_disjointness_pairs(self):
        config = OneColorConfig(v=4, t=1, extension_count=2)

        text = export_extension_ladder_cnf(config)

        lines = text.splitlines()
        self.assertEqual(lines[0], "p cnf 14 68")
        self.assertIn("-7 -11 0", lines)


class ExtensionLadderCnfCliTests(unittest.TestCase):
    def test_stats_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.extension_ladder_cnf",
                "stats",
                "--v",
                "21",
                "--t",
                "4",
                "--extension-count",
                "1",
                "--symmetry-break",
                "triple-matching-off-triple",
                "--json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        data = json.loads(completed.stdout)

        self.assertEqual(data["variables"], 74613)
        self.assertEqual(data["total_clauses"], 3607768)


if __name__ == "__main__":
    unittest.main()
