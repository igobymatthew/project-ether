from .state import SceneState
from . import intents
from .nlg import generate_character_line, pack_plan


class Director:
    def __init__(self, state: SceneState, tts_model_getter=None):
        self.state = state
        self.tts_model_getter = tts_model_getter

    def _find_handoff_target(self, user_text: str) -> str | None:
        """Checks if the user's text triggers a handoff defined in the scene."""
        s = self.state
        if not hasattr(s, 'handoff_triggers') or not isinstance(s.handoff_triggers, list):
            return None

        for trigger in s.handoff_triggers:
            if "from" in trigger and "to" in trigger and "when_user_mentions" in trigger:
                if s.foreground == trigger["from"] and any(
                    keyword.lower() in user_text.lower() for keyword in trigger["when_user_mentions"]
                ):
                    return trigger["to"]
        return None

    def step(self, user_text: str):
        s = self.state
        s.last_user_text = user_text or ""

        intent = intents.classify(user_text)
        if intent == "end_call":
            return {"controls": {"end_call": True}}

        handoff_target = self._find_handoff_target(user_text)
        if handoff_target and s.foreground != handoff_target:
            s.stage = "Handoff"
            handoff_prompt = f"The user wants to talk to {handoff_target}. Let them know you're getting them."
            line = generate_character_line(s.foreground, handoff_prompt)

            current_speaker = s.foreground
            s.foreground = handoff_target

            tts_model = self.tts_model_getter() if self.tts_model_getter else None
            return pack_plan(
                current_speaker,
                line,
                state=s,
                handoff_to=handoff_target,
                tts_model=tts_model
            )

        if s.stage in ["Greeting", "Handoff", "ForegroundTalk"]:
            s.stage = "ForegroundTalk"
            line = generate_character_line(s.foreground, user_text)
            tts_model = self.tts_model_getter() if self.tts_model_getter else None
            return pack_plan(s.foreground, line, state=s, tts_model=tts_model)

        # Fallback for any unexpected state.
        tts_model = self.tts_model_getter() if self.tts_model_getter else None
        return pack_plan(
            s.foreground,
            "We’re here! Can you hear us?",
            state=s,
            tts_model=tts_model
        )
