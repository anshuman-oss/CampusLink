def level(s):
    if s < 40: return "Not Ready"
    if s < 60: return "Developing"
    if s < 80: return "Ready"
    return "Highly Employable"

def readiness(p):
    sp = min(len(p.skills) / 10, 1) * 0.6 + min(len(p.projects) / 3, 1) * 0.4
    parts = {
        "Skills and projects": 25 * sp,
        "Academics": 20 * max(float(p.cgpa) / 10 - 0.05 * p.backlogs, 0),
        "Mock interview": 20 * p.mock_score / 100,
        "Aptitude": 15 * p.aptitude_score / 100,
        "Soft skills": 10 * p.soft_score / 100,
        "Certifications": 10 * min(len(p.certifications) / 3, 1),
    }
    total = round(sum(parts.values()), 1)
    return total, level(total), {k: round(v, 1) for k, v in parts.items()}

def student_text(p):
    projects = [x.get("title", "") + " " + x.get("desc", "") for x in p.projects]
    return " ".join(list(p.skills) + list(p.certifications) + projects) or "no information"

def eligibility(p, job):
    r = []
    if float(p.cgpa) < float(job.min_cgpa):
        r.append(f"CGPA {p.cgpa} is below the required {job.min_cgpa}")
    if job.allowed_branches and p.branch not in job.allowed_branches:
        r.append(f"branch {p.branch} is not in the eligible list")
    if p.backlogs > job.max_backlogs:
        r.append(f"{p.backlogs} backlog(s) exceed the limit of {job.max_backlogs}")
    return r

def fit(p, job, sem):
    req, have = set(job.required_skills), set(p.skills)
    matched, missing = sorted(req & have), sorted(req - have)
    cov = len(matched) / len(req) if req else 1
    rs, _, _ = readiness(p)
    parts = {
        "Skill match": 40 * cov,
        "Semantic relevance": 20 * max(sem, 0),
        "Readiness": 20 * rs / 100,
        "Mock interview": 10 * min(p.mock_score / max(job.mock_benchmark, 1), 1),
        "Academics": 10 * min(float(p.cgpa) / 10, 1),
    }
    return round(sum(parts.values()), 1), {k: round(v, 1) for k, v in parts.items()}, matched, missing

COURSES = {
    "aws": "AWS Cloud Practitioner (free labs)", "docker": "Docker 101 and containerise one project",
    "sql": "SQL practice: 30 queries on HackerRank", "react": "Build a React CRUD app",
    "machine learning": "Andrew Ng ML course and one Kaggle notebook", "git": "Git and GitHub basics",
}

def explain(p, job, score, parts, matched, missing, reasons):
    if reasons:
        return {"summary": "Not eligible: " + "; ".join(reasons) + ".", "factors": parts,
                "matched": matched, "missing": missing, "suggestions": [], "hidden_gem": False}
    bits = ["CGPA meets the eligibility criteria"]
    if matched:
        bits.append("strong match on " + ", ".join(matched))
    if missing:
        bits.append("the required skill set shows a gap in " + ", ".join(missing))
    if p.mock_score < job.mock_benchmark:
        bits.append(f"the mock-interview score ({p.mock_score}) is below the "
                    f"recruiter benchmark ({job.mock_benchmark})")
    head = "Shortlisted" if score >= 60 else "Waitlist" if score >= 45 else "Below Threshold"
    return {"summary": f"{head}: " + ", and ".join(bits) + ".", "factors": parts,
            "matched": matched, "missing": missing,
            "suggestions": [COURSES.get(m, f"Build a mini-project using {m}") for m in missing],
            "hidden_gem": bool(score >= 60 and float(p.cgpa) < 7.5)}