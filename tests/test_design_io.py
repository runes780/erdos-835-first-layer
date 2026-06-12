import unittest

from src.design_io import format_blocks, parse_blocks


class DesignIoTests(unittest.TestCase):
    def test_parse_and_format_blocks(self):
        text = "0 1 2 3 4\n0,1,2,5,6\n"

        blocks = parse_blocks(text)

        self.assertEqual(blocks, [(0, 1, 2, 3, 4), (0, 1, 2, 5, 6)])
        self.assertEqual(format_blocks(blocks), "0 1 2 3 4\n0 1 2 5 6\n")


if __name__ == "__main__":
    unittest.main()
