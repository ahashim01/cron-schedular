# Cron Scheduler Application

## Description

This cron scheduler is an in-process tool designed to schedule and execute jobs periodically. It allows clients to specify job intervals, frequencies, and unique identifiers for each job. Built in Python, it leverages the `apscheduler` library to manage job scheduling efficiently.

## Technical Decisions

1. **Python**: Chosen for its simplicity and readability, and extensive library support.
2. **APScheduler**: Utilized for its robust scheduling capabilities.
3. **Logging and Execution Time Measurement**: Implemented for effective monitoring and debugging.

## Trade-offs

- Simplicity over Complexity: Opted for a straightforward implementation to ensure ease of understanding and maintenance.
- Python's GIL (Global Interpreter Lock) limits the concurrency, which could affect performance under high load.

## Example Usage

```python
from scheduler import CronScheduler
import tasks
from utils import configure_logger

def main():
    scheduler = CronScheduler()

    scheduler.add_job(
        "single_run",
        tasks.sample_task,
        start_in="1m",
        args=["Hello World! once after 1 minute"],
    )

    scheduler.add_job(
        "regular_frequency",
        tasks.sample_task,
        frequency="1m",
        args=["Hello World! every minute"],
    )

    # Keep the script running to let the scheduler operate
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.scheduler.shutdown()

if __name__ == "__main__":
    main()
```

## Future Improvements

1. Enhance task variety in `tasks.py`.
2. More robust error handling and exception management.
3. Comprehensive documentation and testing for reliability.
4. Additional customization options for logging and scheduler settings.
