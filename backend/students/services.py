from engine.scoring import readiness

def refresh_readiness(p):
    p.readiness_score, p.readiness_level, parts = readiness(p)
    p.save(update_fields=["readiness_score", "readiness_level", "updated_at"])
    return parts