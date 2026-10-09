import os
import smtplib
import ssl
from email.message import EmailMessage


def send_email(to, subject, body):
    """Send one email through Gmail. Raises an error with the reason if it fails."""
    user = os.environ.get("EMAIL_USER", "")
    password = os.environ.get("EMAIL_APP_PASSWORD", "")
    if not (user and password):
        raise RuntimeError("EMAIL_USER or EMAIL_APP_PASSWORD is missing. Check the .env file and restart the server.")
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"CampusLink <{user}>"
    msg["To"] = to
    msg.set_content(body)
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
        server.starttls(context=ssl.create_default_context())
        server.login(user, password)
        server.send_message(msg)