import csv
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from accounts.models import User
from students.models import StudentProfile


class Command(BaseCommand):
    help = "Add students to the roster, one at a time or many from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument("--csv", help="CSV with columns: roll_no,first_name,last_name,email,branch,cgpa,backlogs,batch")
        parser.add_argument("--roll")
        parser.add_argument("--first", default="")
        parser.add_argument("--last", default="")
        parser.add_argument("--email")
        parser.add_argument("--branch", default="")
        parser.add_argument("--cgpa", default="0")
        parser.add_argument("--backlogs", default="0")
        parser.add_argument("--batch", default="2026")

    def handle(self, *args, **o):
        if o["csv"]:
            with open(o["csv"], newline="", encoding="utf-8-sig") as f:
                rows = list(csv.DictReader(f))
        elif o["roll"]:
            rows = [{"roll_no": o["roll"], "first_name": o["first"], "last_name": o["last"],
                     "email": o["email"], "branch": o["branch"], "cgpa": o["cgpa"],
                     "backlogs": o["backlogs"], "batch": o["batch"]}]
        else:
            raise CommandError("Use --csv FILE or --roll ROLLNO --email EMAIL ...")

        added = 0
        for r in rows:
            roll = (r.get("roll_no") or "").strip()
            email = (r.get("email") or "").strip().lower()
            if not roll or not email:
                self.stdout.write(self.style.WARNING(f"Skipped (roll_no and email are required): {r}"))
                continue
            if User.objects.filter(username__iexact=roll).exists() or \
               StudentProfile.all_objects.filter(roll_no__iexact=roll).exists():
                self.stdout.write(self.style.WARNING(f"Skipped (already exists): {roll}"))
                continue
            try:
                with transaction.atomic():
                    u = User(username=roll, email=email, role="student",
                             first_name=(r.get("first_name") or "").strip(),
                             last_name=(r.get("last_name") or "").strip())
                    u.set_unusable_password()
                    u.save()
                    StudentProfile.objects.create(
                        user=u, roll_no=roll, branch=(r.get("branch") or "").strip().upper(),
                        cgpa=float(r.get("cgpa") or 0), backlogs=int(r.get("backlogs") or 0),
                        batch=int(r.get("batch") or 2026))
                added += 1
            except (ValueError, TypeError) as e:
                self.stdout.write(self.style.ERROR(f"Skipped {roll}: bad number ({e})"))
        self.stdout.write(self.style.SUCCESS(f"Added {added} student(s)."))