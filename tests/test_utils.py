from datetime import datetime, timedelta
from unittest.mock import patch
import unittest
from scheduler.scheduler import CronScheduler

import pytz
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from scheduler.utils import job_wrapper, SchedulerTrigger


class TestJobWrapper(unittest.TestCase):
    def setUp(self):
        self.scheduler = CronScheduler()
        self.scheduler.job_data = {
            "test_job": {
                "execution_time": None,
                "error": None,
                "run_count": 0,
                "type": "Single Run",
            }
        }

    def tearDown(self):
        self.scheduler.scheduler.shutdown()

    @patch("scheduler.utils.logging.getLogger")
    @patch("scheduler.scheduler.CronScheduler.update_job_data")
    @patch("time.time")
    def test_job_wrapper(self, mock_time, mock_update_job_data, mock_logger):
        mock_time.side_effect = [1, 2]

        def sample_task():
            return "Task executed successfully."

        wrapped_func = job_wrapper(sample_task, self.scheduler, "test_job")
        result = wrapped_func()

        # assert the calls to update_job_data
        # assert call count
        self.assertEqual(mock_update_job_data.call_count, 4)
        mock_update_job_data.assert_any_call(
            "test_job", "status", self.scheduler.STATUS_RUNNING
        )
        mock_update_job_data.assert_any_call("test_job", "run_count", 1)
        mock_update_job_data.assert_any_call(
            "test_job", "execution_time", "1000.0000 ms"
        )
        mock_update_job_data.assert_any_call(
            "test_job", "status", self.scheduler.STATUS_COMPLETED
        )

        # assert logging calls
        mock_logger.assert_called_once_with("main")
        mock_logger.return_value.info.assert_called_once_with(
            "Job test_job (Function: sample_task) execution time: 1000.0000 ms"
        )

        # assert the result of the wrapped function
        self.assertEqual(result, "Task executed successfully.")

    @patch("scheduler.utils.logging.getLogger")
    @patch("scheduler.scheduler.CronScheduler.update_job_data")
    @patch("time.time")
    def test_job_wrapper_with_exception(
        self, mock_time, mock_update_job_data, mock_logger
    ):
        mock_time.side_effect = [1, 2]

        def sample_task():
            raise ValueError("Task failed.")

        wrapped_func = job_wrapper(sample_task, self.scheduler, "test_job")

        wrapped_func()

        # assert the calls to update_job_data
        # assert call count
        self.assertEqual(mock_update_job_data.call_count, 3)
        mock_update_job_data.assert_any_call(
            "test_job", "status", self.scheduler.STATUS_RUNNING
        )
        mock_update_job_data.assert_any_call(
            "test_job", "error", "ValueError: Task failed."
        )
        mock_update_job_data.assert_any_call(
            "test_job", "status", self.scheduler.STATUS_FAILED
        )

        # assert logging calls
        mock_logger.assert_called_once_with("main")
        mock_logger.return_value.error.assert_called_once_with(
            "Error in job test_job: ValueError: Task failed."
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
