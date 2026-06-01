import unittest

from src.erdos835_one_color import (
    OneColorConfig,
    compute_stats,
    comb_tuples,
    export_opb,
    iter_exact_cover_rows,
)
from src.verify_one_color import verify_one_color


def toy_candidate():
    """A resolvable toy exact-cover instance for v=6, t=1, m=2."""
    pairs = [(0, 1), (2, 3), (4, 5)]
    d_blocks = {tuple(sorted(pair)) for pair in pairs}
    g_blocks = [set(), set()]

    for bit0 in range(2):
        for bit1 in range(2):
            for bit2 in range(2):
                bits = (bit0, bit1, bit2)
                block = tuple(sorted(pairs[i][bits[i]] for i in range(3)))
                parity = sum(bits) % 2
                g_blocks[parity].add(block)

    return d_blocks, g_blocks


class OneColorStatsTests(unittest.TestCase):
    def test_problem_835_counts_match_the_first_layer_reduction(self):
        config = OneColorConfig.problem_835()
        stats = compute_stats(config)

        self.assertEqual(stats.d_rows, 20349)
        self.assertEqual(stats.x_rows, 596904)
        self.assertEqual(stats.total_rows, 617253)
        self.assertEqual(stats.t_columns, 5985)
        self.assertEqual(stats.pair_columns, 223839)
        self.assertEqual(stats.u_columns, 54264)
        self.assertEqual(stats.total_columns, 284088)
        self.assertEqual(stats.total_incidences, 4829496)
        self.assertEqual(stats.constraint_lengths, (17, 17, 17))

    def test_comb_tuples_are_sorted_and_lexicographic(self):
        self.assertEqual(
            comb_tuples(5, 3),
            [
                (0, 1, 2),
                (0, 1, 3),
                (0, 1, 4),
                (0, 2, 3),
                (0, 2, 4),
                (0, 3, 4),
                (1, 2, 3),
                (1, 2, 4),
                (1, 3, 4),
                (2, 3, 4),
            ],
        )

    def test_exact_cover_rows_have_stable_names_and_columns(self):
        config = OneColorConfig(v=4, t=1, extension_count=1)

        rows = list(iter_exact_cover_rows(config))

        self.assertEqual(len(rows), 10)
        self.assertEqual(
            rows[0],
            (
                "D:0,1",
                (
                    "T:0",
                    "T:1",
                    "P:0:0,1",
                    "U:0,1,2",
                    "U:0,1,3",
                ),
            ),
        )
        self.assertEqual(
            rows[-1],
            (
                "X:0:1,2,3",
                (
                    "P:0:1,2",
                    "P:0:1,3",
                    "P:0:2,3",
                    "U:1,2,3",
                ),
            ),
        )

    def test_opb_export_inverts_rows_to_exact_one_columns(self):
        config = OneColorConfig(v=4, t=1, extension_count=1)

        text = export_opb(config)

        lines = text.splitlines()
        self.assertEqual(lines[0], "* #variable= 10 #constraint= 14")
        self.assertIn("* row 1 D:0,1", lines)
        self.assertIn("* row 10 X:0:1,2,3", lines)
        self.assertIn("+1 x1 +1 x2 +1 x3 = 1 ; * T:0", lines)
        self.assertIn("+1 x1 +1 x7 +1 x8 = 1 ; * P:0:0,1", lines)

    def test_opb_export_can_omit_row_comments(self):
        config = OneColorConfig(v=4, t=1, extension_count=1)

        text = export_opb(config, include_row_comments=False)

        self.assertNotIn("* row 1 D:0,1", text)
        self.assertIn("+1 x1 +1 x2 +1 x3 = 1 ; * T:0", text)

    def test_opb_export_can_omit_all_non_header_comments_for_solvers(self):
        config = OneColorConfig(v=4, t=1, extension_count=1)

        text = export_opb(
            config,
            include_row_comments=False,
            include_column_comments=False,
        )

        lines = text.splitlines()
        self.assertEqual(lines[0], "* #variable= 10 #constraint= 14")
        self.assertTrue(all(line.startswith("* #") or " * " not in line for line in lines))
        self.assertIn("+1 x1 +1 x2 +1 x3 = 1 ;", lines)

    def test_opb_export_can_force_triple_matching_symmetry_break(self):
        config = OneColorConfig(v=7, t=4, extension_count=1)

        text = export_opb(config, symmetry_break="triple-matching")

        lines = text.splitlines()
        self.assertEqual(lines[0], "* #variable= 28 #constraint= 65")
        self.assertTrue(any(line.endswith("; * force:D:0,1,2,3,4") for line in lines))
        self.assertTrue(any(line.endswith("; * force:D:0,1,2,5,6") for line in lines))

    def test_opb_export_can_force_triple_matching_with_off_triple_block(self):
        config = OneColorConfig(v=9, t=4, extension_count=1)

        text = export_opb(config, symmetry_break="triple-matching-off-triple")

        lines = text.splitlines()
        self.assertEqual(lines[0], "* #variable= 210 #constraint= 340")
        self.assertTrue(any(line.endswith("; * force:D:0,1,2,3,4") for line in lines))
        self.assertTrue(any(line.endswith("; * force:D:0,1,2,5,6") for line in lines))
        self.assertTrue(any(line.endswith("; * force:D:0,1,2,7,8") for line in lines))
        self.assertTrue(any(line.endswith("; * force:D:0,1,3,5,7") for line in lines))

    def test_opb_export_can_add_g4_count_constraints(self):
        config = OneColorConfig(v=7, t=4, extension_count=1)

        text = export_opb(config, add_g4_counts=True)

        lines = text.splitlines()
        self.assertEqual(lines[0], "* #variable= 28 #constraint= 98")
        g4_line = next(line for line in lines if line.endswith("; * G4:0:0,1,2,3"))
        self.assertEqual(g4_line.count("+1 x"), 3)
        self.assertIn(" = 1 ;", g4_line)

    def test_g4_count_constraints_are_only_for_the_problem_strength(self):
        config = OneColorConfig(v=6, t=1, extension_count=2)

        with self.assertRaisesRegex(ValueError, "G4 count constraints require t=4"):
            export_opb(config, add_g4_counts=True)

    def test_opb_export_can_add_d_lower_count_constraints(self):
        config = OneColorConfig(v=11, t=4, extension_count=1)

        text = export_opb(config, add_d_lower_counts=True)

        lines = text.splitlines()
        self.assertEqual(lines[0], "* #variable= 924 #constraint= 1486")
        d3_line = next(line for line in lines if line.endswith("; * D3:0,1,2"))
        self.assertEqual(d3_line.count("+1 x"), 28)
        self.assertIn(" = 4 ;", d3_line)

    def test_d_lower_count_constraints_are_only_for_the_problem_strength(self):
        config = OneColorConfig(v=6, t=1, extension_count=2)

        with self.assertRaisesRegex(ValueError, "D lower count constraints require t=4"):
            export_opb(config, add_d_lower_counts=True)


class OneColorVerifierTests(unittest.TestCase):
    def test_toy_candidate_satisfies_all_exact_cover_constraints(self):
        config = OneColorConfig(v=6, t=1, extension_count=2)
        d_blocks, g_blocks = toy_candidate()

        errors = verify_one_color(config, d_blocks, g_blocks)

        self.assertEqual(errors, [])

    def test_verifier_reports_missing_shadow_block(self):
        config = OneColorConfig(v=6, t=1, extension_count=2)
        d_blocks, g_blocks = toy_candidate()
        g_blocks[0].remove(next(iter(g_blocks[0])))

        errors = verify_one_color(config, d_blocks, g_blocks)

        self.assertTrue(any("U-shadow" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
