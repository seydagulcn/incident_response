# Incident Response Tracker

A web application built with Flask for tracking and managing cybersecurity incidents.

## What it does

This app lets security analysts log and manage security incidents. Each incident includes details like type, severity, status, and timestamps. The app also automatically calculates MTTD, MTTR and MTBF metrics, and keeps an activity log for every incident.

## Features

- Register, login and logout
- Add, edit, delete and view incidents
- Search incidents by title
- Filter incidents by status and severity
- Automatic MTTD, MTTR and MTBF calculations
- Activity log that tracks all changes to each incident

## How to run

1. Clone the repo
2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```
3. Install Flask:
```bash
pip install flask
```
4. Run the app:
```bash
python3 app.py
```
5. Go to http://127.0.0.1:5000 in your browser

## Running tests

```bash
python3 -m pytest test_logic.py -v
```

## Test Results

![Test Results](test_results.png)

## Database

Uses SQLite with 3 tables:
- `users` — stores registered users
- `incidents` — stores incident records linked to users
- `activity_log` — stores change history for each incident