import requests

from app.core.config import settings


def send_verification_email(to_email: str, verification_code: str) -> bool:
    """
    Send verification code to user's email using Brevo transactional API.

    Args:
        to_email: Recipient email address
        verification_code: 6-digit verification code

    Returns:
        True if email sent successfully, False otherwise
    """
    api_key = getattr(settings, "BREVO_API_KEY", "") or getattr(settings, "RESEND_API_KEY", "")
    from_email = getattr(settings, "BREVO_FROM_EMAIL", "noreply@weldtrack.shop") or "noreply@weldtrack.shop"
    from_name = getattr(settings, "BREVO_FROM_NAME", "WeldTrack") or "WeldTrack"

    if not api_key or api_key.startswith("your_") or api_key in ("dummy", "mock"):
        print(
            f"[EMAIL DEV LOG] Brevo API key not configured or placeholder. "
            f"Simulating email to: {to_email}, Code: {verification_code}"
        )
        return True

    payload = {
        "sender": {
            "name": from_name,
            "email": from_email,
        },
        "to": [{"email": to_email}],
        "subject": "WeldTrack Email Verification",
        "htmlContent": f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Email Verification</h2>
                <p>Your verification code is:</p>
                <h1 style="color: #007bff; letter-spacing: 5px;">{verification_code}</h1>
                <p>This code will expire in 15 minutes.</p>
                <p>If you didn't request this code, please ignore this email.</p>
            </body>
        </html>
        """,
    }

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }

    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers=headers,
            timeout=10,
        )

        if response.status_code in (200, 201):
            return True

        print(f"Brevo API error: {response.status_code} - {response.text}")
        if not settings.is_prod:
            print(f"[EMAIL DEV FALLBACK] Simulating email delivery in development mode for {to_email}")
            return True
        return False

    except Exception as e:
        print(f"Error sending email via Brevo: {str(e)}")
        if not settings.is_prod:
            print(f"[EMAIL DEV FALLBACK] Simulating email delivery in development mode for {to_email}")
            return True
        return False
