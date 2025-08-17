from .state import SceneState
from . import intents
from .nlg import mother_line, brother_line, pack_plan

class Director:
    def __init__(self, state: SceneState, tts_model=None):
        self.state = state
        self.tts_model = tts_model
        self._did_mom_eat_check = False

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
            line = mother_line(user_text)
            self._did_mom_eat_check = "Are you eating ok?" in line
            return pack_plan("mother", line, tts_model=self.tts_model)

        # handoff ask
        if intent == "ask_brother" and s.foreground != "brother":
            s.stage = "Handoff"
            s.foreground = "brother"
            return pack_plan("mother", "Just a sec, I’ll grab your brother. Love you—are you eating ok?", handoff_to="brother", tts_model=self.tts_model)

        # after handoff: brother speaks
        if s.stage == "Handoff" and s.foreground == "brother":
            s.stage = "ForegroundTalk"
            return pack_plan("brother", brother_line(user_text), tts_model=self.tts_model)

        # default foreground responses
        if s.foreground == "mother":
            if not self._did_mom_eat_check:
                self._did_mom_eat_check = True
                return pack_plan("mother", "Love you—are you eating ok?", tts_model=self.tts_model)
            return pack_plan("mother", mother_line(user_text), tts_model=self.tts_model)

        if s.foreground == "brother":
            return pack_plan("brother", brother_line(user_text), tts_model=self.tts_model)

        # fallback
        return {"foreground":{"speaker":"mother","line":"We’re here! Can you hear us?"}, "background":[], "controls":{"ducking_db":-14,"overlap_ms":350,"handoff_to":"none"}}
