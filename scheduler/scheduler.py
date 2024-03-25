from apscheduler.schedulers.background import BackgroundScheduler
from scheduler.utils import configure_logger, job_wrapper, SchedulerTrigger

logger = configure_logger("main")


class CronScheduler:
    STATUS_SCHEDULED = "Scheduled"
    STATUS_RUNNING = "Running"
    STATUS_COMPLETED = "Completed"
    STATUS_FAILED = "Failed"

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.jobs = {}  # Stores APScheduler job objects
        self.job_data = {}  # Stores additional data like execution time, errors, status

    def _validate_job_id(self, job_id):
        """Helper method to validate if a job ID already exists."""
        if job_id in self.jobs:
            message = f"Job ID {job_id} already exists."
            logger.error(message)
            raise ValueError(message)

    def add_job(
        self, job_id, func, start_in=None, frequency=None, args=None, kwargs=None
    ):
        if not callable(func):
            raise TypeError(f"{func} is not a callable function.")

        self._validate_job_id(job_id)
        wrapped_func = job_wrapper(func, self, job_id)

        trigger = SchedulerTrigger().perform(start_in, frequency)
        job = self.scheduler.add_job(
            wrapped_func, trigger, args=args, kwargs=kwargs, id=job_id
        )

        self.jobs[job_id] = job
        self.job_data[job_id] = {
            "status": self.STATUS_SCHEDULED,
            "execution_time": None,
            "error": None,
            "run_count": 0,
            "type": "Periodic" if frequency else "Single Run",
        }
        logger.info(f"Job {job_id} added successfully.")

    def remove_job(self, job_id):
        if job_id not in self.jobs:
            raise KeyError(f"Job ID {job_id} not found.")
        self.scheduler.remove_job(job_id)
        del self.jobs[job_id]
        del self.job_data[job_id]
        logger.info(f"Job {job_id} removed successfully.")

    def update_job_data(self, job_id, key, value):
        if job_id in self.job_data:
            self.job_data[job_id][key] = value
        else:
            logger.error(f"Job ID {job_id} not found for data update.")

    def get_job_info(self, job_id):
        if job_id not in self.jobs:
            raise KeyError(f"Job ID {job_id} not found.")
        job = self.jobs[job_id]
        job_info = self.job_data.get(job_id, {})
        job_info.update(
            {
                "id": job.id,
                "name": job.func.__name__,
                "next_run_time": job.next_run_time,
            }
        )
        return job_info
