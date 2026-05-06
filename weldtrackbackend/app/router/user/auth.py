from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User, UserRole
from app.schemas.user import AuthResponse, LoginRequest, SignupRequest, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
AUTH_COOKIE_NAME = os.getenv("AUTH_COOKIE_NAME", "access_token")
AUTH_COOKIE_SECURE = os.getenv("AUTH_COOKIE_SECURE", "false").lower() == "true"
AUTH_COOKIE_SAMESITE = os.getenv("AUTH_COOKIE_SAMESITE", "lax")
PASSWORD_HASH_ITERATIONS = 120_000
PASSWORD_HASH_PREFIX = "pbkdf2_sha256"


def _b64url_encode(data: bytes) -> str:
	return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
	padding = "=" * (-len(data) % 4)
	return base64.urlsafe_b64decode(data + padding)


def encode_jwt(payload: dict[str, Any]) -> str:
	header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
	header_segment = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
	payload_segment = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
	signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
	signature = hmac.new(JWT_SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
	return f"{header_segment}.{payload_segment}.{_b64url_encode(signature)}"


def decode_jwt(token: str) -> dict[str, Any]:
	try:
		header_segment, payload_segment, signature_segment = token.split(".")
	except ValueError as exc:
		raise ValueError("Invalid token format") from exc

	header = json.loads(_b64url_decode(header_segment))
	if header.get("alg") != JWT_ALGORITHM:
		raise ValueError("Unsupported token algorithm")

	signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
	expected_signature = hmac.new(JWT_SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
	provided_signature = _b64url_decode(signature_segment)
	if not hmac.compare_digest(expected_signature, provided_signature):
		raise ValueError("Invalid token signature")

	payload = json.loads(_b64url_decode(payload_segment))
	expires_at = payload.get("exp")
	if expires_at is not None and datetime.now(timezone.utc).timestamp() >= float(expires_at):
		raise ValueError("Token has expired")
	return payload


def hash_password(password: str) -> str:
	salt = secrets.token_bytes(16)
	digest = hashlib.pbkdf2_hmac(
		"sha256",
		password.encode("utf-8"),
		salt,
		PASSWORD_HASH_ITERATIONS,
	)
	return f"{PASSWORD_HASH_PREFIX}${base64.b64encode(salt).decode('utf-8')}${base64.b64encode(digest).decode('utf-8')}"


def verify_password(password: str, hashed_password: str) -> bool:
	try:
		algorithm, salt_value, digest_value = hashed_password.split("$", 2)
	except ValueError:
		return False

	if algorithm != PASSWORD_HASH_PREFIX:
		return False

	salt = base64.b64decode(salt_value.encode("utf-8"))
	expected_digest = base64.b64decode(digest_value.encode("utf-8"))
	candidate_digest = hashlib.pbkdf2_hmac(
		"sha256",
		password.encode("utf-8"),
		salt,
		PASSWORD_HASH_ITERATIONS,
	)
	return hmac.compare_digest(candidate_digest, expected_digest)


def create_access_token(user: User) -> str:
	expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	payload = {
		"sub": str(user.id),
		"email": user.email,
		"role": user.role.value,
		"exp": int(expires_at.timestamp()),
	}
	return encode_jwt(payload)


def get_user_response(user: User) -> UserRead:
	return UserRead.model_validate(user)


def build_auth_response(user: User) -> AuthResponse:
	return AuthResponse(access_token=create_access_token(user), user=get_user_response(user))


def set_auth_cookie(response: Response, token: str) -> None:
	response.set_cookie(
		key=AUTH_COOKIE_NAME,
		value=token,
		httponly=True,
		secure=AUTH_COOKIE_SECURE,
		samesite=AUTH_COOKIE_SAMESITE,
		max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
		path="/",
	)


def get_user_by_email(db: Session, email: str) -> User | None:
	statement = select(User).where(User.email == email)
	return db.scalar(statement)


def get_current_user(
	request: Request,
	db: Session = Depends(get_db),
) -> User:
	token = request.cookies.get(AUTH_COOKIE_NAME)
	if token is None:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Not authenticated",
			headers={"WWW-Authenticate": "Bearer"},
		)

	try:
		payload = decode_jwt(token)
		user_id = int(payload["sub"])
	except (KeyError, ValueError, TypeError, json.JSONDecodeError):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid or expired token",
			headers={"WWW-Authenticate": "Bearer"},
		) from None

	user = db.get(User, user_id)
	if user is None:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="User not found",
			headers={"WWW-Authenticate": "Bearer"},
		)
	return user


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
	existing_user = get_user_by_email(db, payload.email)
	if existing_user is not None:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Email is already registered",
		)

	user = User(
		email=payload.email,
		name=payload.name,
		hashed_password=hash_password(payload.password),
		role=UserRole.customer,
	)
	db.add(user)
	db.commit()
	db.refresh(user)
	auth_response = build_auth_response(user)
	set_auth_cookie(response, auth_response.access_token)
	return auth_response


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
	user = get_user_by_email(db, payload.email)
	if user is None or not verify_password(payload.password, user.hashed_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid email or password",
			headers={"WWW-Authenticate": "Bearer"},
		)

	auth_response = build_auth_response(user)
	set_auth_cookie(response, auth_response.access_token)
	return auth_response


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> UserRead:
	return get_user_response(current_user)
