from datetime import datetime, timedelta, time
from jobs.models import Match
from .models import Drive
def _students(drive):
    return set(Match.objects.filter(job=drive.job, status="shortlisted")
               .values_list("student_id", flat=True))
def find_conflicts(drive):
    out, mine = [], _students(drive)
    others = Drive.objects.filter(date=drive.date, status="scheduled").exclude(pk=drive.pk)
    for o in others.select_related("job"):
        if drive.start_time < o.end_time and o.start_time < drive.end_time:    # time overlap
            if o.venue == drive.venue:
                out.append({"type": "VENUE", "with": o.job.title})
            if o.panel == drive.panel:
                out.append({"type": "PANEL", "with": o.job.title})
            common = mine & _students(o)
            if common:
                out.append({"type": "STUDENT", "with": o.job.title, "count": len(common)})
    return out
def suggest_slot(drive, days=5, step=30):
    dur = (datetime.combine(drive.date, drive.end_time) -
           datetime.combine(drive.date, drive.start_time))
    probe = Drive(job=drive.job, venue=drive.venue, panel=drive.panel)
    for d in range(days):
        day = drive.date + timedelta(days=d)
        t = datetime.combine(day, time(9, 0))
        while t + dur <= datetime.combine(day, time(18, 0)):
            probe.date, probe.start_time, probe.end_time = day, t.time(), (t + dur).time()
            if not find_conflicts(probe):
                return {"date": str(day), "start_time": str(t.time())[:5],
                        "end_time": str((t + dur).time())[:5]}
            t += timedelta(minutes=step)
    return None