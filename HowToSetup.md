# HowToSetup

Step-by-step setup for running the RFID Attendance System locally.

## 1) Prerequisites

- Python 3.12 or newer
- PostgreSQL 14+ (or MySQL 8+) running locally
- MQTT broker (for example Mosquitto)
- Git

## 2) Clone the repository

```bash
git clone https://github.com/matejhendrych/karty.git
cd karty
```

## 3) Create a virtual environment

```bash
python -m venv venv
```

Activate it:

- Windows: `venv\Scripts\activate`
- Linux/macOS: `source venv/bin/activate`

## 4) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 5) Configure the database (PostgreSQL example)

Connect as a superuser and create the database and user:

```sql
CREATE DATABASE karty;
CREATE USER karty WITH PASSWORD 'karty';
GRANT ALL PRIVILEGES ON DATABASE karty TO karty;
```

Adjust names and passwords as needed. For MySQL, create a database and user with matching privileges.

## 6) Create the .env file

If an `.env.example` file is present, copy it and edit values. Otherwise create `.env` with at least:

```env
APP_KEY=replace-with-generated-secret
APP_DEBUG=False
DATABASE_URL=postgresql+psycopg2://karty:karty@localhost/karty
MQTT_BROKER=192.168.1.110
MQTT_PORT=1883
APP_MAIL_USERNAME=
APP_MAIL_PASSWORD=
```

Generate a strong secret key:

```bash
python - <<"PY"
import base64, os
print("APP_KEY=" + base64.b64encode(os.urandom(32)).decode())
PY
```

On Windows PowerShell you can run the same block; it will emit the line to paste into `.env`.

## 7) Run database migrations

```bash
alembic upgrade head
```

## 8) Start the services

Use two terminals (with the virtual environment active):

Terminal 1: API server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2: MQTT listener

```bash
python -m src.mqtt_handler
```

## 9) Verify

- Open <http://localhost:8000/health> to check service health.
- Open <http://localhost:8000/docs> for interactive API documentation.

## Optional: Docker

```bash
docker build -t karty-api .
docker run -d -p 8000:8000 --env-file .env karty-api
```

## Troubleshooting

- Database connection errors: confirm the DSN in `DATABASE_URL`, database is running, and user has privileges.
- MQTT connectivity: verify broker host/port and that topics match device configuration (for example `device/+/ctecka/request`).
- Import errors: ensure the virtual environment is activated and dependencies are installed.
