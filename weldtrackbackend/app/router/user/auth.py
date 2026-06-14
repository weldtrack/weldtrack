from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.middleware.auth_middleware import (
	ACCESS_TOKEN_EXPIRE_MINUTES,
	AUTH_COOKIE_NAME,
	AUTH_COOKIE_SAMESITE,
	AUTH_COOKIE_SECURE,
	create_access_token,
	get_current_user,
	hash_password,
	verify_password,
)
from app.models.user import User, UserRole
from app.models.verification_code import EmailVerificationCode, EmailVerification
from app.schemas.user import AuthResponse, LoginRequest, SignupRequest, UserRead
from app.services.email import send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])


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


def generate_verification_code() -> str:
	"""Generate a random 6-digit verification code"""
	return str(secrets.randbelow(1000000)).zfill(6)





@router.post("/signup", status_code=status.HTTP_200_OK)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
	"""Request signup - validate and send verification code (account not created yet)"""
	existing_user = get_user_by_email(db, payload.email)
	if existing_user is not None:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Email is already registered",
		)
	
	verification_code = generate_verification_code()
	expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
	
	existing_code = db.scalar(
		select(EmailVerificationCode).where(EmailVerificationCode.email == payload.email)
	)
	if existing_code:
		db.delete(existing_code)
	
	verification_record = EmailVerificationCode(
		email=payload.email,
		code=verification_code,
		expires_at=expires_at
	)
	db.add(verification_record)
	db.commit()
	
	email_sent = send_verification_email(payload.email, verification_code)
	
	if not email_sent:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Failed to send verification email",
		)
	
	return {
		"success": True,
		"message": "Verification code sent to email. Code will expire in 15 minutes."
	}


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
	user = get_user_by_email(db, payload.email)
	if user is None or not verify_password(payload.password, user.hashed_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid email or password",
			headers={"WWW-Authenticate": "Bearer"},
		)

	if user.is_banned:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="You are banned from logging in. Please contact an administrator.",
		)

	try:
		user.last_active = datetime.now(timezone.utc)
		db.add(user)
		db.commit()
		db.refresh(user)
	except Exception:
		db.rollback()

	auth_response = build_auth_response(user)
	set_auth_cookie(response, auth_response.access_token)
	return auth_response


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> UserRead:
	return get_user_response(current_user)


@router.get("/staff", response_model=list[UserRead])
def list_staff_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[UserRead]:
	if current_user.role != UserRole.admin:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires admin privileges")

	users = db.scalars(select(User).where(User.role == UserRole.staff).order_by(User.id)).all()
	return [get_user_response(user) for user in users]


@router.post("/logout")
def logout(response: Response, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, bool | str]:
	"""Clear the auth cookie and invalidate the token."""
	try:
		current_user.logged_out_at = datetime.now(timezone.utc)
		db.add(current_user)
		db.commit()
		db.refresh(current_user)
	except Exception:
		db.rollback()
	
	response.delete_cookie(key=AUTH_COOKIE_NAME, path="/")
	return {"success": True, "message": "Logged out successfully"}



def is_user_online(user: User) -> bool:
	"""Determine if user is online based on session activity (last_active within 30 seconds)"""
	if user.last_active is None:
		return False
	thirty_seconds_ago = datetime.now(timezone.utc) - timedelta(seconds=30)
	return user.last_active >= thirty_seconds_ago


@router.get("/admin/users", response_model=list[UserRead])
def admin_get_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[UserRead]:
	"""Admin-only: get all non-admin users (customers and staff)"""
	if current_user.role != UserRole.admin:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires admin privileges")
	
	users = db.scalars(
		select(User)
		.where(User.role != UserRole.admin)
		.order_by(User.last_active.desc(), User.id.desc())
	).all()
	
	for user in users:
		user.is_online = is_user_online(user)
	
	return [get_user_response(user) for user in users]


@router.get("/admin/online", response_model=list[UserRead])
def admin_get_online_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[UserRead]:
	"""Admin-only: get online users (based on recent last_active within 30 seconds)"""
	if current_user.role != UserRole.admin:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires admin privileges")
	
	thirty_seconds_ago = datetime.now(timezone.utc) - timedelta(seconds=30)
	
	users = db.scalars(
		select(User)
		.where(User.role != UserRole.admin)
		.where((User.last_active != None) & (User.last_active >= thirty_seconds_ago))
		.order_by(User.last_active.desc(), User.id.desc())
	).all()
	
	for user in users:
		user.is_online = True
	
	return [get_user_response(user) for user in users]


@router.post("/admin/ban/{user_id}")
def admin_ban_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, bool | str]:
	"""Admin-only: ban a user"""
	if current_user.role != UserRole.admin:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires admin privileges")
	
	if user_id == current_user.id:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot ban yourself")
	
	user = db.get(User, user_id)
	if not user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
	
	if user.role == UserRole.admin:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot ban admin users")
	
	try:
		user.is_banned = True
		db.add(user)
		db.commit()
		db.refresh(user)
	except Exception:
		db.rollback()
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to ban user")
	
	return {"success": True, "message": f"User {user.email} has been banned"}


@router.post("/admin/unban/{user_id}")
def admin_unban_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, bool | str]:
	"""Admin-only: unban a user"""
	if current_user.role != UserRole.admin:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires admin privileges")
	
	user = db.get(User, user_id)
	if not user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
	
	if user.role == UserRole.admin:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot unban admin users")
	
	try:
		user.is_banned = False
		db.add(user)
		db.commit()
		db.refresh(user)
	except Exception:
		db.rollback()
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to unban user")
	
	return {"success": True, "message": f"User {user.email} has been unbanned"}



@router.post("/verifyemail")
def request_verification_email(payload: dict, db: Session = Depends(get_db)):
	"""Request email verification code for existing user (password reset)"""
	email = payload.get("email")
	if not email:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Email is required",
		)
	
	user = get_user_by_email(db, email)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Email not found",
		)
	
	email_verification = user.email_verification
	if not email_verification:
		email_verification = EmailVerification(user_id=user.id)
		db.add(email_verification)
	
	verification_code = generate_verification_code()
	email_verification.verification_code = verification_code
	email_verification.code_expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
	db.commit()
	
	email_sent = send_verification_email(email, verification_code)
	
	if not email_sent:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Failed to send verification email",
		)
	
	return {
		"success": True,
		"message": "Verification code sent to email. Code will expire in 15 minutes."
	}


@router.post("/verifycode")
def verify_code(payload: dict, response: Response, db: Session = Depends(get_db)):
	"""Verify email code for account creation or password reset"""
	email = payload.get("email")
	code = payload.get("code")
	password = payload.get("password")
	action = payload.get("action", "createaccount")
	
	if not email or not code:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Email and code are required",
		)
	
	user = get_user_by_email(db, email)
	
	if action == "createaccount":
		if user:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Email is already registered",
			)
		
		verification_record = db.scalar(
			select(EmailVerificationCode).where(EmailVerificationCode.email == email)
		)
		
		if not verification_record:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="No verification code found. Please request a new signup.",
			)
		
		if datetime.now(timezone.utc) > verification_record.expires_at:
			db.delete(verification_record)
			db.commit()
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Verification code has expired. Please request a new signup.",
			)
		
		if verification_record.code != code:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Invalid verification code",
			)
		
		if not password:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Password is required to complete signup",
			)
		
		user = User(
			email=email,
			hashed_password=hash_password(password),
			role=UserRole.customer,
		)
		db.add(user)
		db.flush()  # Get user.id before creating EmailVerification
		
		email_verification = EmailVerification(
			user_id=user.id,
			is_verified=True
		)
		db.add(email_verification)
		
		db.delete(verification_record)
		db.commit()
		db.refresh(user)
		
		auth_response = build_auth_response(user)
		set_auth_cookie(response, auth_response.access_token)
		return auth_response
	
	elif action == "changepassword":
		if not user:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Email not found",
			)
		
		email_verification = user.email_verification
		if not email_verification or not email_verification.verification_code:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="No verification code found. Please request a password reset.",
			)
		
		if email_verification.code_expires_at and datetime.now(timezone.utc) > email_verification.code_expires_at:
			email_verification.verification_code = None
			email_verification.code_expires_at = None
			db.commit()
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Verification code has expired. Please request a new password reset.",
			)
		
		if email_verification.verification_code != code:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Invalid verification code",
			)
		
		return {
			"success": True,
			"token": create_access_token(user),
			"email": user.email,
			"role": user.role.value,
		}
	
	return {"success": False, "message": "Invalid action"}


@router.post("/admin/create-staff")
def admin_create_staff(payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	"""Admin-only: create a staff account without requiring email verification."""
	if current_user.role != UserRole.admin:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires admin privileges")

	email = payload.get("email")
	password = payload.get("password")

	if not email or not password:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and password are required")

	if len(password) < 8:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters long")

	existing = get_user_by_email(db, email)
	if existing:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")

	user = User(
		email=email,
		hashed_password=hash_password(password),
		role=UserRole.staff,
	)
	db.add(user)
	db.flush()

	email_verification = EmailVerification(user_id=user.id, is_verified=True)
	db.add(email_verification)
	db.commit()
	db.refresh(user)

	return {"success": True, "user": get_user_response(user)}


@router.delete("/staff/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff(staff_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	"""Admin-only: delete a staff member"""
	if current_user.role != UserRole.admin:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires admin privileges")

	staff_user = db.get(User, staff_id)
	if not staff_user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff member not found")

	if staff_user.role != UserRole.staff:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only delete staff members")

	db.delete(staff_user)
	db.commit()


@router.post("/forgot-password/reset")
def reset_password(payload: dict, db: Session = Depends(get_db)):
	"""Reset password with verification code"""
	email = payload.get("email")
	code = payload.get("code")
	new_password = payload.get("password")
	password_confirmation = payload.get("password_confirmation")
	
	if not all([email, code, new_password, password_confirmation]):
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Email, code, and passwords are required",
		)
	
	if new_password != password_confirmation:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Passwords do not match",
		)
	
	user = get_user_by_email(db, email)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Email not found",
		)
	
	email_verification = user.email_verification
	if not email_verification or not email_verification.verification_code:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="No verification code found. Please request a password reset.",
		)
	
	if email_verification.code_expires_at and datetime.now(timezone.utc) > email_verification.code_expires_at:
		email_verification.verification_code = None
		email_verification.code_expires_at = None
		db.commit()
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Verification code has expired. Please request a new password reset.",
		)
	
	if email_verification.verification_code != code:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Invalid verification code",
		)
	
	user.hashed_password = hash_password(new_password)
	email_verification.verification_code = None
	email_verification.code_expires_at = None
	db.commit()
	
	return {"success": True, "message": "Password reset successful"}


@router.get("/admin/users", response_model=list[UserRead])
def list_all_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[UserRead]:
	if current_user.role != UserRole.admin:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires admin privileges")

	users = db.scalars(select(User).order_by(User.id)).all()
	return [get_user_response(user) for user in users]


@router.get("/admin/online", response_model=list[UserRead])
def list_online_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[UserRead]:
	if current_user.role != UserRole.admin:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires admin privileges")

	threshold = datetime.now(timezone.utc) - timedelta(minutes=5)
	users = db.scalars(
		select(User)
		.where(User.is_online.is_(True) | ((User.last_active != None) & (User.last_active >= threshold)))
		.order_by(User.id)
	).all()
	return [get_user_response(user) for user in users]


@router.post("/admin/ban/{user_id}")
def ban_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> UserRead:
	if current_user.role != UserRole.admin:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires admin privileges")

	user = db.get(User, user_id)
	if not user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

	user.is_banned = True
	db.add(user)
	db.commit()
	db.refresh(user)
	return get_user_response(user)


@router.post("/admin/unban/{user_id}")
def unban_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> UserRead:
	if current_user.role != UserRole.admin:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires admin privileges")

	user = db.get(User, user_id)
	if not user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

	user.is_banned = False
	db.add(user)
	db.commit()
	db.refresh(user)
	return get_user_response(user)
