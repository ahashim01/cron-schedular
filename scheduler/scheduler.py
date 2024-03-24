from functools import wraps
import time
from apscheduler.schedulers.background import BackgroundScheduler
from utils import configure_logger, job_wrapper, SchedulerTrigger

logger = configure_logger("main")


class CronScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.create_trigger = SchedulerTrigger()
        self.scheduler.start()
        self.jobs = {}
        self.execution_times = {}

    def add_job(
        self, job_id, func, start_in=None, frequency=None, args=None, kwargs=None
    ):
        # Check if the function is callable
        if not callable(func):
            logger.error(f"{func} is not a function.")
            raise ValueError(f"{func} is not a function.")

        if job_id in self.jobs:
            logger.error(f"Job ID {job_id} already exists.")
            raise ValueError(f"Job ID {job_id} already exists.")

        wrapped_func = job_wrapper(func, self, job_id)

        trigger = self.create_trigger.perform(start_in, frequency)
        job = self.scheduler.add_job(
            wrapped_func, trigger, args=args, kwargs=kwargs, id=job_id
        )
        self.jobs[job_id] = job
        logger.info(f"Job {job_id} added successfully.")
        return job_id

    def remove_job(self, job_id):
        if job_id not in self.jobs:
            logger.error(f"Job ID {job_id} not found.")
            raise ValueError(f"Job ID {job_id} not found.")
        self.scheduler.remove_job(job_id)
        del self.jobs[job_id]
        logger.info(f"Job {job_id} removed successfully.")

    def get_job_info(self, job_id):
        if job_id not in self.jobs:
            logger.error(f"Job ID {job_id} not found.")
            raise ValueError(f"Job ID {job_id} not found.")
        job = self.jobs[job_id]
        logger.info(f"Job {job_id} info retrieved successfully.")
        return {"id": job.id, "name": job.name, "next_run_time": job.next_run_time}

    def get_execution_time(self, job_id):
        return self.execution_times.get(job_id)
