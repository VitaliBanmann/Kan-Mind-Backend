# KanMind Backend

## About the project

KanMind is a task and project management application developed with Django REST
Framework. This repository contains the API for user authentication, boards,
tasks, and comments.

## Technologies

- Python 3
- Django 6.1
- Django REST Framework 3.18.0
- Token authentication
- SQLite
- Coverage.py
- pycodestyle

## Features

### Authentication

- User registration and login
- Token-based authentication
- Email address lookup

### Boards

- Create, list, view, update, and delete boards
- Manage board members and owners
- Board task statistics

### Tasks and comments

- Create, retrieve, update, and delete tasks and comments
- Assign tasks and reviewers
- Filter tasks assigned to or reviewed by the current user
- Validate board membership and permissions
- Assign authenticated users as comment authors

## Requirements

- Python 3.x
- Git

Install the dependencies listed in `requirements.txt`.

## Local setup

1. Create a virtual environment:

       python -m venv .venv

2. Activate the environment:

   **Windows**

       .venv\Scripts\activate

   **macOS/Linux**

       source .venv/bin/activate

3. Install dependencies:

       pip install -r requirements.txt

4. Create a `.env` file beside `manage.py` and set a local Django secret:

       DJANGO_SECRET_KEY=your-secret-key-here

   `.env` is ignored by Git; never commit secrets. The SQLite database is
   created at `db.sqlite3` in this backend directory. This database file is
   also ignored by Git.

5. Create or synchronize local database tables:

       python manage.py migrate --run-syncdb

6. Start the development server:

       python manage.py runserver

The API is normally available at `http://127.0.0.1:8000/`. The project apps
have no migration files; Django's built-in apps continue to use Django's
provided migrations.

## Frontend

The frontend is maintained separately at
`https://github.com/VitaliBanmann/Kan-Mind-Frontend`. Its API configuration
defaults to this backend at `http://127.0.0.1:8000/api/`.

## Tests and coverage

Run the complete test suite:

    python manage.py test

The test suite currently contains 121 tests.

Run the tests with coverage and check the 95% threshold:

    coverage run --source=auth_app,board_app,task_app,core --omit="*/tests/*,*/migrations/*" manage.py test
    coverage report --show-missing --fail-under=95

## API overview

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/registration/` | Register a new user |
| POST | `/api/login/` | Authenticate a user |
| GET | `/api/email-check/` | Check whether an email is registered |
| GET, POST | `/api/boards/` | List or create boards |
| GET, PATCH, DELETE | `/api/boards/<board_id>/` | Retrieve, update, or delete a board |
| GET | `/api/tasks/assigned-to-me/` | List tasks assigned to the current user |
| GET | `/api/tasks/reviewing/` | List tasks reviewed by the current user |
| POST | `/api/tasks/` | Create a task |
| GET, PATCH, DELETE | `/api/tasks/<task_id>/` | Retrieve, update, or delete a task |
| GET, POST | `/api/tasks/<task_id>/comments/` | List or create task comments |
| DELETE | `/api/tasks/<task_id>/comments/<comment_id>/` | Delete a task comment |

Protected endpoints require token authentication.

## Development commands

Check the Django project:

    python manage.py check

Run the tests:

    python manage.py test

Create five sample tasks for an existing user in a local development database:

    python manage.py seed_sample_tasks --email user@example.com --board-title "KanMind Sample Board"

This optional command creates a board if needed. Do not run it against
production data.

## Deployment note

SQLite is intended for local development. Hosted SQLite data can be lost if
the host uses an ephemeral filesystem. Use persistent storage before relying
on a hosted SQLite database.

For hosting, configure persistent storage appropriate to that environment,
then set `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`,
`DJANGO_CORS_ALLOWED_ORIGINS`, and `DJANGO_CSRF_TRUSTED_ORIGINS` there. Local
development uses SQLite and does not require a database URL.

## License

This project was developed as part of the Developer Akademie Backend course.
