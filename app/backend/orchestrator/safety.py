def sanitize(text: str) -> str:
    # minimal PG-13 scrub (soften a few common words)
    bad = {"damn":"darn", "shit":"shoot", "ass":"butt"}
    words = text.split()
    return " ".join(bad.get(w.lower(), w) for w in words)
