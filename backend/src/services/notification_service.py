from aiosmtplib import send
from email.message import EmailMessage
from config import get_settings

settings = get_settings()

class NotificationService:
    async def send_email(self, recipient_email: str, subject: str, body: str):
        message = EmailMessage()
        message["From"] = settings.smtp_username
        message["To"] = recipient_email
        message["Subject"] = subject
        message.set_content(body)

        try:
            await send(
                message,
                hostname=settings.smtp_server,
                port=settings.smtp_port,
                username=settings.smtp_username,
                password=settings.smtp_password,
                start_tls=True
            )
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

notification_service = NotificationService()
