from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pathlib import Path
import json
from .orchestrator.state import SceneState
from .orchestrator.router import Director

app = FastAPI()
scene_path = Path("scenes/family_party.yaml")
state = SceneState.from_yaml(scene_path)
director = Director(state)

@app.get("/")
async def root():
    return HTMLResponse("<h1>Backend OK</h1><p>Connect your frontend to <code>/ws</code>.</p>")

@app.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    try:
        await ws.send_json({"type": "hello", "scene_id": state.scene_id, "title": state.title})
        while True:
            msg = await ws.receive_text()
            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                continue

            if data.get("type") == "user_transcript":
                user_text = data.get("text", "")
                plan = director.step(user_text)
                await ws.send_json({"type": "plan", "data": plan})
            elif data.get("type") == "set_bg_energy":
                state.intensity = float(data.get("value", state.intensity))
                await ws.send_json({"type": "ack", "ok": True})
            elif data.get("type") == "end_call":
                await ws.send_json({"type": "plan", "data": {"controls": {"end_call": True}}})
                break
    except WebSocketDisconnect:
        pass
