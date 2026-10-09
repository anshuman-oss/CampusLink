import logging
import threading
from .mailer import send_email
from .models import Notification

log = logging.getLogger(__name__)


def _send(to, title, message):
    try:
        send_email(to, title, message)
    except Exception:
        log.warning("Email to %s could not be sent.", to, exc_info=True)


def notify(user, title, message):
    Notification.objects.create(user=user, title=title, message=message)    # bell icon: always saved
    if user.email:
        threading.Thread(target=_send, args=(user.email, title, message), daemon=True).start()