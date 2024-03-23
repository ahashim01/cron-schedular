import logging
import time
from functools import wraps


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
