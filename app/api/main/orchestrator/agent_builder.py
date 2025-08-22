"""
Agent Builder
Dynamically constructs agent personas from a high-level "vibe."
"""
from __future__ import annotations
from app.api.main.llm.gemini import Gemini
import json
import os

llm_connector = None

def get_llm_connector():
    global llm_connector
    if llm_connector is None:
        # In a real app, you'd get the model and api_key from config
        llm_connector = Gemini(model="models/gemini-1.5-flash-latest", api_key=os.environ.get("GEMINI_API_KEY", "DUMMY"))
    return llm_connector

def generate_persona_details_from_vibe(vibe: str) -> dict:
    """
    Generates persona details from a vibe string using an LLM.
    """
    system_prompt = f"""
You are a creative writer. Your task is to generate a detailed character persona based on a short "vibe" description.
The user will provide a vibe, and you must return a JSON object with the following keys: "archetype", "smalltalk", "nicknames", "entrances", and "handoff_lines".

Example vibe: "a grumpy old man who loves to complain about the weather"
Example output:
{{
  "archetype": "a grumpy old man who loves to complain about the weather",
  "smalltalk": ["Here we go with the rain again.", "My joints are aching, must be a storm coming.", "They just don't make weather like they used to."],
  "nicknames": ["old timer", "grumpy"],
  "entrances": ["Alright, what's all this racket?", "Don't mind me, just here to complain."],
  "handoff_lines": ["Fine, I'll go get them. Don't expect me to be happy about it.", "Yeah, yeah, I'm going."]
}}

Now, generate the persona for the following vibe.
Vibe: "{vibe}"
"""
    response = get_llm_connector().generate_response(
        system_prompt=system_prompt,
        user_prompt=vibe
    )
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Fallback if the LLM response is not valid JSON
        return {{
            "archetype": vibe,
            "smalltalk": ["How's it going?"],
            "nicknames": [],
            "entrances": ["Hey, I'm here."],
            "handoff_lines": ["One second, I'll go get them."]
        }}


def build_persona_from_vibe(pid: str, vibe: str) -> dict:
    """
    Builds a persona from a vibe string.
    """
    details = generate_persona_details_from_vibe(vibe)

    persona = {
        "id": pid,
        "archetype": details.get("archetype", vibe),
        "signature": [], # Not clear how to generate this, so I'll leave it empty
        "style": {"politeness": "casual", "pace": "medium", "asides": "light"}, # default style
        "boundaries": ["no politics", "no medical or financial advice", "PG-13 only"],
        "relationship": {"to_user": "acquaintance", "nicknames": details.get("nicknames", [])},
        "entrances": details.get("entrances", ["Hey, I'm here."]),
        "handoff_lines": details.get("handoff_lines", ["One second."]),
        "smalltalk": details.get("smalltalk", ["How's it going?"]),
        "goodbyes": [
            "Okay, talk soon.",
            "Alright, I’ll let you go."
        ]
    }
    return persona
