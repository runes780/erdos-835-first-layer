import unittest

from src.erdos835_one_color import OneColorConfig, compute_d_only_stats, export_d_only_opb


class DOnlyTests(unittest.TestCase):
    def test_problem_835_d_only_counts(self):
        stats = compute_d_only_stats(OneColorConfig.problem_835())

        self.assertEqual(stats.variables, 20349)
        self.assertEqual(stats.constraints, 5985)
        self.assertEqual(stats.constraint_length, 17)

    def test_d_only_opb_exports_exact_cover_constraints(self):
        config = OneColorConfig(v=6, t=1, extension_count=2)

        text = export_d_only_opb(config)

        self.assertEqual(text.splitlines()[0], "* #variable= 15 #constraint= 6")
        self.assertIn("+1 x1 +1 x2 +1 x3 +1 x4 +1 x5 = 1 ; * T:0", text)

    def test_d_only_opb_can_force_triple_matching_symmetry_break(self):
        config = OneColorConfig(v=7, t=4, extension_count=1)

        text = export_d_only_opb(config, symmetry_break="triple-matching")

        self.assertEqual(text.splitlines()[0], "* #variable= 21 #constraint= 37")
        self.assertTrue(any(line.endswith("; * force:D:0,1,2,3,4") for line in text.splitlines()))
        self.assertTrue(any(line.endswith("; * force:D:0,1,2,5,6") for line in text.splitlines()))

    def test_d_only_opb_can_omit_solver_comments(self):
        config = OneColorConfig(v=6, t=1, extension_count=2)

        text = export_d_only_opb(
            config,
            include_row_comments=False,
            include_column_comments=False,
        )

        lines = text.splitlines()
        self.assertEqual(lines[0], "* #variable= 15 #constraint= 6")
        self.assertTrue(all(line.startswith("* #") or " * " not in line for line in lines))


if __name__ == "__main__":
    unittest.main()
