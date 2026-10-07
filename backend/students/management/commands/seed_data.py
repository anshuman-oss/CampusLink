import random, math
from datetime import date, time, timedelta
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from accounts.models import User
from students.models import StudentProfile
from jobs.models import Company, JobDescription
from drives.models import Drive
from offers.models import Offer
from engine.nlp import SKILLS, parse_jd
from engine.scoring import readiness
from engine.matcher import run_match

FIRST = ["Aarav", "Ananya", "Subham", "Priya", "Rahul", "Sneha", "Dipun", "Nihar", "Ipsita", "Rohit"]
LAST = ["Sahoo", "Mishra", "Rout", "Behera", "Lenka", "Tripathy", "Das", "Nayak", "Patra", "Mohanty"]
BR = {"CSE": .3, "IT": .2, "ECE": .2, "EEE": .1, "ME": .1, "CE": .1}
CERTS = ["AWS Cloud Practitioner", "Python Basics", "SQL Bootcamp", "Azure Fundamentals"]
JDS = [
    ("CloudCorp", "Cloud Engineer", 8.5, "Looking for engineers with AWS, Docker, Linux and Git. "
     "Minimum CGPA 7.0, no backlogs. CSE, IT and ECE branches."),
    ("DataNest", "Data Analyst", 6.0, "Need SQL, Excel, Python and machine learning skills with good "
     "communication. CGPA 6.5 and above."),
    ("WebCraft", "Full-Stack Developer", 7.5, "React, Node, JavaScript, REST API and SQL experience "
     "required. CGPA 6.0. CSE and IT."),
]


class Command(BaseCommand):
    help = "Create demo data: 300 students, 3 recruiters, JDs, drive, offers"

    def handle(self, *args, **kw):
        if User.objects.filter(username="officer").exists():
            self.stdout.write("Already seeded."); return
        random.seed(7)
        pw = make_password("demo123")                    # hash once = fast seeding
        names = list(SKILLS)
        User.objects.create(username="officer", password=pw, role="officer", is_staff=True)
        mentors = [User.objects.create(username=f"mentor{i}", password=pw, role="mentor") for i in (1, 2)]

        for i in range(300):
            u = User.objects.create(username=f"s{i:03d}", password=pw, role="student",
                                    first_name=random.choice(FIRST), last_name=random.choice(LAST),
                                    email=f"s{i:03d}@demo.edu")
            sk = random.sample(names, random.randint(2, 10))
            pr = [{"title": f"{s.title()} project", "desc": f"Built an application using {s}"}
                  for s in random.sample(sk, min(len(sk), random.randint(0, 3)))]
            p = StudentProfile(
                user=u, mentor=mentors[i % 2], roll_no=f"2201{i:04d}",
                branch=random.choices(list(BR), list(BR.values()))[0],
                cgpa=round(random.uniform(5.5, 9.5), 2),
                backlogs=random.choices([0, 1, 2], [.8, .15, .05])[0],
                aptitude_score=random.randint(35, 95), mock_score=random.randint(30, 95),
                soft_score=random.randint(40, 95), skills=sk, projects=pr,
                certifications=random.sample(CERTS, random.randint(0, 3)),
                batch=2025 if i < 200 else 2026)
            p.readiness_score, p.readiness_level, _ = readiness(p)
            z = 0.9 * (float(p.cgpa) - 7) + 0.04 * (p.mock_score - 60) + 0.3 * (len(sk) - 5) - 0.8 * p.backlogs
            p.placed = random.random() < (1 / (1 + math.exp(-z))) * (1 if p.batch == 2025 else 0.5)
            p.save()

        jobs = []
        for name, title, ctc, desc in JDS:
            cu = User.objects.create(username=name.lower(), password=pw, role="recruiter")
            c = Company.objects.create(user=cu, name=name, contact_email=f"hr@{name.lower()}.com")
            job = JobDescription.objects.create(company=c, title=title, description=desc,
                                                ctc_lpa=ctc, **parse_jd(desc))
            run_match(job); jobs.append(job)

        Drive.objects.create(job=jobs[0], venue="Main Auditorium", panel="Panel A",
                             date=date.today() + timedelta(days=7),
                             start_time=time(10, 0), end_time=time(13, 0))
        statuses = ["issued", "accepted", "accepted", "joined"]
        docs = ["pending", "submitted", "verified", "verified"]
        for job in jobs:
            for k, m in enumerate(job.matches.filter(status="shortlisted")[:4]):
                Offer.objects.create(student=m.student, job=job, ctc_lpa=job.ctc_lpa,
                                     status=statuses[k], docs_status=docs[k])
        self.stdout.write(self.style.SUCCESS("Seeded. Logins: officer / cloudcorp / s001, password demo123"))