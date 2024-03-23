from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from celery import Celery
from datetime import datetime, timedelta
import re

app = Celery("scheduler", broker="redis://redis:6379/0")


class CronScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.jobs = {}

    def add_job(
        self, job_id, func, start_in=None, frequency=None, args=None, kwargs=None
    ):
        if job_id in self.jobs:
            raise ValueError(f"Job ID {job_id} already exists.")

        trigger = self._create_trigger(start_in, frequency)
        job = self.scheduler.add_job(func, trigger, args=args, kwargs=kwargs, id=job_id)
        self.jobs[job_id] = job
        return job_id

    def _create_trigger(self, start_in, frequency):
        """Create a trigger based on the provided start_in and frequency."""
        if start_in and frequency:
            # Start after a delay and then run at regular intervals
            start_time = datetime.now() + timedelta(**self.parse_time(start_in))
            return IntervalTrigger(**self.parse_time(frequency), start_date=start_time)
        elif start_in:
            # Run once after a delay
            start_time = datetime.now() + timedelta(**self.parse_time(start_in))
            return DateTrigger(run_date=start_time)
        elif frequency:
            # Run at regular intervals
            return IntervalTrigger(**self.parse_time(frequency))
        else:
            raise ValueError("Either start_in or frequency must be provided.")

    @staticmethod
    def parse_time(time_str: str) -> dict:
        match = re.match(r"(\d+)([mh])", time_str)
        if not match:
            raise ValueError(
                "Invalid time format. Use '30m' for 30 minutes, '1h' for 1 hour, etc."
            )
        amount, unit = match.groups()
        if unit == "m":
            return {"minutes": int(amount)}
        elif unit == "h":
            return {"hours": int(amount)}
        else:
            raise ValueError("Invalid time unit. Use 'm' for minutes or 'h' for hours.")

    def remove_job(self, job_id):
        if job_id not in self.jobs:
            raise ValueError(f"Job ID {job_id} not found.")
        self.scheduler.remove_job(job_id)
        del self.jobs[job_id]

    def get_job_info(self, job_id):
        if job_id not in self.jobs:
            raise ValueError(f"Job ID {job_id} not found.")
        job = self.jobs[job_id]
        return {"id": job.id, "next_run_time": job.next_run_time}

    # Celery task wrapper
    def execute_job(self, job_id, func, *args, **kwargs):
        print(
            f"Executing job {job_id} with func {func} and args {args} and kwargs {kwargs}"
        )
        app.send_task("execute", args=(job_id, func, args, kwargs))
