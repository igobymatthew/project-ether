from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any
import yaml

@dataclass
class SceneState:
    scene_id: str
    title: str
    roomtone: str
    walla_beds: List[str]
    intensity: float
    characters: Dict[str, List[str]]
    rules: Dict[str, Any]
    timing: Dict[str, Any]
    overlap: Dict[str, Any]
    ducking_db: int
    tts: Dict[str, Any]
    background_asides: List[Dict[str, Any]]
    safety: Dict[str, Any]
    stop_words: List[str]
    # runtime
    stage: str = "Greeting"
    foreground: str = "mother"
    last_user_text: str = ""
    memory: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path):
        with open(path, "r", encoding="utf-8") as f:
            y = yaml.safe_load(f)
        return cls(
            scene_id=y["scene_id"],
            title=y.get("title", y["scene_id"]),
            roomtone=y.get("roomtone",""),
            walla_beds=y.get("walla_beds",[]),
            intensity=float(y.get("intensity",0.5)),
            characters=y.get("characters",{}),
            rules=y.get("rules",{}),
            timing=y.get("timing",{}),
            overlap=y.get("overlap",{}),
            ducking_db=int(y.get("ducking_db",-14)),
            tts=y.get("tts",{}),
            background_asides=y.get("background_asides",[]),
            safety=y.get("safety",{}),
            stop_words=y.get("stop_words",["end call"])
        )
