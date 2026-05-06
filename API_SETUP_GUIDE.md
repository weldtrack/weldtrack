# WeldTrack API Setup Guide

## Backend Environment Variables

Create a `.env` file in the `weldtrackbackend` directory with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/weldtrack

# Server
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Cookie Configuration
AUTH_COOKIE_NAME=access_token
AUTH_COOKIE_SECURE=false  # Set to true in production with HTTPS
AUTH_COOKIE_SAMESITE=lax
```

## Frontend Environment Variables

Create a `.env` file in the `weldtrackfrontend` directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Running the Application

### Backend
```bash
cd weldtrackbackend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

### Frontend
```bash
cd weldtrackfrontend
npm install
npm run dev
```

## API Base URL
- Backend: `http://localhost:8000`
- API Endpoints: `http://localhost:8000/api`
- Frontend: `http://localhost:5173`

## Database Setup

If using PostgreSQL, create a database:
```bash
createdb weldtrack
```

The database tables will be created automatically when the app starts.

## Testing the API

You can test the API endpoints using:
- **curl**: `curl http://localhost:8000/api/bookings`
- **Postman**: Import the API endpoints
- **Browser**: Visit `http://localhost:8000/docs` for Swagger documentation

## Notes

- All API endpoints are prefixed with `/api`
- Authentication is required for most endpoints (except login/signup)
- The app uses JWT tokens for authentication
- Tokens expire after the configured `ACCESS_TOKEN_EXPIRE_MINUTES`
