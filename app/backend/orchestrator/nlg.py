from .safety import sanitize
import torchaudio
import uuid
from pathlib import Path

# --- Audio Generation ---
# This is where we'll create and save the audio files.
# The frontend will need to be able to access this directory.
AUDIO_DIR = Path("app/frontend/assets/gen-audio")
AUDIO_DIR.mkdir(exist_ok=True)

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

def pack_plan(fore_speaker: str, line: str, tts_model=None, handoff_to: str|None=None, duck_db=-14):
    sanitized_line = sanitize(line)

    if tts_model:
        try:
            wav = tts_model.generate(sanitized_line)
            filename = f"{uuid.uuid4()}.wav"
            filepath = AUDIO_DIR / filename
            torchaudio.save(filepath, wav, tts_model.sr)
            # The line becomes the URL to the audio file
            line_content = f"assets/gen-audio/{filename}"
        except Exception as e:
            print(f"ERROR: TTS generation failed: {e}")
            # Fallback to sending text if TTS fails
            line_content = sanitized_line
    else:
        # If no TTS model, just send the text
        line_content = sanitized_line

    return {
        "foreground": {"speaker": fore_speaker, "line": line_content, "transcript": sanitized_line},
        "background": aside_lines(),
        "controls": {"ducking_db": duck_db, "overlap_ms": 350, "handoff_to": handoff_to or "none"}
    }
