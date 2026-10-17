import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calc import add


class AddTest(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(add(2, 3), 5)

    def test_negative_and_positive(self):
        self.assertEqual(add(-2, 3), 1)

    def test_zeros(self):
        self.assertEqual(add(0, 0), 0)


if __name__ == "__main__":
    unittest.main()
