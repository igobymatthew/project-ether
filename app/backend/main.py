from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pathlib import Path
import json
from .orchestrator.state import SceneState
from .orchestrator.router import Director
from chatterbox.tts import ChatterboxTTS
import torch
import torchaudio
import asyncio
import logging

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("tts_loader.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- Application State ---
app_state = {"tts_model": None}

# --- TTS Model Loading ---
def load_tts_model_sync():
    """Synchronous function to load the TTS model."""
    logger.info("Loading TTS model in background...")
    try:
        model = ChatterboxTTS.from_pretrained(device="cpu")
        app_state["tts_model"] = model
        logger.info("TTS model loaded successfully.")
    except Exception as e:
        logger.error(f"Could not load ChatterboxTTS model: {e}", exc_info=True)

async def load_tts_model_async():
    """Asynchronous wrapper to run the synchronous model loading in a thread pool."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, load_tts_model_sync)

@app.on_event("startup")
async def startup_event():
    """On startup, kick off the model loading in the background."""
    logger.info("Application startup...")
    asyncio.create_task(load_tts_model_async())


scene_path = Path("scenes/family_party.yaml")
state = SceneState.from_yaml(scene_path)
director = Director(state, tts_model_getter=lambda: app_state["tts_model"])

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
