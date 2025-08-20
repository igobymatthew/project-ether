# orchestrator/scheduler.py
def on_user_transcript(text):
    intent = nlu.parse(text)  # “ask_for_brother”, “greeting”, “goodbye”, etc.
    if state.stage == "ForegroundTalk" and intent == "ask_for_brother":
        return director.plan_handoff(from_="mother", to_="brother")

def tick():
    # Runs every ~100ms
    next_bg_event = director.maybe_emit_background(state)
    if next_bg_event:
        queue_audio(next_bg_event)
