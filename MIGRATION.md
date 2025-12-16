# Migration Guide: Flask to FastAPI + PostgreSQL

This guide covers the migration from Flask (Python 2) to FastAPI (Python 3.12+) with PostgreSQL support for the RFID Attendance System.

## Overview

The system has been modernized with the following changes:
- **Python 2.7** → **Python 3.12+**
- **Flask** → **FastAPI**
- **SQLite/MySQL** → **PostgreSQL** (with MySQL support maintained)
- **Flask-Login** → **JWT Authentication**
- **Flask-WTF Forms** → **Pydantic Models**
- All dependencies updated to latest versions
- Type hints added throughout the codebase

## Prerequisites

- Python 3.12 or higher
- PostgreSQL 14+ (recommended) or MySQL 8+
- pip and virtualenv
- MQTT broker (for card reader communication)

## Installation Steps

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

#### Option A: PostgreSQL (Recommended)

Install PostgreSQL:
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
```

Create database and user:
```bash
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE karty;
CREATE USER karty WITH PASSWORD 'karty';
GRANT ALL PRIVILEGES ON DATABASE karty TO karty;
\q
```

#### Option B: MySQL (Supported)

Install MySQL:
```bash
# Ubuntu/Debian
sudo apt-get install mysql-server

# macOS
brew install mysql
```

Create database and user:
```bash
mysql -u root -p

# In MySQL shell:
CREATE DATABASE karty CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'karty'@'localhost' IDENTIFIED BY 'karty';
GRANT ALL PRIVILEGES ON karty.* TO 'karty'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
# Application
APP_KEY=your-secret-key-here-change-this-in-production
APP_DEBUG=False

# Database - Choose one:
# PostgreSQL
DATABASE_URL=postgresql://karty:karty@localhost/karty

# OR MySQL
# DATABASE_URL=mysql+pymysql://karty:karty@localhost/karty?charset=utf8mb4

# MQTT Broker
MQTT_BROKER=192.168.1.110
MQTT_PORT=1883

# Email (optional)
APP_MAIL_USERNAME=your-email@gmail.com
APP_MAIL_PASSWORD=your-app-password
APP_MAIL_INFO_ACCOUNT=your-email@gmail.com
```

Generate a secure secret key:
```bash
python3 -c 'import os; import base64; print("APP_KEY=" + base64.b64encode(os.urandom(32)).decode())'
```

### 5. Database Migration from SQLite

If migrating from existing SQLite database:

```bash
# Use the migration script:
python3 scripts/migrate_db.py --from sqlite:///dev.db --to postgresql://karty:karty@localhost/karty
```

Alternatively, export and import manually using standard tools (pg_dump, MySQL dumps, etc.).

### 6. Run Database Migrations

```bash
# Initialize Alembic (if needed)
alembic upgrade head
```

### 7. Start the Application

#### Development Mode

```bash
# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start MQTT listener
python3 -m src.mqtt_handler
```

#### Production Mode

```bash
# Using Gunicorn with Uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Start MQTT listener as a service (systemd example below)
```

## Key Changes

### 1. Authentication

**Old (Flask-Login):**
```python
from flask_login import login_user, logout_user, current_user

@login_required
def protected_route():
    return f"Hello {current_user.username}"
```

**New (JWT):**
```python
from fastapi import Depends
from src.auth_utils import get_current_user

@router.get("/protected")
async def protected_route(current_user = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}"}
```

To get a token:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=pass"
```

Use the token:
```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 2. API Endpoints

All endpoints are now RESTful JSON APIs. The main endpoint changes:

| Old Flask Route | New FastAPI Route | Method |
|----------------|-------------------|---------|
| `/login` | `/auth/login` | POST |
| `/register` | `/auth/register` | POST |
| `/logout` | (Token expiration) | - |
| `/user/<id>` | `/auth/users/{id}` | GET |
| `/services/health` | `/services/health` | GET |

### 3. Database Models

Models remain mostly the same but with updated SQLAlchemy 2.0 syntax:

```python
# Old
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# New
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
```

### 4. MQTT Integration

MQTT handler updated but functionality remains the same:
- Subscribes to card reader topics
- Validates user access based on groups and time restrictions
- Logs all access attempts
- Publishes access grants/denials

Run MQTT listener:
```bash
python3 -m src.mqtt_handler
```

### 5. Forms to Pydantic Models

**Old (WTForms):**
```python
class LoginForm(Form):
    username = StringField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
```

**New (Pydantic):**
```python
class LoginRequest(BaseModel):
    username: str
    password: str
```

## Production Deployment

### Systemd Service for FastAPI

Create `/etc/systemd/system/karty-api.service`:

```ini
[Unit]
Description=RFID Attendance System API
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/karty
Environment="PATH=/opt/karty/venv/bin"
ExecStart=/opt/karty/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Systemd Service for MQTT Listener

Create `/etc/systemd/system/karty-mqtt.service`:

```ini
[Unit]
Description=RFID Attendance System MQTT Listener
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/karty
Environment="PATH=/opt/karty/venv/bin"
ExecStart=/opt/karty/venv/bin/python3 -m src.mqtt_handler
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable karty-api karty-mqtt
sudo systemctl start karty-api karty-mqtt
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/karty/src/static;
    }
}
```

## Testing

Run tests:
```bash
pytest
```

Test API endpoints:
```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"test123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=test123"
```

## Troubleshooting

### Database Connection Issues

Check PostgreSQL is running:
```bash
sudo systemctl status postgresql
```

Test connection:
```bash
psql -U karty -d karty -h localhost
```

### MQTT Connection Issues

Check MQTT broker is accessible:
```bash
mosquitto_sub -h 192.168.1.110 -p 1883 -t '#' -v
```

### Import Errors

Ensure virtual environment is activated and all dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements-new.txt
```

## Rollback Plan

If issues occur, you can rollback to the Flask version:
1. Restore the old database backup
2. Switch to the original branch
3. Use the old `requirements.txt`
4. Restart with `./manage.py runserver`

## Support

For issues or questions:
- Check the logs: `/var/log/karty/`
- Review the API docs: `http://localhost:8000/docs`
- Check MQTT logs for reader communication issues

## Breaking Changes

1. **Sessions removed**: Use JWT tokens instead
2. **URL structure changed**: All API routes now use RESTful conventions
3. **Form submissions**: Now expect JSON payloads
4. **Template rendering**: Limited support, primarily API-focused
5. **Email templates**: Updated for async operation

## Preserved Functionality

✅ User authentication and management
✅ RFID card reader MQTT communication  
✅ Access control based on groups and time restrictions
✅ Monthly attendance reports
✅ User and group management
✅ Card access logging
✅ Email notifications
