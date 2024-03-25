import unittest
from scheduler.scheduler import CronScheduler
import scheduler.tasks as tasks
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

    def test_add_job_single_run(self):
        job_id = "test_job"
        self.scheduler.add_job(job_id, tasks.sample_task, start_in="1m", args=self.args)
        self.assertIn(job_id, self.scheduler.jobs)
        self.assertIsNotNone(self.scheduler.jobs[job_id])
        self.assertEqual(
            self.scheduler.job_data[job_id],
            {
                "execution_time": None,
                "error": None,
                "run_count": 0,
                "type": "Single Run",
            },
        )

    def test_add_job_periodic(self):
        job_id = "test_job_periodic"
        self.scheduler.add_job(
            job_id, tasks.sample_task, frequency="1m", args=self.args
        )
        self.assertIn(job_id, self.scheduler.jobs)
        self.assertIsNotNone(self.scheduler.jobs[job_id])
        self.assertEqual(
            self.scheduler.job_data[job_id],
            {
                "execution_time": None,
                "error": None,
                "run_count": 0,
                "type": "Periodic",
            },
        )

    def test_add_duplicate_job(self):
        job_id = "duplicate_job"
        self.scheduler.add_job(job_id, tasks.sample_task, start_in="1m", args=self.args)
        with self.assertRaisesRegex(ValueError, f"Job ID {job_id} already exists."):
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
        self.assertEqual(job_info["name"], "sample_task")
        self.assertIsNotNone(job_info["next_run_time"])
        self.assertEqual(job_info["type"], "Single Run")

    def test_add_job_with_invalid_function(self):
        job_id = "invalid_func"
        with self.assertRaisesRegex(
            TypeError, "invalid_function is not a callable function."
        ):
            self.scheduler.add_job(job_id, "invalid_function")

    def test_concurrent_jobs(self):
        job_one_id = "concurrent_job_one"
        job_two_id = "concurrent_job_two"
        self.scheduler.add_job(
            job_one_id, tasks.sample_task, start_in="1m", args=self.args
        )
        self.scheduler.add_job(
            job_two_id, tasks.sample_task, start_in="1m", args=self.args
        )
        self.assertIn(job_one_id, self.scheduler.jobs)
        self.assertIn(job_two_id, self.scheduler.jobs)
        self.assertIsNotNone(self.scheduler.jobs[job_one_id])
        self.assertIsNotNone(self.scheduler.jobs[job_two_id])

    def test_update_job_data(self):
        job_id = "update_job_data"
        self.scheduler.add_job(job_id, tasks.sample_task, start_in="1m", args=self.args)
        self.scheduler.update_job_data(job_id, "run_count", 1)
        self.assertEqual(self.scheduler.job_data[job_id]["run_count"], 1)
        self.scheduler.update_job_data(job_id, "error", "Test Error")
        self.assertEqual(self.scheduler.job_data[job_id]["error"], "Test Error")
