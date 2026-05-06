import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")


def send_verification_email(to_email: str, verification_code: str) -> bool:
    """
    Send verification code to user's email using SendGrid.
    
    Args:
        to_email: Recipient email address
        verification_code: 6-digit verification code
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=to_email,
            subject="WeldTrack Email Verification",
            html_content=f"""
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
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        # SendGrid returns 202 for successful send
        return response.status_code == 202
    
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False
