# RFID Attendance System (FastAPI)

Modern RFID-based attendance tracking system built with FastAPI, PostgreSQL, and MQTT for card reader communication.

## Features

- 🔐 **JWT Authentication** - Secure token-based authentication
- 📊 **User Management** - Complete user and group administration
- 🎫 **RFID Card Integration** - Real-time card reader communication via MQTT
- ⏰ **Time-based Access Control** - Configurable access schedules by group
- 📅 **Monthly Reports** - Automated attendance reporting
- 🗄️ **PostgreSQL Support** - Modern, scalable database backend
- 🔄 **RESTful API** - Clean, documented API endpoints
- 🐍 **Python 3.12+** - Modern Python with type hints

## Tech Stack

- **FastAPI** - Modern web framework with automatic API documentation
- **SQLAlchemy 2.0** - Advanced ORM with type safety
- **PostgreSQL** - Primary database (MySQL also supported)
- **Paho MQTT** - MQTT client for card reader communication
- **Pydantic** - Data validation using Python type annotations
- **JWT** - Secure authentication tokens
- **Alembic** - Database migrations

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 14+ or MySQL 8+
- MQTT broker (for card readers)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/matejhendrych/karty.git
cd karty
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up database**

For PostgreSQL:
```bash
sudo -u postgres psql
CREATE DATABASE karty;
CREATE USER karty WITH PASSWORD 'karty';
GRANT ALL PRIVILEGES ON DATABASE karty TO karty;
\q
```

5. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

Generate a secret key:
```bash
python3 -c 'import os; import base64; print("APP_KEY=" + base64.b64encode(os.urandom(32)).decode())'
```

6. **Run migrations**
```bash
alembic upgrade head
```

7. **Start the application**

Development mode:
```bash
# Terminal 1: API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: MQTT listener
python3 -m src.mqtt_handler
```

8. **Access the application**
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Documentation

### Authentication

**Register a new user:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "securepassword",
    "name": "John",
    "second_name": "Doe"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&password=securepassword"
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Access protected endpoints:**
```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Main Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get token
- `GET /auth/me` - Get current user info
- `PUT /auth/me` - Update current user
- `GET /auth/users` - List all users
- `GET /auth/users/{id}` - Get user by ID

For complete API documentation, visit `/docs` when the server is running.

## MQTT Integration

The system communicates with RFID card readers via MQTT:

1. Card readers publish card numbers to specific topics
2. System validates user access based on:
   - User membership in groups
   - Group access times
   - Day of week restrictions
   - Card reader associations
3. System publishes access grant/deny to reader
4. All access attempts are logged

### MQTT Topics

- Subscribe: `device/+/ctecka/request` or `#` (all topics)
- Publish: Configured per reader in database

## Database Migration

To migrate from the old Flask/SQLite system:

```bash
python3 scripts/migrate_db.py \
  --from sqlite:///dev.db \
  --to postgresql://karty:karty@localhost/karty \
  --verbose
```

See [MIGRATION.md](MIGRATION.md) for detailed migration instructions.

## Development

### Running Tests

```bash
pytest
```

### Type Checking

```bash
mypy src/
```

### Linting

```bash
pylint src/
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

## Production Deployment

### Using Gunicorn

```bash
gunicorn main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Using Docker

```bash
docker build -t karty-api .
docker run -d -p 8000:8000 --env-file .env karty-api
```

### Systemd Services

See [MIGRATION.md](MIGRATION.md) for systemd service configurations.

## Configuration

All configuration is done via environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_KEY` | Secret key for JWT tokens | Required |
| `APP_DEBUG` | Enable debug mode | `False` |
| `DATABASE_URL` | Database connection URL | Required |
| `MQTT_BROKER` | MQTT broker host | `192.168.1.110` |
| `MQTT_PORT` | MQTT broker port | `1883` |
| `APP_MAIL_USERNAME` | Email username (optional) | - |
| `APP_MAIL_PASSWORD` | Email password (optional) | - |

## Project Structure

```
karty/
├── main.py                 # FastAPI application entry point
├── src/
│   ├── routers/           # API route handlers
│   │   ├── auth.py        # Authentication endpoints
│   │   ├── public.py      # Public endpoints
│   │   └── services.py    # Service endpoints
│   ├── data/              # Database models and utilities
│   │   └── models/        # SQLAlchemy models
│   ├── config.py          # Application configuration
│   ├── database.py        # Database connection
│   ├── schemas.py         # Pydantic schemas
│   ├── auth_utils.py      # Authentication utilities
│   └── mqtt_handler.py    # MQTT communication
├── scripts/               # Utility scripts
│   └── migrate_db.py      # Database migration
├── migrations/            # Alembic migrations
├── tests/                 # Test suite
├── requirements.txt       # Python dependencies
├── MIGRATION.md          # Migration guide
└── .env.example          # Environment variables template
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

### MQTT Issues

Test MQTT broker connection:
```bash
mosquitto_sub -h 192.168.1.110 -p 1883 -t '#' -v
```

### Import Errors

Ensure virtual environment is activated:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the [MIGRATION.md](MIGRATION.md) guide
- Review API documentation at `/docs`

## Changelog

### Version 2.0.0 (2024)
- ✨ Migrated from Flask to FastAPI
- ✨ Python 3.12+ support with type hints
- ✨ PostgreSQL as primary database
- ✨ JWT-based authentication
- ✨ RESTful API design
- ✨ Automatic API documentation
- ✨ Improved MQTT integration
- ✨ Modern async/await patterns
- ✨ Enhanced security and performance

### Version 1.0.0
- Initial Flask-based implementation
- SQLite/MySQL support
- Basic RFID attendance tracking
