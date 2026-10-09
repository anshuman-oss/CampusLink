from sentence_transformers import util
from jobs.models import JobDescription, Match
from students.models import StudentProfile
from .nlp import embed
from .scoring import eligibility, explain, fit, level, student_text


def _fields(p, job, sem):
    reasons = eligibility(p, job)
    score, parts, matched, missing = fit(p, job, sem)
    if reasons:
        status = "below_threshold"
    else:
        status = "shortlisted" if score >= 60 else "waitlist" if score >= 45 else "below_threshold"
    return dict(fit_score=score, level=level(score), eligible=not reasons, status=status,
                explanation=explain(p, job, score, parts, matched, missing, reasons))


def run_match(job):
    """Match every active student with consent against one job."""
    students = list(StudentProfile.objects.filter(consent_given=True))
    if not students:
        return 0
    sims = util.cos_sim(embed([job.description]),
                        embed([student_text(s) for s in students]))[0].tolist()
    Match.all_objects.filter(job=job).hard_delete()      # derived data: safe to rebuild
    Match.objects.bulk_create([Match(job=job, student=p, **_fields(p, job, sem))
                               for p, sem in zip(students, sims)])
    return len(students)


def rematch_student(p):
    """Refresh one student's matches for all open jobs (after profile or resume changes)."""
    jobs = list(JobDescription.objects.filter(status="open"))
    if not jobs or not p.consent_given:
        return 0
    s_vec = embed([student_text(p)])
    for job in jobs:
        sem = float(util.cos_sim(embed([job.description]), s_vec)[0][0])
        Match.all_objects.update_or_create(
            job=job, student=p,
            defaults={**_fields(p, job, sem), "is_active": True, "deleted_at": None})
    return len(jobs)