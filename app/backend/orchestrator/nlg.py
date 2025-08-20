import json
from pathlib import Path
import random
import uuid

from app.backend.llm import llm_connector
from .safety import sanitize
from .state import SceneState

# Directory for storing generated audio files, accessible by the frontend.
AUDIO_DIR = Path("app/frontend/assets/gen-audio")
AUDIO_DIR.mkdir(exist_ok=True)

def _build_system_prompt(persona: dict) -> str:
    """
    Constructs a detailed system prompt from a character's persona dictionary
    to guide the LLM's responses and maintain character consistency.
    """
    style = persona.get("style", {})
    relationship = persona.get("relationship", {})

    # Craft a detailed prompt that defines the character's personality, style, and rules.
    prompt = (
        f"You are a character in a simulated family group call. "
        f"Your persona is: {persona.get('archetype', 'a friendly person')}.\n"
        f"Your speaking style is {style.get('pace', 'medium')} paced and {style.get('politeness', 'casually')} polite.\n"
        f"You are talking to {relationship.get('to_user', 'someone you know well')}, who you call {relationship.get('nicknames', ['pal'])[0]}.\n"
        f"A few things you might say are: \"{', '.join(persona.get('smalltalk', []))}\".\n\n"
        f"**RULES:**\n"
        f"1. Respond naturally to the user's last message: \"{{user_text}}\".\n"
        f"2. Keep your entire response to one or two short, speakable sentences.\n"
        f"3. DO NOT use asterisks, emojis, or formatting.\n"
        f"4. Stay strictly in character. Do not reveal you are an AI."
    )
    return prompt

def generate_character_line(character_id: str, user_text: str) -> str:
    """
    Generates a dynamic, in-character line using the configured LLM.
    """
    persona_path = Path(f"agents/{character_id}.json")
    if not persona_path.exists():
        print(f"WARNING: No persona file found for character '{character_id}'.")
        return "Uh, who is this?"

    try:
        with persona_path.open("r", encoding="utf-8") as f:
            persona = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"ERROR: Could not read or parse persona for '{character_id}'. Details: {e}")
        return "I'm not feeling like myself right now."

    # Build the prompt and get a dynamic response from the LLM.
    system_prompt = _build_system_prompt(persona).format(user_text=user_text)

    generated_line = llm_connector.generate_response(
        system_prompt=system_prompt,
        user_prompt=user_text  # Pass user_text again for models that use it separately
    )
    return generated_line

def aside_lines(state: SceneState) -> list[dict]:
    """Pulls a random subset of background chatter from the current scene state."""
    if not hasattr(state, 'background_asides') or not state.background_asides:
        return []

    max_asides = min(len(state.background_asides), 2)
    num_to_play = random.randint(0, max_asides)

    if num_to_play == 0:
        return []

    all_possible_lines = []
    for aside_group in state.background_asides:
        speaker = aside_group.get("speaker")
        if speaker:
            for line in aside_group.get("lines", []):
                all_possible_lines.append({"speaker": speaker, "line": line})

    if not all_possible_lines:
        return []

    return random.sample(all_possible_lines, min(num_to_play, len(all_possible_lines)))


import requests

def pack_plan(
    fore_speaker: str,
    line: str,
    state: SceneState,
    handoff_to: str | None = None
):
    """
    Packages the generated line and other data into the final JSON plan
    that the frontend will execute. This includes generating the TTS audio.
    """
    sanitized_line = sanitize(line)

    try:
        response = requests.post("http://localhost:8081/tts", json={"text": sanitized_line})
        response.raise_for_status()  # Raise an exception for bad status codes

        filename = f"{uuid.uuid4()}.wav"
        filepath = AUDIO_DIR / filename
        with open(filepath, "wb") as f:
            f.write(response.content)

        line_content = f"assets/gen-audio/{filename}"
    except requests.exceptions.RequestException as e:
        print(f"ERROR: TTS request failed: {e}")
        line_content = sanitized_line

    duck_db = getattr(state, 'ducking_db', -14)
    overlap_ms = getattr(state, 'overlap', {}).get('max_ms', 350)

    return {
        "foreground": {"speaker": fore_speaker, "line": line_content, "transcript": sanitized_line},
        "background": aside_lines(state),
        "controls": {"ducking_db": duck_db, "overlap_ms": overlap_ms, "handoff_to": handoff_to or "none"}
    }
