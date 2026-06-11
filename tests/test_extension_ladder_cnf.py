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

    def test_problem_e1_branch_cnf_adds_one_unit_clause(self):
        stats = compute_extension_ladder_cnf_stats(
            OneColorConfig(v=21, t=4, extension_count=1),
            symmetry_break="triple-matching-off-triple",
            forced_d_blocks=[(0, 1, 3, 6, 8)],
        )

        self.assertEqual(stats.variables, 74613)
        self.assertEqual(stats.symmetry_unit_clauses, 11)
        self.assertEqual(stats.total_clauses, 3607769)

    def test_problem_e1_terminal_branch_cnf_adds_two_unit_clauses(self):
        stats = compute_extension_ladder_cnf_stats(
            OneColorConfig(v=21, t=4, extension_count=1),
            symmetry_break="triple-matching-off-triple",
            forced_d_blocks=[(0, 1, 3, 6, 8), (0, 1, 3, 9, 11)],
        )

        self.assertEqual(stats.variables, 74613)
        self.assertEqual(stats.symmetry_unit_clauses, 12)
        self.assertEqual(stats.total_clauses, 3607770)

    def test_problem_e1_branch_d3_g4_cnf_counts(self):
        stats = compute_extension_ladder_cnf_stats(
            OneColorConfig(v=21, t=4, extension_count=1),
            symmetry_break="triple-matching-off-triple",
            forced_d_blocks=[(0, 1, 3, 6, 8)],
            add_d3_upper_counts=True,
            add_g4_upper_counts=True,
        )

        self.assertEqual(stats.variables, 8357853)
        self.assertEqual(stats.auxiliary_variables, 8283240)
        self.assertEqual(stats.d3_upper_constraints, 1330)
        self.assertEqual(stats.d3_upper_clauses, 3818430)
        self.assertEqual(stats.g4_upper_constraints, 5985)
        self.assertEqual(stats.g4_upper_clauses, 13645800)
        self.assertEqual(stats.total_clauses, 21071999)

    def test_problem_e2_branch_d3_g4_cnf_counts(self):
        stats = compute_extension_ladder_cnf_stats(
            OneColorConfig(v=21, t=4, extension_count=2),
            symmetry_break="triple-matching-off-triple",
            forced_d_blocks=[(0, 1, 3, 6, 8)],
            add_d3_upper_counts=True,
            add_g4_upper_counts=True,
        )

        self.assertEqual(stats.variables, 14875917)
        self.assertEqual(stats.auxiliary_variables, 14747040)
        self.assertEqual(stats.total_clauses, 37559876)


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

    def test_cnf_can_force_residual_orbit_branch_block(self):
        config = OneColorConfig(v=7, t=4, extension_count=1)

        text = export_extension_ladder_cnf(config, forced_d_blocks=[(0, 1, 2, 3, 4)])

        lines = text.splitlines()
        self.assertEqual(lines[0], "p cnf 28 225")
        self.assertIn("1 0", lines)

    def test_toy_cnf_can_add_sequential_upper_bound(self):
        config = OneColorConfig(v=4, t=1, extension_count=1)

        text = export_extension_ladder_cnf(config, extra_upper_bounds=[((1, 2, 3), 1)])

        lines = text.splitlines()
        self.assertEqual(lines[0], "p cnf 12 45")
        self.assertIn("-1 11 0", lines)
        self.assertIn("-2 -11 0", lines)
        self.assertIn("-3 -12 0", lines)


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
