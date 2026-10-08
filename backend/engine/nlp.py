import re
import spacy
from spacy.matcher import PhraseMatcher
from sentence_transformers import SentenceTransformer

SKILLS = {
    "python": ["python"], "java": ["java", "core java"],
    "javascript": ["javascript", "js", "es6"], "react": ["react", "reactjs", "react.js"],
    "django": ["django", "drf"], "node": ["node", "nodejs"],
    "sql": ["sql", "mysql", "postgresql", "rdbms"],
    "rest api": ["rest api", "restful", "api development"],
    "git": ["git", "github"], "docker": ["docker", "containers"],
    "aws": ["aws", "amazon web services", "ec2"], "cloud": ["cloud", "azure", "gcp"],
    "machine learning": ["machine learning", "ml", "scikit-learn"],
    "nlp": ["nlp", "natural language processing"],
    "data structures": ["data structures", "dsa", "algorithms"],
    "html/css": ["html", "css", "tailwind"],
    "communication": ["communication", "presentation"],
    "linux": ["linux", "bash"], "testing": ["testing", "unit test", "pytest"],
    "excel": ["excel", "power bi"],
}
_nlp = spacy.load("en_core_web_sm", disable=["ner", "parser", "lemmatizer"])
_matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")
for canon, aliases in SKILLS.items():
    _matcher.add(canon, [_nlp.make_doc(a) for a in aliases])
def extract_skills(text):
    doc = _nlp.make_doc(text or "")
    return sorted({_nlp.vocab.strings[mid] for mid, _, _ in _matcher(doc)})

BRANCHES = {"CSE": ["cse", "computer science"], "IT": ["information technology"],
            "ECE": ["ece", "electronics"], "EEE": ["eee", "electrical"],
            "ME": ["mechanical"], "CE": ["civil"]}

def parse_jd(text):
    t = (text or "").lower()
    out = {"required_skills": extract_skills(text)}
    m = re.search(r"(?:cgpa|gpa)[^0-9]{0,25}(\d(?:\.\d+)?)", t)
    if m:
        out["min_cgpa"] = float(m.group(1))
    b = re.search(r"backlogs?[^0-9]{0,20}(\d)", t)
    if b:
        out["max_backlogs"] = int(b.group(1))
    if "no backlog" in t or "zero backlog" in t:
        out["max_backlogs"] = 0
    br = [k for k, al in BRANCHES.items() if any(re.search(rf"\b{a}\b", t) for a in al)]
    if br:
        out["allowed_branches"] = br
    return out
_model = None
def embed(texts):
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model.encode(texts, convert_to_tensor=True, normalize_embeddings=True)