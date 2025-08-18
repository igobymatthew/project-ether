from .state import SceneState
from . import intents
from .nlg import generate_character_line, pack_plan

class Director:
    def __init__(self, state: SceneState, tts_model=None):
        self.state = state
        self.tts_model = tts_model
        self._did_mom_eat_check = False # This logic can be removed or refactored if the LLM handles it.

    def step(self, user_text: str):
        s = self.state
        s.last_user_text = user_text or ""

        intent = intents.classify(user_text)
        if intent == "end_call":
            return {"controls": {"end_call": True}}

        # greet flow
        if s.stage == "Greeting":
            s.stage = "ForegroundTalk"
            s.foreground = "mother"
            # The first line is often scripted, but can also be dynamic.
            # For now, we keep the original greeting for consistency.
            line = "Oh honey! Glad you called—hang on—Jared, feet off—love you. Are you eating ok?"
            self._did_mom_eat_check = "Are you eating ok?" in line
            return pack_plan(s.foreground, line, tts_model=self.tts_model)

        # handoff ask
        if intent == "ask_brother" and s.foreground != "brother":
            s.stage = "Handoff"
            # The handoff line can also be generated dynamically or kept scripted.
            # Let's keep it scripted for reliability.
            handoff_line = "Just a sec, I’ll grab your brother. Love you—are you eating ok?"
            current_speaker = s.foreground
            s.foreground = "brother" # The state now anticipates the brother.
            return pack_plan(current_speaker, handoff_line, handoff_to="brother", tts_model=self.tts_model)

        # after handoff: new character speaks
        if s.stage == "Handoff":
            s.stage = "ForegroundTalk"
            # The new speaker generates a response to the original user text.
            line = generate_character_line(s.foreground, user_text)
            return pack_plan(s.foreground, line, tts_model=self.tts_model)

        # default foreground responses
        if s.foreground in ["mother", "brother", "uncle", "kid"]: # Check against all possible speakers
            # The main logic change: use the generic generator for any character.
            line = generate_character_line(s.foreground, user_text)
            return pack_plan(s.foreground, line, tts_model=self.tts_model)

        # fallback
        return pack_plan("mother", "We’re here! Can you hear us?", tts_model=self.tts_model)
