#!/usr/bin/env python3
"""
make_agents.py
Generate agent persona JSON files and core prompt files from agents/_scaffold.yaml.

Usage:
  python scripts/make_agents.py                      # default paths
  python scripts/make_agents.py --force              # overwrite existing
  python scripts/make_agents.py --scaffold agents/_scaffold.yaml --out-agents agents --out-prompts prompts
"""

from __future__ import annotations
import argparse, json, os, sys, textwrap
from pathlib import Path

try:
    import yaml
except ImportError as e:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    raise

# ---------- Defaults ----------
DEFAULT_SCAFFOLD = Path("agents/_scaffold.yaml")
DEFAULT_AGENTS_DIR = Path("agents")
DEFAULT_PROMPTS_DIR = Path("prompts")
DEFAULT_SCENES_DIR = Path("scenes")

# ---------- Prompt templates (from previous message) ----------
DIRECTOR_PROMPT = """You are the Scene Director for a simulated family group call.

**Objectives**
- Natural handoffs, light overlaps (≤600ms), warm tone, PG‑13.
- Obey scene rules: must‑hit lines and handoff triggers.
- Keep *one* foreground speaker; others may do brief, short asides.

**Handoff plan when user asks for someone**
1) Foreground filler by current speaker (≤3s).
2) Brief off‑mic background shout to target.
3) New speaker entrance within 4–8 seconds.

**Output JSON only**
{
  "foreground": {"speaker": "<id>", "line": "<speakable text ≤7s>", "aside": "<optional short>"},
  "background": [{"speaker":"<id>","line":"<very short>","proximity":"near|far"}],
  "controls": {"ducking_db": -14, "overlap_ms": 350, "handoff_to": "<id|none>"}
}

Constraints: natural, affectionate, no advice, no real‑world claims about the user. Keep lines short and speakable. If user says a stop word, return {"controls":{"end_call":true}}.
""".rstrip() + "\n"

CHARACTER_PROMPT = """You are <mother|brother|uncle|kid>. Stay strictly in persona.

Style: contractions, short sentences, casual, warm, PG‑13, minimal filler. No politics or advice. Use universal, low‑stakes details only. For handoffs, include a brief affectionate line if appropriate. Return plain text ≤7 seconds. If asked for someone else, acknowledge and keep it short.
""".rstrip() + "\n"

# ---------- Helpers ----------

def slurp_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def write_text(path: Path, content: str, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True

def write_json(path: Path, obj: dict, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return True

def archetype_from_vibe(vibe: str, pid: str) -> str:
    # light mapping with tasteful defaults
    vibe = (vibe or "").lower()
    if "mom" in pid or "mother" in pid:
        return "warm, slightly nosy Midwestern mom"
    if "brother" in pid:
        return "rowdy but loving older brother"
    if "uncle" in pid:
        return "dad‑jokey relative with sports takes"
    if "kid" in pid:
        return "excited kid with short attention span"
    # fallback: capitalize vibe
    return vibe if vibe else "casual, friendly acquaintance"

def default_style_for(pid: str) -> dict:
    if "mother" in pid:
        return {"politeness": "high", "pace": "medium", "asides": "gentle"}
    if "brother" in pid:
        return {"politeness": "casual", "pace": "fast", "asides": "blurted"}
    if "uncle" in pid:
        return {"politeness": "casual", "pace": "medium", "asides": "muttered"}
    if "kid" in pid:
        return {"politeness": "casual", "pace": "fast", "asides": "excited"}
    return {"politeness": "casual", "pace": "medium", "asides": "light"}

def default_smalltalk(pid: str) -> list[str]:
    if "mother" in pid:
        return ["How’s work treating you?", "Did you get enough sleep?", "I found that casserole recipe you liked."]
    if "brother" in pid:
        return ["You still lifting or just lifting snacks?", "You catch the game?", "I’m making wings—don’t judge me."]
    if "uncle" in pid:
        return ["How 'bout them Lions?", "Anyone want more chips?", "This remote is haunted."]
    if "kid" in pid:
        return ["Where’s the charger?", "Can I show you something?", "I didn’t touch it!"]
    return ["How’s your week?", "All good on your end?"]

def entrance_for(pid: str, anchors: list[str]) -> str:
    if "mother" in pid:
        return "Oh hi, sweetie! We’ve got everyone here—Jared, not on the cushions—okay, I’m back."
    if "brother" in pid:
        return "Broham, what it be?!—hey, put that down—sorry, okay I’m here."
    # generic entrance referencing first anchor if exists
    a = anchors[0] if anchors else "hey!"
    return f"{a}—okay, I’m here."

def handoff_line_for(pid: str, anchors: list[str]) -> str:
    if "mother" in pid:
        return "Just a sec, I’ll grab your brother. Love you—are you eating ok?"
    if "brother" in pid:
        return "Ma! He’s on—okay, I got it. So what’s good?"
    return "One sec, I’ll grab them for you."

def build_persona(p: dict) -> dict:
    pid = p.get("id", "unknown").strip()
    vibe = p.get("vibe", "")
    anchors = p.get("anchors", []) or []
    nicknames = p.get("nicknames", []) or []

    persona = {
        "id": pid,
        "archetype": archetype_from_vibe(vibe, pid),
        "signature": anchors[:4],
        "style": default_style_for(pid),
        "boundaries": ["no politics", "no medical or financial advice", "PG-13 only"],
        "relationship": {"to_user": "their adult child", "nicknames": nicknames},
        "entrances": [entrance_for(pid, anchors)],
        "handoff_lines": [handoff_line_for(pid, anchors)],
        "smalltalk": default_smalltalk(pid),
        "goodbyes": [
            "Okay, love you, talk soon.",
            "Alright, I’ll let you go. Eat something real, okay?"
        ]
    }
    # Relationship tweak for brother style
    if "brother" in pid:
        persona["relationship"] = {"to_user": "younger sibling", "nicknames": nicknames or ["broham"]}
    return persona

def maybe_write_default_scene(scenes_dir: Path, force: bool):
    path = scenes_dir / "family_party.yaml"
    if path.exists() and not force:
        return False
    content = textwrap.dedent("""\
    scene_id: family_party
    title: "Family Call: Living Room Chaos"
    roomtone: "sfx/roomtone_livingroom.wav"
    walla_beds:
      - "sfx/walla_family_casual_1.wav"
      - "sfx/cutlery_clink_1.wav"
      - "sfx/kids_scatter_1.wav"
    intensity: 0.6
    characters:
      foreground: ["mother"]
      nearby: ["brother"]
      background: ["uncle", "kid", "cousin"]
    rules:
      must_hit_lines:
        - character: mother
          line_hint: "Are you eating ok?"
          within_seconds: 90
      handoff_triggers:
        - when_user_mentions: ["brother", "can I talk to", "hand me to", "put him on"]
          from: "mother"
          to: "brother"
    timing:
      handoff_min_s: 4
      handoff_max_s: 8
    overlap:
      max_ms: 600
    ducking_db: -14
    tts:
      voice_map:
        mother: "voice_mom_a"
        brother: "voice_bro_b"
        uncle: "voice_uncle_c"
        kid: "voice_kid_d"
    background_asides:
      - speaker: "uncle"
        lines: ["(muffled) save me a plate!", "(far) who moved my hat?"]
      - speaker: "kid"
        lines: ["Mom! Where’s the charger?", "I didn’t touch it!"]
      - speaker: "cousin"
        lines: ["You calling? Tell them hi!", "Wait—smile for the thing!"]
    safety:
      pg13: true
      blocked_topics: ["politics", "medical advice", "financial advice", "slurs"]
    stop_words: ["end call", "stop", "too loud"]
    """)
    return write_text(path, content, force)

# ---------- Main ----------

def main():
    ap = argparse.ArgumentParser(description="Generate agent files and prompts from _scaffold.yaml")
    ap.add_argument("--scaffold", type=Path, default=DEFAULT_SCAFFOLD)
    ap.add_argument("--out-agents", type=Path, default=DEFAULT_AGENTS_DIR)
    ap.add_argument("--out-prompts", type=Path, default=DEFAULT_PROMPTS_DIR)
    ap.add_argument("--out-scenes", type=Path, default=DEFAULT_SCENES_DIR)
    ap.add_argument("--no-scene", action="store_true", help="Do not create default scene file")
    ap.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = ap.parse_args()

    if not args.scaffold.exists():
        print(f"ERROR: scaffold not found: {args.scaffold}", file=sys.stderr)
        sys.exit(1)

    data = slurp_yaml(args.scaffold)
    personas = data.get("personas", [])
    if not personas:
        print("ERROR: No 'personas' in scaffold.", file=sys.stderr)
        sys.exit(1)

    ensure_dir(args.out_agents)
    ensure_dir(args.out_prompts)
    ensure_dir(args.out_scenes)

    # Write prompts
    wrote_dp = write_text(args.out_prompts / "director.system.md", DIRECTOR_PROMPT, args.force)
    wrote_cp = write_text(args.out_prompts / "character.system.md", CHARACTER_PROMPT, args.force)

    # Write personas
    written = []
    skipped = []
    for p in personas:
        pid = p.get("id", "").strip()
        if not pid:
            print("WARNING: Skipping persona with missing id", file=sys.stderr)
            continue
        persona = build_persona(p)
        out_path = args.out_agents / f"{pid}.json"
        ok = write_json(out_path, persona, args.force)
        (written if ok else skipped).append(str(out_path))

    # Optional default scene
    wrote_scene = False
    if not args.no_scene:
        wrote_scene = maybe_write_default_scene(args.out_scenes, args.force)

    # Summary
    print("\n=== make_agents summary ===")
    print(f"Scaffold:  {args.scaffold}")
    print(f"Agents ->  {args.out_agents}")
    for p in written:
        print(f"  [+] wrote {p}")
    for p in skipped:
        print(f"  [=] exists (skip) {p}")
    print(f"Prompts -> {args.out_prompts}")
    print(f"  {'[+]' if wrote_dp else '[=]'} director.system.md")
    print(f"  {'[+]' if wrote_cp else '[=]'} character.system.md")
    if not args.no_scene:
        print(f"Scenes  -> {args.out_scenes}")
        print(f"  {'[+]' if wrote_scene else '[=]'} family_party.yaml")
    print("Done.\n")

if __name__ == "__main__":
    main()
