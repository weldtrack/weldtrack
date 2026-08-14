# WeldTrack Backend

The API for WeldTrack, built with FastAPI and PostgreSQL. It manages core business logic including inventory tracking, project scheduling, and multi-role authentication.

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Auth:** JWT-based with HTTP-only cookies
- **Email:** SendGrid API

## Local Setup

### 1. Requirements
- Python 3.10+
- PostgreSQL instance

### 2. Installation
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env` and update the values:
```bash
cp .env.example .env
```
Key variables to configure:
- `DATABASE_URL`: Your PostgreSQL connection string.
- `SENDGRID_API_KEY`: For email verifications.
- `ADMIN_EMAIL` & `ADMIN_PASSWORD`: Initial admin credentials (scripts).

### 4. Running the Server
```bash
# From the weldtrackbackend directory
python app/main.py
```
The server will start at `http://0.0.0.0:8000`.

## Features
- **Auto-Bootstrap:** Creates the initial admin account on first run if no users exist.
- **Middleware:** Includes CORS and JWT authentication middleware.
- **Reporting:** Endpoints for generating business analytics and staff attendance data.
