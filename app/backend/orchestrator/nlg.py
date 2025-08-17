from .safety import sanitize

def mother_line(user_text: str) -> str:
    t = user_text.lower()
    if "eat" in t or "food" in t:
        return "I’ll make you leftovers. Love you."
    # default warmth + required beat baked in early
    return "Oh honey! Glad you called—hang on—Jared, feet off—love you. Are you eating ok?"

def brother_line(user_text: str) -> str:
    t = user_text.lower()
    if "how are you" in t or "what's up" in t or "whats up" in t:
        return "Broham, what it be?! I’m good—hey put that down—okay, talk to me."
    return "Broham, what it be?!—hey put that down—where’s Mom at? Okay, I’m here."

def aside_lines() -> list[dict]:
    return [
        {"speaker":"uncle","line":"(far) save me a plate!","proximity":"far"},
        {"speaker":"kid","line":"Where’s the charger?","proximity":"near"}
    ]

def pack_plan(fore_speaker: str, line: str, handoff_to: str|None=None, duck_db=-14):
    return {
        "foreground": {"speaker": fore_speaker, "line": sanitize(line)},
        "background": aside_lines(),
        "controls": {"ducking_db": duck_db, "overlap_ms": 350, "handoff_to": handoff_to or "none"}
    }
