from flask import render_template, request, redirect, url_for
from app import app
from scheduler import tasks
from scheduler.scheduler import CronScheduler

# Initialize the scheduler
scheduler = CronScheduler()


@app.route("/")
def index():
    # List all available tasks from tasks.py
    available_tasks = [
        name
        for name in dir(tasks)
        if callable(getattr(tasks, name)) and not name.startswith("__")
    ]
    jobs = list(scheduler.jobs.values())
    print("JOBS:", jobs)
    return render_template("index.html", available_tasks=available_tasks, jobs=jobs)


@app.route("/schedule", methods=["POST"])
def schedule():
    task_name = request.form.get("task")
    job_id = request.form.get("job_id")
    start_in = request.form.get("start_in")
    frequency = request.form.get("frequency")
    args = request.form.get("args")
    kwargs = request.form.get("kwargs")

    # Convert the args string to a list
    args_list = [arg.strip() for arg in args.split(",")] if args else []

    # Convert the kwargs string to a dictionary
    kwargs_dict = {}
    if kwargs:
        for kwarg in kwargs.split(","):
            key, value = kwarg.split("=")
            kwargs_dict[key.strip()] = value.strip()

    if task_name in dir(tasks):
        task_func = getattr(tasks, task_name)
        scheduler.add_job(
            job_id,
            task_func,
            start_in=start_in,
            frequency=frequency,
            args=args_list,
            kwargs=kwargs_dict,
        )

    return redirect(url_for("index"))


@app.route("/remove/<job_id>")
def remove(job_id):
    scheduler.remove_job(job_id)
    return redirect(url_for("index"))


@app.route("/job/<job_id>")
def job_details(job_id):
    job = scheduler.get_job_info(job_id)
    execution_time = scheduler.get_execution_time(job_id)
    if job:
        return render_template(
            "job_details.html", job=job, execution_time=execution_time
        )
    else:
        return "Job not found", 404
