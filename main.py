from scheduler import CronScheduler
import tasks
from utils import configure_logger

logger = configure_logger("main")


def main():
    # Initialize the scheduler
    scheduler = CronScheduler()

    # Add a sample job
    job_one_id = scheduler.add_job(
        "single_run",
        tasks.sample_task,
        start_in="1m",
        args=["Hello World! once after 1 minute"],
    )

    job_two_id = scheduler.add_job(
        "regular_frequency",
        tasks.sample_task,
        frequency="1m",
        args=["Hello World! every minute"],
    )

    job_three_id = scheduler.add_job(
        "delayed_start_with_frequency",
        tasks.sample_task,
        start_in="2m",
        frequency="1m",
        args=["Hello World! starting in 2 minutes and then every minute"],
    )

    job_one_info = scheduler.get_job_info(job_one_id)
    job_two_info = scheduler.get_job_info(job_two_id)
    job_three_info = scheduler.get_job_info(job_three_id)
    logger.info(f"Job info: {job_one_info}")
    logger.info(f"Job info: {job_two_info}")
    logger.info(f"Job info: {job_three_info}")

    # Keeping the script running to let the scheduler operate
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down the scheduler.")
        scheduler.scheduler.shutdown()


if __name__ == "__main__":
    main()
