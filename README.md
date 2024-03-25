# Cron-App: In-Process Cron Scheduler

## Overview

Cron-App is an in-process cron scheduler built in Python, utilizing APScheduler for scheduling and Flask for the web interface. It allows scheduling of tasks, defined as Python functions, with options for single-run or periodic execution. Each task is identified by a unique job ID and can be executed concurrently with others.

## Technical Decisions

- **APScheduler**: Chosen for robust scheduling within a Python process, providing flexibility and ease of use.
- **Flask**: Facilitates a web interface to interact with the scheduler, offering a user-friendly method to manage scheduled tasks.
- **Modular Structure**: The project is structured with `app` for web functionalities, `scheduler` for scheduling logic, and `tests` for unit testing.

## Trade-offs

1. **Python Performance**: While Python facilitates rapid development and has a vast ecosystem, it may not perform as efficiently as compiled languages under high-load conditions.

2. **Basic Web UI**: The current web interface is functional but basic, lacking advanced features and aesthetics that could improve user experience.

3. **APScheduler Limitations**: Utilizing APScheduler simplifies scheduling implementation but may restrict control over low-level job management and execution features.

4. **In-Memory Job Data**: Jobs are managed in-memory, offering speed and simplicity but lacking persistence across application restarts, which is essential for longer-running tasks.

5. **Testing Scope**: The existing tests cover fundamental functionalities but might not encompass all edge cases or complex scheduling scenarios.

## Example Usage

### Defining Tasks

First, define the tasks you want to schedule in the `schedular/tasks.py` file. These tasks should be written as Python functions. For example:

```python
# In tasks.py

def sample_task(arg1, arg2):
    print(f"Task executed with arguments: {arg1}, {arg2}")
```

### Running the Application

To start the web interface:

1. Install dependencies: `pip install -r requirements.txt`
2. Run the Flask app: `python main.py`
3. Access the web interface at `http://localhost:5000`

### Using the Web Interface for Scheduling

Once your tasks are defined, you can easily schedule, view, and manage them via the web interface:

1. **Scheduling a New Task**:

   - Navigate to `http://localhost:5000` after starting the application.
   - Select the task you want to schedule from the list of available tasks.
   - Provide the necessary scheduling parameters (job ID, start interval, frequency, etc.) and submit the form.

2. **Removing a Scheduled Task**:

   - Each scheduled task in the list has a "Remove" option.
   - Click on "Remove" next to the task you want to delete.

3. **Viewing Task Details**:
   - Click on a specific job ID in the list of scheduled tasks to view detailed information about the execution and status of that task.

### Interaction Through the UI

The Flask web interface provides a user-friendly way to manage and interact with the scheduler, allowing scheduling, removal, and inspection of tasks without directly manipulating the code.

## Tests

The project includes a suite of unit tests located in the `tests` directory. These tests validate the functionality of various components of the application, including task scheduling, job management, and the utils.

### Running the Tests

To run the tests:

1. Navigate to the project's root directory in your terminal.
2. Use the following command to run the tests with `unittest`:
   ```bash
   python -m unittest discover -s tests
   ```

## Future Improvements

1. **Persistent Storage for Jobs**: Implement a database or file-based system to store scheduled jobs persistently.
2. **Advanced Job Management**: Introduce features like job dependencies, error retries, and pausing/resuming jobs.
3. **Scalability and Load Balancing**: Optimize for handling a higher volume of jobs and distribute the load across multiple servers or processes.
4. **Enhanced Security Measures**: Implement security features for the web interface, including authentication and authorization.
5. **Comprehensive Logging and Monitoring**: Develop a more elaborate logging system for detailed monitoring and debugging.
6. **User Interface Improvements**: Revamp the web interface with a modern, intuitive design, real-time updates and communicate the errors better.
7. **API Endpoints for Remote Management**: Create RESTful API endpoints for programmatic management of jobs.
8. **Improved Test Coverage**: Expand the test suite to cover more edge cases and complex scenarios.
9. **Dockerization**: Plan to containerize the application with Docker to streamline deployment and ensure environment consistency. Dockerization will aid in achieving seamless deployment across various platforms and ease the development process.
