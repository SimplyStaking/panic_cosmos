import unittest
from datetime import timedelta, datetime
from time import sleep

from src.utils.datetime import strfdelta
from src.utils.timing import TimedTaskLimiter, TimedOccurrenceTracker


class TestTimedTaskLimiter(unittest.TestCase):

    def setUp(self) -> None:
        self.interval_seconds = 2
        self.interval_timedelta = timedelta(seconds=self.interval_seconds)
        self.ttl = TimedTaskLimiter(self.interval_timedelta)

    def test_time_interval_is_supplied_time_interval(self):
        self.assertEqual(self.ttl.time_interval, self.interval_timedelta)

    def test_last_time_that_did_task_is_min_datetime(self):
        self.assertEqual(self.ttl.last_time_that_did_task, datetime.min)

    def test_can_do_task_if_not_done_before(self):
        self.assertTrue(self.ttl.can_do_task())

    def test_can_do_task_if_not_done_before_and_wait_time_interval(self):
        sleep(self.interval_seconds)
        self.assertTrue(self.ttl.can_do_task())

    def test_cannot_do_task_if_check_within_time_interval(self):
        self.ttl.did_task()
        self.assertFalse(self.ttl.can_do_task())

    def test_cannot_do_task_if_check_after_time_interval(self):
        self.ttl.did_task()
        sleep(self.interval_seconds)
        self.assertTrue(self.ttl.can_do_task())

    def test_do_task_updates_last_time_that_did_task_to_a_greater_time(self):
        before = self.ttl.last_time_that_did_task
        self.ttl.did_task()
        after = self.ttl.last_time_that_did_task
        self.assertGreater(after, before)

    def test_do_task_actually_allowed_even_if_cannot_do_task(self):
        self.ttl.did_task()
        self.assertFalse(self.ttl.can_do_task())
        self.ttl.did_task()

    def test_reset_sets_last_time_to_min_datetime(self):
        self.ttl.reset()
        self.assertEqual(self.ttl.last_time_that_did_task, datetime.min)

    def test_reset_sets_last_time_to_min_datetime_even_after_task_done(self):
        self.ttl.did_task()
        self.assertNotEqual(self.ttl.last_time_that_did_task, datetime.min)

        self.ttl.reset()
        self.assertEqual(self.ttl.last_time_that_did_task, datetime.min)


class TestTimedOccurrenceTracker(unittest.TestCase):

    def setUp(self) -> None:
        self.max_occurrences = 4
        self.interval_seconds = 3
        self.interval_timedelta = timedelta(seconds=self.interval_seconds)
        self.ttl = TimedOccurrenceTracker(self.max_occurrences,
                                          self.interval_timedelta)

    def test_max_occurrences_is_supplied_max_occurrences(self):
        self.assertEqual(self.ttl.max_occurrences, self.max_occurrences)

    def test_time_interval_is_supplied_time_interval(self):
        self.assertEqual(self.ttl.time_interval, self.interval_timedelta)

    def test_time_interval_pretty_returns_strfdelta_result(self):
        self.assertEqual(
            self.ttl.time_interval_pretty,
            strfdelta(self.interval_timedelta,
                      "{hours}h, {minutes}m, {seconds}s"))

    def test_not_too_many_occurrence_if_no_occurrences(self):
        self.assertFalse(self.ttl.too_many_occurrences())

    def test_not_too_many_occurrences_if_just_below_limit(self):
        for i in range(self.max_occurrences - 1):
            self.ttl.action_happened()

        self.assertFalse(self.ttl.too_many_occurrences())

    def test_too_many_occurrences_if_enough_occurrences(self):
        for i in range(self.max_occurrences):
            self.ttl.action_happened()

        self.assertTrue(self.ttl.too_many_occurrences())

    def test_not_too_many_occurrences_if_enough_occurrences_but_wait(self):
        for i in range(self.max_occurrences):
            self.ttl.action_happened()

        self.assertTrue(self.ttl.too_many_occurrences())
        sleep(self.interval_seconds)
        self.assertFalse(self.ttl.too_many_occurrences())

    def test_not_too_many_occurrences_if_reset(self):
        self.ttl.reset()
        self.assertFalse(self.ttl.too_many_occurrences())

    def test_not_too_many_occurrences_if_reset_after_enough_occurrences(self):
        for i in range(self.max_occurrences):
            self.ttl.action_happened()

        self.assertTrue(self.ttl.too_many_occurrences())
        self.ttl.reset()
        self.assertFalse(self.ttl.too_many_occurrences())
