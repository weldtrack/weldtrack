from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db import get_db
from app.models.user import User, UserRole
from app.models.verification_code import EmailVerification, EmailVerificationCode
from app.schemas.user import SignupRequest
from app.services.auth_service import (
    build_auth_response,
    generate_verification_code,
    get_user_by_email,
    set_auth_cookie,
)
from app.services.email import send_verification_email

router = APIRouter(prefix="/auth", tags=["verification"])

@router.post("/signup", status_code=status.HTTP_200_OK)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    """Request signup — validate email and send verification code. Account is not created yet."""

    if get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    existing_code = db.scalar(
        select(EmailVerificationCode).where(
            EmailVerificationCode.email == payload.email
        )
    )
    if existing_code:
        db.delete(existing_code)
        db.flush()

    db.add(
        EmailVerificationCode(
            email=payload.email,
            code=generate_verification_code(),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        )
    )
    db.commit()

    verification_record = db.scalar(
        select(EmailVerificationCode).where(
            EmailVerificationCode.email == payload.email
        )
    )

    if not send_verification_email(payload.email, verification_record.code):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email",
        )

    return {
        "success": True,
        "message": "Verification code sent to email. Code will expire in 15 minutes.",
    }


@router.post("/verifyemail")
def request_verification_email(payload: dict, db: Session = Depends(get_db)):
    """Send a verification code to an existing user (for password reset)."""
    email = payload.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required"
        )

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email not found"
        )

    email_verification = user.email_verification
    if not email_verification:
        email_verification = EmailVerification(user_id=user.id)
        db.add(email_verification)

    verification_code = generate_verification_code()
    email_verification.verification_code = verification_code
    email_verification.code_expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=15
    )
    db.commit()

    if not send_verification_email(email, verification_code):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email",
        )

    return {
        "success": True,
        "message": "Verification code sent to email. Code will expire in 15 minutes.",
    }


@router.post("/verifycode")
def verify_code(payload: dict, response: Response, db: Session = Depends(get_db)):
    """Verify email code for account creation or password reset."""
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
        db.flush()

        db.add(EmailVerification(user_id=user.id, is_verified=True))
        db.delete(verification_record)
        db.commit()
        db.refresh(user)

        auth_response = build_auth_response(user)
        set_auth_cookie(response, auth_response.access_token)
        return auth_response

    elif action == "changepassword":
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email not found"
            )

        email_verification = user.email_verification
        if not email_verification or not email_verification.verification_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No verification code found. Please request a password reset.",
            )

        if (
            email_verification.code_expires_at
            and datetime.now(timezone.utc) > email_verification.code_expires_at
        ):
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
            "email": user.email,
            "role": user.role.value,
        }

    return {"success": False, "message": "Invalid action"}


@router.post("/forgot-password/reset")
def reset_password(payload: dict, db: Session = Depends(get_db)):
    """Reset password using a previously verified code."""
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Email not found"
        )

    email_verification = user.email_verification
    if not email_verification or not email_verification.verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification code found. Please request a password reset.",
        )

    if (
        email_verification.code_expires_at
        and datetime.now(timezone.utc) > email_verification.code_expires_at
    ):
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
