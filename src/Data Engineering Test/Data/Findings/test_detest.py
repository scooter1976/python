import unittest
import detest
from datetime import datetime
from detest import normalise_unit


class MyTestCase(unittest.TestCase):
    def test_succcess(self):
        """
        Testing success
        """
        self.assertEqual(
            detest.normalise_unit(100.0, "kWH"), 100.0
        )  # add assertion here
        self.assertEqual(
            detest.normalise_unit(1.0, "MWH"), 1000.0
        )  # add assertion here
        self.assertEqual(
            detest.normalise_unit(1.5, "MWH"), 1500.0
        )  # add assertion here
        self.assertEqual(detest.normalise_unit(1000, "WH"), 1)  # add assertion here
        self.assertEqual(detest.normalise_unit(1500, "WH"), 1.5)  # add assertion here

        self.assertEqual(
            detest.normalise_time(datetime(2018, 9, 30, 21, 30, 00), "QLD"),
            datetime(2018, 9, 30, 21, 30, 00),
        )  # add assertion here
        self.assertEqual(
            detest.normalise_time(datetime(2018, 9, 30, 21, 30, 00), "SA"),
            datetime(2018, 9, 30, 21, 00, 00),
        )  # add assertion here
        self.assertEqual(
            detest.normalise_time(datetime(2018, 9, 30, 21, 30, 00), "WA"),
            datetime(2018, 9, 30, 19, 30, 00),
        )  # add assertion here

    def test_failure(self):
        """
        Testing Failure
        """
        self.assertNotEqual(
            detest.normalise_unit(1000, "kWH"), 100
        )  # add assertion here

        with self.assertRaises(ValueError):
            self.assertNotEqual(
                detest.normalise_unit(1000, "zzz"), 100
            )  # add assertion here

        self.assertNotEqual(
            detest.normalise_time(datetime(2018, 9, 30, 21, 30, 00), "QLD"),
            datetime(2018, 9, 30, 22, 30, 00),
        )  # add assertion here
        self.assertNotEqual(
            detest.normalise_time(datetime(2018, 9, 30, 21, 30, 00), "SA"),
            datetime(2018, 9, 30, 22, 00, 00),
        )  # add assertion here
        self.assertNotEqual(
            detest.normalise_time(datetime(2018, 9, 30, 21, 30, 00), "WA"),
            datetime(2018, 9, 30, 22, 30, 00),
        )  # add assertion here


if __name__ == "__main__":
    unittest.main()
