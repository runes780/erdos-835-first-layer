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
