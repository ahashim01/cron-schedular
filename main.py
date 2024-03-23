from scheduler import CronScheduler
import tasks


def main():
    # Initialize the scheduler
    scheduler = CronScheduler()

    # Add a sample job
    job_id = scheduler.add_job(
        "job1", tasks.sample_task, interval=1, args=["Hello, world!"]
    )

    # Print the job info
    job_info = scheduler.get_job_info(job_id)
    print(f"Job info: {job_info}")

    # Keeping the script running to let the scheduler operate
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down the scheduler.")
        scheduler.scheduler.shutdown()


if __name__ == "__main__":
    main()
