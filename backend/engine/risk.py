from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from students.models import StudentProfile


def feats(p):
    return [float(p.cgpa), p.readiness_score, p.mock_score, p.aptitude_score, len(p.skills), p.backlogs]


def at_risk(threshold=0.45):
    hist = list(StudentProfile.objects.filter(batch__lt=2026))
    if len({p.placed for p in hist}) < 2:
        return []                                   # need both placed and unplaced examples
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    model.fit([feats(p) for p in hist], [int(p.placed) for p in hist])
    cur = list(StudentProfile.objects.filter(batch=2026, placed=False).select_related("user"))
    if not cur:
        return []
    probs = model.predict_proba([feats(p) for p in cur])[:, 1]
    out = []
    for p, pr in zip(cur, probs):
        if pr < threshold:
            weak = []
            if p.mock_score < 50: weak.append("Mock interview")
            if len(p.skills) < 4: weak.append("Skills")
            if p.backlogs: weak.append("Backlogs")
            if float(p.cgpa) < 6.5: weak.append("CGPA")
            out.append({"id": p.id, "roll_no": p.roll_no, "name": p.user.get_full_name(),
                        "branch": p.branch, "probability": round(float(pr) * 100),
                        "weak_areas": weak,
                        "mentor": p.mentor.username if p.mentor else None})
    return sorted(out, key=lambda x: x["probability"])