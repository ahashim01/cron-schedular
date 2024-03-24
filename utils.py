import logging
import time
from functools import wraps
import re
from datetime import datetime, timedelta
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger


def configure_logger(logger_name):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - [%(levelname)s] - [%(funcName)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(logger_name)
    return logger


def measure_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger = logging.getLogger("main")
        logger.info(
            f"Execution time of {func.__name__}: {((end_time - start_time)* 1000):.4f} ms"
        )
        return result

    return wrapper


def job_wrapper(func, scheduler, job_id):
    logger = logging.getLogger("main")

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            scheduler.update_job_data(job_id, "status", scheduler.STATUS_RUNNING)
            start_time = time.time()

            result = func(*args, **kwargs)

            end_time = time.time()
            execution_time = f"{((end_time - start_time) * 1000):.4f} ms"

            scheduler.update_job_data(
                job_id, "run_count", scheduler.job_data[job_id]["run_count"] + 1
            )
            scheduler.update_job_data(job_id, "execution_time", execution_time)
            if scheduler.job_data[job_id]["type"] == "Single Run":
                scheduler.update_job_data(job_id, "status", scheduler.STATUS_COMPLETED)
            else:
                scheduler.update_job_data(job_id, "status", scheduler.STATUS_SCHEDULED)

            logger.info(
                f"Job {job_id} (Function: {func.__name__}) execution time: {execution_time} seconds"
            )
            return result

        except Exception as e:
            error_info = f"{type(e).__name__}: {e}"
            scheduler.update_job_data(job_id, "error", error_info)
            scheduler.update_job_data(job_id, "status", scheduler.STATUS_FAILED)

            logger.error(f"Error in job {job_id}: {error_info}")

    return wrapper


class SchedulerTrigger:
    def __init__(self):
        self.logger = configure_logger("main")

    def _create_interval_trigger(self, start_in=None, frequency=None):
        start_time = (
            datetime.now() + timedelta(**self._parse_time(start_in))
            if start_in
            else None
        )
        return IntervalTrigger(**self._parse_time(frequency), start_date=start_time)

    def _create_date_trigger(self, start_in):
        start_time = datetime.now() + timedelta(**self._parse_time(start_in))
        return DateTrigger(run_date=start_time)

    def _parse_time(self, time_str: str) -> dict:
        # Regular expression to match the time format
        match = re.match(r"(\d+)([smh])$", time_str)
        if not match:
            raise ValueError(
                "Invalid time format. Expected format like '30s', '20m', or '1h'."
            )

        amount, unit = match.groups()
        amount = int(amount)

        time_unit_map = {"s": "seconds", "m": "minutes", "h": "hours"}

        if unit in time_unit_map:
            return {time_unit_map[unit]: amount}

        raise ValueError("Invalid time unit. Expected 's', 'm', or 'h'.")

    def perform(self, start_in=None, frequency=None):
        if start_in and frequency:
            return self._create_interval_trigger(start_in, frequency)
        elif start_in:
            return self._create_date_trigger(start_in)
        elif frequency:
            return self._create_interval_trigger(frequency=frequency)
        else:
            self.logger.error("Either start_in or frequency must be provided.")
            raise ValueError("Either start_in or frequency must be provided.")
