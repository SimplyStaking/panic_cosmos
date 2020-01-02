import unittest
from datetime import timedelta

from src.utils.datetime import strfdelta


class TestDatetimeFunctions(unittest.TestCase):

    def test_strfdelta_returns_correct_string_for_integer_values(self):
        d = 1
        h = 2
        m = 3
        s = 4

        str_date = strfdelta(timedelta(days=d, hours=h, minutes=m, seconds=s),
                             '{days}d {hours}h {minutes}m {seconds}s')

        expected_d = d
        expected_h = h
        expected_m = m
        expected_s = s

        self.assertEqual(str_date,
                         '{}d {}h {}m {}s'.format(expected_d, expected_h,
                                                  expected_m, expected_s))

    def test_strfdelta_returns_correct_string_for_float_values(self):
        d = 1.5
        h = 2.5
        m = 3.5
        s = 4.5

        str_date = strfdelta(timedelta(days=d, hours=h, minutes=m, seconds=s),
                             '{days}d {hours}h {minutes}m {seconds}s')

        expected_d = 1
        expected_h = 2 + 12  # 0.5 days = 12 hours
        expected_m = 3 + 30  # 0.5 hours = 30 minutes
        expected_s = 4 + 30  # 0.5 minutes = 30 seconds

        self.assertEqual(str_date,
                         '{}d {}h {}m {}s'.format(expected_d, expected_h,
                                                  expected_m, expected_s))

    def test_strfdelta_includes_days_as_hours_if_days_not_in_fmt(self):
        d = 1
        h = 2
        m = 3
        s = 4

        str_date = strfdelta(timedelta(days=d, hours=h, minutes=m, seconds=s),
                             '{hours}h {minutes}m {seconds}s')

        expected_h = h + (d * 24)
        expected_m = m
        expected_s = s

        self.assertEqual(str_date, '{}h {}m {}s'.format(
            expected_h, expected_m, expected_s))
