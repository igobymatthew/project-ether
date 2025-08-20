from .state import SceneState
from . import intents
from .nlg import generate_character_line, pack_plan
from . import agent_builder
import json
from pathlib import Path


class Director:
    def __init__(self, state: SceneState):
        self.state = state

    def _create_agent(self, agent_id: str, vibe: str):
        """Creates a new agent and adds it to the scene."""
        persona = agent_builder.build_persona_from_vibe(agent_id, vibe)

        # Save the persona to a file
        agents_dir = Path("agents")
        agents_dir.mkdir(exist_ok=True)
        persona_path = agents_dir / f"{agent_id}.json"
        with persona_path.open("w", encoding="utf-8") as f:
            json.dump(persona, f, ensure_ascii=False, indent=2)

        # Add the agent to the scene
        if "background" not in self.state.characters:
            self.state.characters["background"] = []
        self.state.characters["background"].append(agent_id)

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

        if intent == "create_agent":
            match = intents.CREATE_AGENT.search(user_text)
            if match:
                # Extract agent name and vibe
                agent_id = match.group(2).lower()
                vibe = user_text[match.end(0) :].strip()

                # Check if agent exists
                persona_path = Path(f"agents/{agent_id}.json")
                if not persona_path.exists():
                    self._create_agent(agent_id, vibe)

                # Handoff to the new or existing agent
                s.stage = "Handoff"
                handoff_prompt = f"The user wants to talk to {agent_id}. Let them know you're getting them."
                line = generate_character_line(s.foreground, handoff_prompt)

                current_speaker = s.foreground
                s.foreground = agent_id

                return pack_plan(
                    current_speaker,
                    line,
                    state=s,
                    handoff_to=agent_id,
                )

        handoff_target = self._find_handoff_target(user_text)
        if handoff_target and s.foreground != handoff_target:
            s.stage = "Handoff"
            handoff_prompt = f"The user wants to talk to {handoff_target}. Let them know you're getting them."
            line = generate_character_line(s.foreground, handoff_prompt)

            current_speaker = s.foreground
            s.foreground = handoff_target

            return pack_plan(
                current_speaker,
                line,
                state=s,
                handoff_to=handoff_target,
            )

        if s.stage in ["Greeting", "Handoff", "ForegroundTalk"]:
            s.stage = "ForegroundTalk"
            line = generate_character_line(s.foreground, user_text)
            return pack_plan(s.foreground, line, state=s)

        # Fallback for any unexpected state.
        return pack_plan(
            s.foreground,
            "We’re here! Can you hear us?",
            state=s,
        )
