from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from students.models import StudentProfile


def feats(p):
    return [float(p.cgpa), p.readiness_score, p.mock_score, p.aptitude_score, len(p.skills), p.backlogs]


def rule_prob(p):
    """Used when there is no history to learn from: readiness score, reduced by backlogs."""
    return max(0.0, min(1.0, p.readiness_score / 100 - 0.1 * p.backlogs))


def weak_areas(p):
    w = []
    if p.mock_score < 50: w.append("Mock interview")
    if p.aptitude_score < 50: w.append("Aptitude")
    if len(p.skills) < 4: w.append("Skills")
    if p.backlogs: w.append("Backlogs")
    if float(p.cgpa) < 6.5: w.append("CGPA")
    return w


def at_risk(threshold=0.45):
    allp = list(StudentProfile.objects.select_related("user", "mentor"))
    if not allp:
        return []
    current = max(p.batch for p in allp)
    hist = [p for p in allp if p.batch < current]
    cur = [p for p in allp if p.batch == current and not p.placed]
    if not cur:
        return []
    if len(hist) >= 30 and len({p.placed for p in hist}) == 2:
        model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
        model.fit([feats(p) for p in hist], [int(p.placed) for p in hist])
        probs, method = model.predict_proba([feats(p) for p in cur])[:, 1], "ml"
    else:
        probs, method = [rule_prob(p) for p in cur], "rules"
    out = []
    for p, pr in zip(cur, probs):
        if pr < threshold:
            out.append({"id": p.id, "roll_no": p.roll_no, "name": p.user.get_full_name() or p.user.username,
                        "branch": p.branch, "probability": round(float(pr) * 100),
                        "weak_areas": weak_areas(p), "method": method,
                        "mentor": (p.mentor.get_full_name() or p.mentor.username) if p.mentor else None})
    return sorted(out, key=lambda x: x["probability"])