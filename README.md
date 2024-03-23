# Python Cron Scheduler

### Project Overview

This project implements a simple yet powerful in-process cron scheduler in Python. Utilizing Celery for task queuing and APScheduler for job scheduling, this scheduler is designed to execute multiple jobs concurrently, following specified intervals.

### Setup and Installation

#### Prerequisites

- Docker
- Docker Compose

### Running the Application

1. Clone the repository:

```bash
git clone git@github.com:ahashim01/cron-schedular.git
```

2. Navigate to the project directory:

```bash
cd cron-schedular
```

3. Build and run the Docker container:

```bash
docker compose up --build
```

**_The application and Redis will start in Docker containers._**

### Usage

#### To schedule a new job:

1. Define your task in tasks.py.
2. In main.py, use the CronScheduler to add your job with a unique job ID, the task function, and the scheduling interval.
3. Run the application as described in the setup section.

**_Example:_**

```python
# In main.py
scheduler.add_job("job1", tasks.sample_task, interval=1, args=["Hello, world!"])
```

#### To remove a job:

1. In main.py, use the CronScheduler to remove the job by its unique job ID.
2. Run the application as described in the setup section.

**_Example:_**

```python
# In main.py
scheduler.remove_job("job1")
```

### Testing

Run the tests to ensure everything is working as expected:

```bash
docker compose run web python -m unittest tests/test*.py
```

### Technical Decisions

- **Python**: Chosen for its simplicity and robust libraries for task scheduling and concurrency.
- **Celery**: Used for managing asynchronous task queues.
- **Redis**: Used as the message broker for Celery.
- **APScheduler**: Integrated for handling the scheduling of jobs.
- **Docker**: Ensures a consistent environment, avoiding the "it works on my machine" problem.

### Trade-offs

- Using Docker adds a layer of complexity for deployment but offers benefits in consistency and scalability.
- Celery, while powerful, might introduce some overhead for smaller applications.

### Possible Future Improvements

- Enhanced error handling and retry mechanisms.
- Support for more complex scheduling scenarios.
- Scaling the application for high availability and distributed processing.
- Adding a RESTful API for job management.
