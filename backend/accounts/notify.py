from django.core.mail import send_mail
from .models import Notification


def notify(user, title, message):
    Notification.objects.create(user=user, title=title, message=message)
    if user.email:
        send_mail(title, message, "placements@campuslink.local", [user.email], fail_silently=True)