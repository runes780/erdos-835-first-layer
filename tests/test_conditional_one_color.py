import unittest

from src.conditional_one_color import allowed_u_blocks, compute_conditional_stats, export_conditional_opb
from src.erdos835_one_color import OneColorConfig


class ConditionalOneColorTests(unittest.TestCase):
    def test_problem_835_conditional_counts_from_note(self):
        config = OneColorConfig.problem_835()

        stats = compute_conditional_stats(config, d_block_count=1197, allowed_u_count=35112)

        self.assertEqual(stats.variables, 386232)
        self.assertEqual(stats.constraints, 245784)
        self.assertEqual(stats.incidences, 2703624)

    def test_allowed_u_blocks_remove_blocks_containing_d_block(self):
        config = OneColorConfig(v=4, t=1, extension_count=1)
        d_blocks = {(0, 1)}

        allowed = allowed_u_blocks(config, d_blocks)

        self.assertNotIn((0, 1, 2), allowed)
        self.assertNotIn((0, 1, 3), allowed)
        self.assertIn((0, 2, 3), allowed)
        self.assertIn((1, 2, 3), allowed)

    def test_conditional_opb_uses_only_allowed_u_blocks(self):
        config = OneColorConfig(v=4, t=1, extension_count=1)
        d_blocks = {(0, 1)}

        text = export_conditional_opb(config, d_blocks)

        lines = text.splitlines()
        self.assertEqual(lines[0], "* #variable= 2 #constraint= 7")
        self.assertIn("* row 1 X:0:0,2,3", lines)
        self.assertIn("* row 2 X:0:1,2,3", lines)
        self.assertIn("+1 x1 = 1 ; * P:0:0,2", lines)
        self.assertIn("+1 x1 +1 x2 = 1 ; * P:0:2,3", lines)
        self.assertIn("+1 x1 = 1 ; * U:0,2,3", lines)


if __name__ == "__main__":
    unittest.main()
