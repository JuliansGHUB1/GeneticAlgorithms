import unittest
from nurses import NurseSchedulingProblem  # import the class

class TestStreakFunction(unittest.TestCase):
    def setUp(self):
        print("Setting up!")
        self.scheduler = NurseSchedulingProblem(10)

    def test_short_streaks(self):
        self.assertEqual(self.scheduler.penalize_non_streaks("1001", len("1001")), 2)

    def test_long_streak(self):
        self.assertEqual(self.scheduler.penalize_non_streaks("1111000", len("1111000")), 0)

    def test_edge_case_last_four(self):
        self.assertEqual(self.scheduler.penalize_non_streaks("000111001101", len("000111001101")), 3)
    
    def test_edge_case_continuing_streak_violation(self):
        self.assertEqual(self.scheduler.penalize_non_streaks("000111001111", len("000111001111")), 1)

    def test_edge_case_continuing_streak_not_violation(self):
        self.assertEqual(self.scheduler.penalize_non_streaks("0001110101011", len("0001110101011")), 4)

    def test_generate_block_availability(self):
        self.assertEqual(len(self.scheduler.generate_block_availability()), 160)
        print("Availability string: " + self.scheduler.generate_block_availability())

if __name__ == '__main__':
    unittest.main()