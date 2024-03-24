import time
from datetime import datetime, timedelta
from unittest.mock import patch
import unittest

import pytz
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from utils import measure_execution_time, SchedulerTrigger


class TestExecutionTime(unittest.TestCase):

    @patch("logging.getLogger")
    @patch("time.time", side_effect=[0, 1])
    def test_measure_execution_time(self, time_mock, mock_logger_getter):
        @measure_execution_time
        def test_func():
            time.sleep(0)  # To simulate some work

        test_func()
        mock_logger_getter.assert_called_once()
        mock_logger_getter.return_value.info.assert_called_once_with(
            "Execution time of test_func: 1000.0000 ms"
        )


class TestSchedularTrigger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tz = pytz.timezone("Africa/Cairo")
        cls.create_trigger = SchedulerTrigger()

    def test_create_trigger_with_start_in_and_frequency(self):
        start_in = "1m"
        frequency = "1h"
        trigger = self.create_trigger.perform(start_in, frequency)
        self.assertIsInstance(trigger, IntervalTrigger)

        # Getting the current time and stripping off the microseconds part
        now_without_microseconds = datetime.now(self.tz).replace(microsecond=0)
        expected_start_date = now_without_microseconds + timedelta(minutes=1)

        # Stripping off the microseconds part from the trigger's start_date
        trigger_start_date_without_microseconds = trigger.start_date.astimezone(
            self.tz
        ).replace(microsecond=0)
        self.assertEqual(trigger_start_date_without_microseconds, expected_start_date)
        self.assertEqual(trigger.interval, timedelta(hours=1))

    def test_create_trigger_with_start_in_only(self):
        start_in = "1m"
        trigger = self.create_trigger.perform(start_in, None)
        self.assertIsInstance(trigger, DateTrigger)

        # Getting the current time and stripping off the microseconds part
        now_without_microseconds = datetime.now(self.tz).replace(microsecond=0)
        expected_run_date = now_without_microseconds + timedelta(minutes=1)

        # Stripping off the microseconds part from the trigger's run_date
        trigger_run_date_without_microseconds = trigger.run_date.astimezone(
            self.tz
        ).replace(microsecond=0)

        self.assertEqual(trigger_run_date_without_microseconds, expected_run_date)

    def test_create_trigger_with_frequency_only(self):
        frequency = "1h"
        trigger = self.create_trigger.perform(None, frequency)
        self.assertIsInstance(trigger, IntervalTrigger)
        self.assertEqual(trigger.interval, timedelta(hours=1))

    def test_create_trigger_without_start_in_and_frequency(self):
        with self.assertRaisesRegex(
            ValueError, "Either start_in or frequency must be provided."
        ):
            self.create_trigger.perform(None, None)

    def test_parse_time_with_valid_time_str(self):
        time_str = "30m"
        parsed_time = self.create_trigger._parse_time(time_str)
        self.assertEqual(parsed_time, {"minutes": 30})

    def test_parse_time_with_invalid_time_str(self):
        time_str = "invalid"
        with self.assertRaisesRegex(
            ValueError,
            "Invalid time format. Expected format like '30s', '20m', or '1h'.",
        ):
            self.create_trigger._parse_time(time_str)

    def test_parse_time_with_invalid_time_unit(self):
        time_str = "1d"
        with self.assertRaisesRegex(
            ValueError,
            "Invalid time format. Expected format like '30s', '20m', or '1h'.",
        ):
            self.create_trigger._parse_time(time_str)
