import os
import resend

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL")

resend.api_key = RESEND_API_KEY


def send_verification_email(to_email: str, verification_code: str) -> bool:
    """
    Send verification code to user's email using Resend.
    
    Args:
        to_email: Recipient email address
        verification_code: 6-digit verification code
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        response = resend.Emails.send({
            "from": RESEND_FROM_EMAIL,
            "to": to_email,
            "subject": "WeldTrack Email Verification",
            "html": f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Email Verification</h2>
                    <p>Your verification code is:</p>
                    <h1 style="color: #007bff; letter-spacing: 5px;">{verification_code}</h1>
                    <p>This code will expire in 15 minutes.</p>
                    <p>If you didn't request this code, please ignore this email.</p>
                </body>
            </html>
            """
        })

        return response.get("id") is not None

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False