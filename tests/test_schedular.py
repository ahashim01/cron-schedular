import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from scheduler import CronScheduler
import tasks
import pytz


class TestCronScheduler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.interval = 1
        cls.args = ["test"]
        cls.tz = pytz.timezone("Africa/Cairo")

    def setUp(self):
        self.scheduler = CronScheduler()

    def tearDown(self):
        self.scheduler.scheduler.shutdown()

    def test_add_job(self):
        job_id = "test_job"
        self.scheduler.add_job(job_id, tasks.sample_task, start_in="1m", args=self.args)
        self.assertIn(job_id, self.scheduler.jobs)
        self.assertIsNotNone(self.scheduler.jobs[job_id])

    def test_add_duplicate_job(self):
        job_id = "duplicate_job"
        self.scheduler.add_job(job_id, tasks.sample_task, start_in="1m", args=self.args)
        with self.assertRaises(ValueError, msg=f"Job ID {job_id} already exists."):
            self.scheduler.add_job(
                job_id, tasks.sample_task, start_in="1m", args=self.args
            )

    def test_remove_job(self):
        job_id = "remove_job"
        self.scheduler.add_job(job_id, tasks.sample_task, start_in="1m", args=self.args)
        self.scheduler.remove_job(job_id)
        self.assertNotIn(job_id, self.scheduler.jobs)

    def test_get_job_info(self):
        job_id = "get_job_info"
        self.scheduler.add_job(job_id, tasks.sample_task, start_in="1m", args=self.args)
        job_info = self.scheduler.get_job_info(job_id)
        self.assertEqual(job_info["id"], job_id)
        self.assertIsInstance(job_info["next_run_time"], datetime)

    # @patch("scheduler.CronScheduler.execute_job")
    # def test_job_execution(self, mock_execute_job):
    #     job_id = "execute_job"
    #     self.scheduler.add_job(job_id, tasks.sample_task, start_in="1m", args=self.args)
    #     self.scheduler.execute_job(job_id, tasks.sample_task, *self.args)
    #     mock_execute_job.assert_called_once_with(job_id, tasks.sample_task, *self.args)

    def test_create_trigger_with_start_in_and_frequency(self):
        start_in = "1m"
        frequency = "1h"
        trigger = self.scheduler._create_trigger(start_in, frequency)
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
        trigger = self.scheduler._create_trigger(start_in, None)
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
        trigger = self.scheduler._create_trigger(None, frequency)
        self.assertIsInstance(trigger, IntervalTrigger)
        self.assertEqual(trigger.interval, timedelta(hours=1))

    def test_create_trigger_without_start_in_and_frequency(self):
        with self.assertRaises(ValueError):
            self.scheduler._create_trigger(None, None)

    def test_parse_time_with_valid_time_str(self):
        time_str = "30m"
        parsed_time = self.scheduler.parse_time(time_str)
        self.assertEqual(parsed_time, {"minutes": 30})

    def test_parse_time_with_invalid_time_str(self):
        time_str = "invalid"
        with self.assertRaises(
            ValueError,
            msg="Invalid time format. Use '30m' for 30 minutes, '1h' for 1 hour, etc.",
        ):
            self.scheduler.parse_time(time_str)

    def test_parse_time_with_invalid_time_unit(self):
        time_str = "1d"
        with self.assertRaises(
            ValueError, msg="Invalid time unit. Use 'm' for minutes or 'h' for hours."
        ):
            self.scheduler.parse_time(time_str)
