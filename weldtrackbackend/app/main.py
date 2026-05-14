import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


load_dotenv()

from app.api import router
from app.db import Base, engine, SessionLocal


# Base.metadata.create_all(bind=engine)
Base.metadata.drop_all(bind=engine)

import base64
import hashlib
import secrets
from sqlalchemy import select

from app.models.user import User, UserRole
from app.models.verification_code import EmailVerification

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
PASSWORD_HASH_ITERATIONS = 120_000
PASSWORD_HASH_PREFIX = "pbkdf2_sha256"


def _make_hashed_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )
    return f"{PASSWORD_HASH_PREFIX}${base64.b64encode(salt).decode('utf-8')}${base64.b64encode(digest).decode('utf-8')}"


def _create_admin_if_missing() -> None:
    db = SessionLocal()
    try:
        existing = db.scalar(select(User).where(User.email == ADMIN_EMAIL))
        if existing:
            return

        admin = User(
            email=ADMIN_EMAIL,
            hashed_password=_make_hashed_password(ADMIN_PASSWORD),
            role=UserRole.admin,
        )
        db.add(admin)
        db.flush()

        ev = EmailVerification(user_id=admin.id, is_verified=True)
        db.add(ev)
        db.commit()
    finally:
        db.close()

_create_admin_if_missing()

app = FastAPI(title="Weldtrack")
origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST")
    port = int(os.getenv("PORT"))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
