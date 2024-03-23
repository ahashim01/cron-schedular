import unittest
from unittest.mock import patch, Mock
from scheduler import CronScheduler
import tasks


class TestCronScheduler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.interval = 1
        cls.args = ["test"]

    def setUp(self):
        self.scheduler = CronScheduler()

    def test_add_job(self):
        job_id = "test_job"
        self.scheduler.add_job(job_id, tasks.sample_task, self.interval, self.args)
        self.assertIn(job_id, self.scheduler.jobs)
        self.assertIsNotNone(self.scheduler.jobs[job_id])

    def test_add_duplicate_job(self):
        job_id = "duplicate_job"
        self.scheduler.add_job(job_id, tasks.sample_task, self.interval, self.args)
        with self.assertRaises(ValueError):
            self.scheduler.add_job(job_id, tasks.sample_task, self.interval, self.args)

    def test_remove_job(self):
        job_id = "remove_job"
        self.scheduler.add_job(job_id, tasks.sample_task, self.interval, self.args)
        self.scheduler.remove_job(job_id)
        self.assertNotIn(job_id, self.scheduler.jobs)

    @patch("scheduler.CronScheduler.execute_job")
    def test_job_execution(self, mock_execute_job):
        job_id = "execute_job"
        self.scheduler.add_job(job_id, tasks.sample_task, self.interval, self.args)
        self.scheduler.execute_job(job_id, tasks.sample_task, self.args)
        mock_execute_job.assert_called_once()
        mock_execute_job.assert_called_with(job_id, tasks.sample_task, self.args)
