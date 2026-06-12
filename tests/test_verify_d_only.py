import unittest

from src.erdos835_one_color import OneColorConfig
from src.verify_d_only import verify_d_only


class VerifyDOnlyTests(unittest.TestCase):
    def test_toy_d_only_design_passes(self):
        config = OneColorConfig(v=6, t=1, extension_count=2)
        blocks = [(0, 1), (2, 3), (4, 5)]

        self.assertEqual(verify_d_only(config, blocks), [])

    def test_duplicate_point_cover_fails(self):
        config = OneColorConfig(v=6, t=1, extension_count=2)
        blocks = [(0, 1), (0, 2), (4, 5)]

        errors = verify_d_only(config, blocks)

        self.assertTrue(any("T:0" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
