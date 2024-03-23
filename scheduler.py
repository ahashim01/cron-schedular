from apscheduler.schedulers.background import BackgroundScheduler
from celery import Celery
import datetime

# Initialize Celery
app = Celery("scheduler", broker="redis://redis:6379/0")


class CronScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.jobs = {}

    def add_job(self, job_id, func, interval, args=None, kwargs=None):
        if job_id in self.jobs:
            raise ValueError(f"Job ID {job_id} already exists.")

        job = self.scheduler.add_job(
            func, "interval", minutes=interval, args=args, kwargs=kwargs, id=job_id
        )
        self.jobs[job_id] = job
        return job_id

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
        app.send_task("execute", args=(job_id, func, args, kwargs))


@app.task(name="execute")
def execute_task(job_id, func, args, kwargs):
    print(f"Executing job {job_id} at {datetime.datetime.now()}")
    func(*args, **kwargs)
