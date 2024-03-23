from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import re
from utils import configure_logger, measure_execution_time

logger = configure_logger("main")


class CronScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.jobs = {}

    def add_job(
        self, job_id, func, start_in=None, frequency=None, args=None, kwargs=None
    ):
        if job_id in self.jobs:
            logger.error(f"Job ID {job_id} already exists.")
            raise ValueError(f"Job ID {job_id} already exists.")

        # Wrap the function with the execution time measurer
        wrapped_func = measure_execution_time(func)

        trigger = self._create_trigger(start_in, frequency)
        job = self.scheduler.add_job(
            wrapped_func, trigger, args=args, kwargs=kwargs, id=job_id
        )
        self.jobs[job_id] = job
        logger.info(f"Job {job_id} added successfully.")
        return job_id

    def _create_trigger(self, start_in, frequency):
        if start_in and frequency:
            start_time = datetime.now() + timedelta(**self.parse_time(start_in))
            return IntervalTrigger(**self.parse_time(frequency), start_date=start_time)
        elif start_in:
            start_time = datetime.now() + timedelta(**self.parse_time(start_in))
            return DateTrigger(run_date=start_time)
        elif frequency:
            return IntervalTrigger(**self.parse_time(frequency))
        else:
            logger.error("Either start_in or frequency must be provided.")
            raise ValueError("Either start_in or frequency must be provided.")

    @staticmethod
    def parse_time(time_str: str) -> dict:
        logger.debug(f"Parsing time string: {time_str}")  # Changed to DEBUG
        match = re.match(r"(\d+)([mh])", time_str)
        if not match:
            logger.error(f"Invalid time format for {time_str}")
            raise ValueError(
                "Invalid time format. Use '30m' for 30 minutes, '1h' for 1 hour, etc."
            )
        amount, unit = match.groups()
        logger.debug(
            f"Amount: {amount}, Unit: {unit} for time string {time_str}"
        )  # Changed to DEBUG
        if unit == "m":
            return {"minutes": int(amount)}
        elif unit == "h":
            return {"hours": int(amount)}
        else:
            logger.error(f"Invalid time unit for {time_str}")
            raise ValueError("Invalid time unit. Use 'm' for minutes or 'h' for hours.")

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
        return {"id": job.id, "next_run_time": job.next_run_time}
