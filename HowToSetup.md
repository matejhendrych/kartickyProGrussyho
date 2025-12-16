# HowToSetup

Step-by-step setup for running the RFID Attendance System locally.

## Platform Notes

- **Windows:** Use PowerShell or Command Prompt; paths use `\` and commands like `.venv\Scripts\activate`
- **Linux/macOS:** Use Bash/Zsh; paths use `/` and commands like `source .venv/bin/activate`

## 1) Clone the repository

```bash
git clone https://github.com/matejhendrych/karty.git
cd karty
```

## 2) Create a virtual environment

```bash
# Windows:
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS:
python3 -m venv .venv
source .venv/bin/activate
```

## 3) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4) Generate APP_KEY (REQUIRED)

The `APP_KEY` environment variable is **mandatory** for the application to start. It is used to sign JWT authentication tokens.

**Generate a secure random key:**

```bash
# Linux/macOS:
python3 -c 'import os; import base64; print("APP_KEY=" + base64.b64encode(os.urandom(32)).decode())'

# Windows PowerShell:
python -c "import os; import base64; print('APP_KEY=' + base64.b64encode(os.urandom(32)).decode())"
```

Copy the entire output (including the `APP_KEY=` prefix).

## 5) Create the .env file

If `.env.example` exists, copy it; otherwise, create `.env` manually:

```bash
# Linux/macOS:
cp .env.example .env

# Windows:
copy .env.example .env
```

**Edit `.env` and paste the APP_KEY value:**

```env
APP_KEY=<paste-the-generated-key-here>
APP_DEBUG=False
DATABASE_URL=sqlite:///./karty.db
MQTT_BROKER=192.168.1.110
MQTT_PORT=1883
APP_MAIL_USERNAME=
APP_MAIL_PASSWORD=
```

## 6) Configure database (optional)

**Using SQLite (default, no setup needed):**

- Database file `karty.db` is created automatically in project root.
- This is suitable for development and testing.

**Using PostgreSQL (recommended for production):**

Connect as superuser and create database/user:

```sql
CREATE DATABASE karty;
CREATE USER karty WITH PASSWORD 'karty';
GRANT ALL PRIVILEGES ON DATABASE karty TO karty;
```

Then update `.env`:

```env
DATABASE_URL=postgresql://karty:karty@localhost/karty
```

**Using MySQL:**

```sql
CREATE DATABASE karty CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'karty'@'localhost' IDENTIFIED BY 'karty';
GRANT ALL PRIVILEGES ON karty.* TO 'karty'@'localhost';
FLUSH PRIVILEGES;
```

Then update `.env`:

```env
DATABASE_URL=mysql+pymysql://karty:karty@localhost/karty?charset=utf8mb4
```

## 7) Run database migrations

```bash
alembic upgrade head
```

_Note: This is optional for SQLite but recommended for PostgreSQL/MySQL to ensure schema is up-to-date._

## 8) Start the services

Open **two separate terminal windows** (with virtual environment active in each):

### **Terminal 1: API Server**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **Terminal 2: MQTT Listener**

```bash
python -m src.mqtt_handler
```

## 9) Verify it's working

### **Option 1: Browser**

- API Docs (Swagger UI): <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- Health check: <http://localhost:8000/health>

### **Option 2: PowerShell (Windows)**

```powershell
Invoke-WebRequest http://localhost:8000/health | Select-Object -ExpandProperty Content
```

### **Option 3: curl (Linux/macOS/Git Bash)**

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{ "status": "healthy" }
```

## Troubleshooting

### APP_KEY is missing or invalid

**Error:** `ValidationError` or `Missing APP_KEY`
**Solution:** Ensure `.env` file exists and contains a valid `APP_KEY` value (generated in step 4).

### Cannot connect to MQTT broker

**Error:** MQTT listener fails to connect
**Solution:** Ensure MQTT broker is running at `MQTT_BROKER` address. If you don't have an MQTT broker, the API will still work; only MQTT features will fail.

### Database locked (SQLite)

**Error:** `sqlite3.OperationalError: database is locked`
**Solution:** Close other instances of the app or use PostgreSQL for concurrent access.

### Database connection error

**Error:** `psycopg2.OperationalError` or `pymysql.err.OperationalError`
**Solution:** Check that database server is running and `DATABASE_URL` in `.env` is correct.

### Import errors

**Error:** `ModuleNotFoundError: No module named 'src'`
**Solution:** Ensure you are in the project root directory and virtual environment is activated. Reinstall dependencies: `pip install -r requirements.txt`

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest test_fastapi.py

# Run with coverage
pytest --cov=src
```

## Optional: Docker Setup

If you prefer using Docker instead of manual setup:

```bash
# Build and start services
docker compose up --build

# Services will be available at:
# - API: http://localhost:8000
# - PostgreSQL: localhost:5432
```

The `.env` file is still required for secrets (see step 5). Create it before running `docker compose up`.

## Next Steps

Once verified:

1. Check API documentation at `/docs`
2. Create a user via `/auth/register` endpoint
3. Configure MQTT readers if needed (see [MIGRATION.md](MIGRATION.md))
4. For production deployment, see [MIGRATION.md](MIGRATION.md) for Systemd, Nginx, etc.
