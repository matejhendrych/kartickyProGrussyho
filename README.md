# RFID Attendance System (FastAPI)

Modern RFID-based attendance tracking system built with FastAPI, PostgreSQL, and MQTT for card reader communication. Originally bootstrapped from a Flask skeleton, now fully upgraded to Python 3 and FastAPI.

## Features

- JWT authentication and user/group management
- Time-based access control and reader-to-group bindings
- Real-time RFID validation over MQTT with full logging
- Automated monthly attendance reports
- PostgreSQL first (MySQL supported) via SQLAlchemy 2.0
- API-first design with automatic OpenAPI documentation

## Tech Stack

- FastAPI + Uvicorn
- SQLAlchemy 2.0, Alembic
- PostgreSQL (preferred) or MySQL
- Pydantic models and schemas
- Paho MQTT client
- Pytest, pylint, mypy

## Quick Links

- Setup guide: [HowToSetup.md](HowToSetup.md)
- Migration guide and systemd/Docker notes: [MIGRATION.md](MIGRATION.md)

## Quick Start

```bash
python -m venv venv
venv\Scripts\activate  # Windows; on Linux/macOS use source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env  # then edit values
alembic upgrade head
uvicorn main:app --reload --host 0.0.0.0 --port 8000
python -m src.mqtt_handler  # second terminal
```

Full walkthrough (DB creation, secrets, tips) is in [HowToSetup.md](HowToSetup.md).

## Installation (expanded)

1. Clone: `git clone https://github.com/matejhendrych/karty.git && cd karty`
2. Create and activate venv (see above).
3. Install deps: `pip install -r requirements.txt`.
4. Database (PostgreSQL example): create database/user and grant privileges.
5. Configure `.env` (copy from `.env.example` if present) and generate `APP_KEY`.
6. Run migrations: `alembic upgrade head`.
7. Start services: `uvicorn main:app --reload ...` and `python -m src.mqtt_handler`.
8. Open <http://localhost:8000/docs> for interactive API docs.

## API Overview

- `GET /` API info
- `GET /health` health check
- `POST /auth/register` register user
- `POST /auth/login` login and receive JWT
- `GET /auth/me` read current user
- `PUT /auth/me` update current user
- `GET /auth/users` list users
- `GET /auth/users/{id}` fetch user by id
  See live documentation at `/docs` or `/redoc` when the server is running.

## MQTT Integration

1. Readers publish card numbers to configured topics (for example `device/+/ctecka/request`).
2. Server validates against user-group bindings, schedules, and reader associations.
3. Access grant or deny is published back; all attempts are logged.

## Database Migration

- Legacy migration helper: `python scripts/migrate_db.py --from sqlite:///dev.db --to postgresql://karty:karty@localhost/karty --verbose`
- More details in [MIGRATION.md](MIGRATION.md).

## Development

- Run API: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- MQTT listener: `python -m src.mqtt_handler`
- Tests: `pytest`
- Type check: `mypy src/`
- Lint: `pylint src/`
- Migrations: `alembic revision --autogenerate -m "message"` then `alembic upgrade head`

## Deployment

- Gunicorn: `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --access-logfile - --error-logfile -`
- Docker: `docker build -t karty-api . && docker run -d -p 8000:8000 --env-file .env karty-api`
- Systemd examples in [MIGRATION.md](MIGRATION.md).

## Configuration (.env)

| Variable          | Description               | Default       |
| ----------------- | ------------------------- | ------------- |
| APP_KEY           | Secret key for JWT tokens | required      |
| APP_DEBUG         | Enable debug mode         | False         |
| DATABASE_URL      | Database connection URL   | required      |
| MQTT_BROKER       | MQTT broker host          | 192.168.1.110 |
| MQTT_PORT         | MQTT broker port          | 1883          |
| APP_MAIL_USERNAME | SMTP username (optional)  | -             |
| APP_MAIL_PASSWORD | SMTP password (optional)  | -             |

## Project Structure

```text
karty/
├── main.py                 # FastAPI application entry point
├── src/
│   ├── routers/           # API route handlers
│   ├── data/              # Database models and utilities
│   ├── config.py          # Application configuration
│   ├── database.py        # Database connection setup
│   ├── schemas.py         # Pydantic schemas
│   ├── auth_utils.py      # Authentication utilities
│   └── mqtt_handler.py    # MQTT communication
├── scripts/               # Helper scripts (migrate_db, etc.)
├── migrations/            # Alembic migrations
├── tests/                 # Test suite
├── requirements.txt       # Python dependencies
└── MIGRATION.md           # Migration and deployment notes
```

## Troubleshooting

- Database: verify `DATABASE_URL`, database service is running, and user privileges are set.
- MQTT: check broker host/port and subscribed topics match device configuration.
- Imports: ensure the virtual environment is active and dependencies are installed.

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Commit and push changes.
4. Open a Pull Request.

## Changelog

- 2.0.0 (2024): Migrated to FastAPI, Python 3.12+, JWT auth, PostgreSQL-first, improved MQTT.
- 1.0.0: Initial Flask-based implementation.

## License

MIT License.

## Support

Open an issue or consult [MIGRATION.md](MIGRATION.md) and the `/docs` endpoint when the server is running.
