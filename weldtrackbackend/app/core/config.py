from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

"""
Application configuration powered by Pydantic Settings.
"""

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DATABASE_URL: str = "postgresql+psycopg2://weldtrack:weldtrack_123@localhost:5432/weldtrack_db"
    CORS_ORIGINS: str = "http://localhost:8080,http://localhost:5173,http://127.0.0.1:5173"

    # JWT & Auth
    JWT_SECRET_KEY: str = "weldtrack-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    AUTH_COOKIE_NAME: str = "access_token"
    AUTH_COOKIE_SECURE: bool = False
    AUTH_COOKIE_SAMESITE: str = "lax"
    PASSWORD_HASH_ITERATIONS: int = 120_000
    PASSWORD_HASH_PREFIX: str = "pbkdf2_sha256"

    # Email & Integrations
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "noreply@ruzzgd.dev"
    EMAIL_CHECKER_API_KEY: str = ""

    # Object storage
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_PUBLIC_URL: str = "http://localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "weldtrack"
    MINIO_SECURE: bool = False

    # Initial Admin Seed
    ADMIN_EMAIL: str = "admin@weldtrack.com"
    ADMIN_PASSWORD: str = "Admin123!@#$"

    # Labor Rate
    FIXED_LABOR_RATE: float = 150.0

    # Attendance
    ATTENDANCE_TIMEZONE: str = "Asia/Manila"
    ATTENDANCE_MORNING_OPEN: str = "06:00"
    ATTENDANCE_MORNING_CLOSE: str = "08:00"
    ATTENDANCE_LATE_AFTER: str = "08:00"
    ATTENDANCE_MORNING_OUT_OPEN: str = "12:00"
    ATTENDANCE_AFTERNOON_IN_OPEN: str = "12:00"
    ATTENDANCE_AFTERNOON_IN_CLOSE: str = "14:00"
    ATTENDANCE_REGULAR_HOURS: float = 8.0

    @property
    def is_prod(self) -> bool:
        return self.ENV.lower() == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def minio_endpoint(self) -> str:
        if Path("/.dockerenv").exists():
            return self.MINIO_ENDPOINT
        return self.MINIO_ENDPOINT.replace("minio:", "localhost:", 1)


settings = Settings()

# Module-level variable exports for backward compatibility
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
AUTH_COOKIE_NAME = settings.AUTH_COOKIE_NAME
AUTH_COOKIE_SECURE = settings.AUTH_COOKIE_SECURE
AUTH_COOKIE_SAMESITE = settings.AUTH_COOKIE_SAMESITE
PASSWORD_HASH_ITERATIONS = settings.PASSWORD_HASH_ITERATIONS
PASSWORD_HASH_PREFIX = settings.PASSWORD_HASH_PREFIX

FIXED_LABOR_RATE = settings.FIXED_LABOR_RATE

ATTENDANCE_TIMEZONE = settings.ATTENDANCE_TIMEZONE
ATTENDANCE_MORNING_OPEN = settings.ATTENDANCE_MORNING_OPEN
ATTENDANCE_MORNING_CLOSE = settings.ATTENDANCE_MORNING_CLOSE
ATTENDANCE_LATE_AFTER = settings.ATTENDANCE_LATE_AFTER
ATTENDANCE_MORNING_OUT_OPEN = settings.ATTENDANCE_MORNING_OUT_OPEN
ATTENDANCE_AFTERNOON_IN_OPEN = settings.ATTENDANCE_AFTERNOON_IN_OPEN
ATTENDANCE_AFTERNOON_IN_CLOSE = settings.ATTENDANCE_AFTERNOON_IN_CLOSE
ATTENDANCE_REGULAR_HOURS = settings.ATTENDANCE_REGULAR_HOURS
