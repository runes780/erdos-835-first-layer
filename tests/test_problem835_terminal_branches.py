import unittest

from src.problem835_terminal_branches import (
    TERMINAL_BRANCHES,
    audit_terminal_branch_orbits,
)


class Problem835TerminalBranchTests(unittest.TestCase):
    def test_terminal_branch_forced_blocks_match_pro_strategy(self):
        self.assertEqual(
            TERMINAL_BRANCHES,
            {
                "a_star": ((0, 1, 3, 6, 8), (0, 1, 3, 9, 11)),
                "b1": ((0, 1, 3, 6, 9), (0, 1, 3, 8, 10)),
                "b2": ((0, 1, 3, 6, 9), (0, 1, 3, 8, 11)),
            },
        )

    def test_terminal_orbit_audit_documents_branch_coverage(self):
        audits = {audit.name: audit for audit in audit_terminal_branch_orbits()}

        self.assertEqual(
            audits["initial_ab"].valid_fifth_points,
            tuple(range(8, 21)),
        )
        self.assertEqual(
            audits["initial_ab"].orbits,
            ((8,), tuple(range(9, 21))),
        )

        self.assertEqual(
            audits["branch_a"].valid_fifth_points,
            tuple(range(11, 21)),
        )
        self.assertEqual(
            audits["branch_a"].orbits,
            (tuple(range(11, 21)),),
        )

        self.assertEqual(
            audits["branch_b"].valid_fifth_points,
            (10, *range(11, 21)),
        )
        self.assertEqual(
            audits["branch_b"].orbits,
            ((10,), tuple(range(11, 21))),
        )


if __name__ == "__main__":
    unittest.main()
