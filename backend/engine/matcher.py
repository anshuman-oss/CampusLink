from sentence_transformers import util
from students.models import StudentProfile
from jobs.models import Match
from .nlp import embed
from .scoring import student_text, eligibility, fit, explain, level
def run_match(job):
    students = list(StudentProfile.objects.filter(consent_given=True))  
    if not students:
        return 0
    sims = util.cos_sim(embed([job.description]),
                        embed([student_text(s) for s in students]))[0].tolist()
    Match.all_objects.filter(job=job).hard_delete()
    rows = []
    for p, sem in zip(students, sims):
        reasons = eligibility(p, job)
        score, parts, matched, missing = fit(p, job, sem)
        if reasons:
            status = "below_threshold"
        else:
            status = "shortlisted" if score >= 60 else "waitlist" if score >= 45 else "below_threshold"
        rows.append(Match(job=job, student=p, fit_score=score, level=level(score),
                          eligible=not reasons, status=status,
                          explanation=explain(p, job, score, parts, matched, missing, reasons)))
    Match.objects.bulk_create(rows)
    return len(rows)