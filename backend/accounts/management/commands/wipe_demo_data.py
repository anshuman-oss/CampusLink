from django.core.management.base import BaseCommand
from accounts.models import Notification, User
from core.models import AuditLog
from drives.models import Drive
from jobs.models import Company, JobDescription, Match
from offers.models import Offer
from students.models import StudentProfile


class Command(BaseCommand):
    help = "Permanently delete ALL application data. Superuser accounts are kept."

    def add_arguments(self, parser):
        parser.add_argument("--yes", action="store_true", help="skip the confirmation prompt")

    def handle(self, *args, **opts):
        if not opts["yes"]:
            ans = input("This permanently deletes ALL students, jobs, drives, offers and "
                        "non-superuser accounts. Type YES to continue: ")
            if ans != "YES":
                self.stdout.write("Cancelled.")
                return
        for model in (Offer, Drive, Match, JobDescription, Company, StudentProfile, Notification):
            model.all_objects.all().hard_delete()
        AuditLog.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        for su in User.objects.filter(is_superuser=True):
            su.save()                                  # makes sure the role is "officer"
        self.stdout.write(self.style.SUCCESS("Done. Only superuser accounts remain."))