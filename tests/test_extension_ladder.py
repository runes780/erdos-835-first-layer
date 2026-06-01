import json
import subprocess
import sys
import unittest

from src.erdos835_one_color import OneColorConfig
from src.extension_ladder import (
    compute_extension_ladder_stats,
    export_extension_ladder_opb,
)


class ExtensionLadderStatsTests(unittest.TestCase):
    def test_e1_counts_match_staged_reduction(self):
        stats = compute_extension_ladder_stats(OneColorConfig(v=21, t=4, extension_count=1))

        self.assertEqual(stats.d_rows, 20349)
        self.assertEqual(stats.x_rows, 54264)
        self.assertEqual(stats.total_variables, 74613)
        self.assertEqual(stats.d_star_constraints, 5985)
        self.assertEqual(stats.point_extension_constraints, 20349)
        self.assertEqual(stats.exact_one_constraints, 26334)
        self.assertEqual(stats.disjointness_constraints, 0)
        self.assertEqual(stats.total_constraints, 26334)
        self.assertEqual(stats.d_row_exact_one_incidences, 122094)
        self.assertEqual(stats.x_row_exact_one_incidences, 325584)
        self.assertEqual(stats.exact_one_incidences, 447678)
        self.assertEqual(stats.disjointness_incidences, 0)
        self.assertEqual(stats.total_incidences, 447678)

    def test_e2_counts_include_disjointness_constraints(self):
        stats = compute_extension_ladder_stats(OneColorConfig(v=21, t=4, extension_count=2))

        self.assertEqual(stats.total_variables, 128877)
        self.assertEqual(stats.exact_one_constraints, 46683)
        self.assertEqual(stats.disjointness_constraints, 54264)
        self.assertEqual(stats.total_constraints, 100947)
        self.assertEqual(stats.exact_one_incidences, 793611)
        self.assertEqual(stats.disjointness_incidences, 108528)
        self.assertEqual(stats.total_incidences, 902139)


class ExtensionLadderOpbTests(unittest.TestCase):
    def test_e1_opb_has_d_star_and_point_extension_equalities(self):
        config = OneColorConfig(v=4, t=1, extension_count=1)

        text = export_extension_ladder_opb(config)

        lines = text.splitlines()
        self.assertEqual(lines[0], "* #variable= 10 #constraint= 10")
        self.assertIn("* row 1 D:0,1", lines)
        self.assertIn("* row 10 X:0:1,2,3", lines)
        self.assertIn("+1 x1 +1 x2 +1 x3 = 1 ; * T:0", lines)
        self.assertIn("+1 x1 +1 x7 +1 x8 = 1 ; * P:0:0,1", lines)
        self.assertNotIn(" <= 1 ; * U:", text)

    def test_e2_opb_adds_cross_family_disjointness(self):
        config = OneColorConfig(v=4, t=1, extension_count=2)

        text = export_extension_ladder_opb(config)

        lines = text.splitlines()
        self.assertEqual(lines[0], "* #variable= 14 #constraint= 20")
        self.assertIn("+1 x7 +1 x11 <= 1 ; * U:0,1,2", lines)

    def test_opb_can_omit_non_header_comments(self):
        config = OneColorConfig(v=4, t=1, extension_count=2)

        text = export_extension_ladder_opb(
            config,
            include_row_comments=False,
            include_column_comments=False,
        )

        self.assertTrue(all(line.startswith("* #") or " * " not in line for line in text.splitlines()))

    def test_opb_can_force_triple_matching_symmetry_break(self):
        config = OneColorConfig(v=7, t=4, extension_count=1)

        text = export_extension_ladder_opb(config, symmetry_break="triple-matching")

        lines = text.splitlines()
        self.assertEqual(lines[0], "* #variable= 28 #constraint= 58")
        self.assertTrue(any(line.endswith("; * force:D:0,1,2,3,4") for line in lines))
        self.assertTrue(any(line.endswith("; * force:D:0,1,2,5,6") for line in lines))

    def test_opb_can_force_triple_matching_with_off_triple_block(self):
        config = OneColorConfig(v=9, t=4, extension_count=1)

        text = export_extension_ladder_opb(config, symmetry_break="triple-matching-off-triple")

        lines = text.splitlines()
        self.assertEqual(lines[0], "* #variable= 210 #constraint= 256")
        self.assertTrue(any(line.endswith("; * force:D:0,1,2,3,4") for line in lines))
        self.assertTrue(any(line.endswith("; * force:D:0,1,2,5,6") for line in lines))
        self.assertTrue(any(line.endswith("; * force:D:0,1,2,7,8") for line in lines))
        self.assertTrue(any(line.endswith("; * force:D:0,1,3,5,7") for line in lines))

    def test_opb_can_add_d_lower_count_constraints(self):
        config = OneColorConfig(v=11, t=4, extension_count=1)

        text = export_extension_ladder_opb(config, add_d_lower_counts=True)

        lines = text.splitlines()
        self.assertEqual(lines[0], "* #variable= 924 #constraint= 1024")
        d3_line = next(line for line in lines if line.endswith("; * D3:0,1,2"))
        self.assertEqual(d3_line.count("+1 x"), 28)
        self.assertIn(" = 4 ;", d3_line)

    def test_opb_can_add_g4_count_constraints(self):
        config = OneColorConfig(v=7, t=4, extension_count=1)

        text = export_extension_ladder_opb(config, add_g4_counts=True)

        lines = text.splitlines()
        self.assertEqual(lines[0], "* #variable= 28 #constraint= 91")
        g4_line = next(line for line in lines if line.endswith("; * G4:0:0,1,2,3"))
        self.assertEqual(g4_line.count("+1 x"), 3)
        self.assertIn(" = 1 ;", g4_line)

    def test_opb_can_force_residual_orbit_branch_block(self):
        config = OneColorConfig(v=7, t=4, extension_count=1)

        text = export_extension_ladder_opb(config, forced_d_blocks=[(0, 1, 2, 3, 4)])

        lines = text.splitlines()
        self.assertEqual(lines[0], "* #variable= 28 #constraint= 57")
        self.assertIn("+1 x1 = 1 ; * force:D:0,1,2,3,4", lines)

    def test_g4_count_constraints_are_only_for_strength_four(self):
        config = OneColorConfig(v=6, t=1, extension_count=1)

        with self.assertRaisesRegex(ValueError, "G4 count constraints require t=4"):
            export_extension_ladder_opb(config, add_g4_counts=True)

    def test_problem_e1_g4_branch_opb_count_matches_next_experiment(self):
        config = OneColorConfig(v=21, t=4, extension_count=1)

        text = export_extension_ladder_opb(
            config,
            include_row_comments=False,
            include_column_comments=False,
            symmetry_break="triple-matching-off-triple",
            add_d_lower_counts=True,
            add_g4_counts=True,
            forced_d_blocks=[(0, 1, 3, 6, 8)],
        )

        self.assertEqual(text.splitlines()[0], "* #variable= 74613 #constraint= 33892")


class ExtensionLadderCliTests(unittest.TestCase):
    def test_stats_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.extension_ladder",
                "stats",
                "--v",
                "21",
                "--t",
                "4",
                "--extension-count",
                "1",
                "--json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        data = json.loads(completed.stdout)

        self.assertEqual(data["total_variables"], 74613)
        self.assertEqual(data["total_constraints"], 26334)


if __name__ == "__main__":
    unittest.main()
