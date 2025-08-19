from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pathlib import Path
import json
from .orchestrator.state import SceneState
from .orchestrator.router import Director
from .orchestrator.local_processors import (
    LocalSTTProcessor,
    LocalLLMProcessor,
    LocalTTSProcessor,
)
from chatterbox_tts import ChatterboxTTS
from genai_processors import Pipeline
import torch
import torchaudio
import asyncio
import logging
import whisper

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
app_state = {
    "tts_model": None,
    "tts_ready": False,
    "whisper_model": None,
    "websockets": set(),
}


# --- Model Loading ---
def load_models_sync():
    """Synchronous function to load all models."""
    # Load TTS
    logger.info("Loading TTS model...")
    try:
        app_state["tts_model"] = ChatterboxTTS.from_pretrained(device="cpu")
        app_state["tts_ready"] = True
        logger.info("TTS model loaded successfully.")
    except Exception as e:
        logger.error(f"Could not load ChatterboxTTS model: {e}", exc_info=True)

    # Load Whisper
    logger.info("Loading Whisper model...")
    try:
        # Using "tiny.en" for a smaller footprint, adjust as needed
        app_state["whisper_model"] = whisper.load_model("tiny.en")
        logger.info("Whisper model loaded successfully.")
    except Exception as e:
        logger.error(f"Could not load Whisper model: {e}", exc_info=True)


async def load_models_async():
    """Asynchronous wrapper to run model loading in a thread pool."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, load_models_sync)

    if app_state["tts_ready"]:
        logger.info(f"Broadcasting TTS ready status to {len(app_state['websockets'])} clients.")
        tasks = [
            ws.send_json({"type": "tts_status", "ready": True})
            for ws in app_state["websockets"]
        ]
        await asyncio.gather(*tasks, return_exceptions=True)


@app.on_event("startup")
async def startup_event():
    """On startup, kick off the model loading in the background."""
    logger.info("Application startup...")
    asyncio.create_task(load_models_async())


scene_path = Path("scenes/family_party.yaml")
state = SceneState.from_yaml(scene_path)
director = Director(state, tts_model_getter=lambda: app_state["tts_model"])

@app.get("/")
async def root():
    return HTMLResponse("<h1>Backend OK</h1><p>Connect your frontend to <code>/ws</code>.</p>")

@app.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    app_state["websockets"].add(ws)
    logger.info(f"Client connected. Total clients: {len(app_state['websockets'])}")
    try:
        # Send initial status first
        await ws.send_json({"type": "tts_status", "ready": app_state["tts_ready"]})
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
        logger.info("Client disconnected.")
    finally:
        app_state["websockets"].remove(ws)
        logger.info(f"Client removed. Total clients: {len(app_state['websockets'])}")


@app.websocket("/ws-audio")
async def ws_audio(ws: WebSocket):
    """WebSocket endpoint for bidirectional audio streaming."""
    await ws.accept()
    logger.info("Audio client connected.")

    # 1. Create processor instances
    stt_proc = LocalSTTProcessor(app_state["whisper_model"])
    llm_proc = LocalLLMProcessor()
    tts_proc = LocalTTSProcessor(app_state["tts_model"])

    # 2. Define the pipeline
    pipeline = Pipeline(
        [stt_proc, llm_proc, tts_proc],
        input_queue_maxsize=50,  # Buffer for incoming audio chunks
        output_queue_maxsize=50, # Buffer for outgoing audio chunks
    )

    async def stream_from_client():
        """Task to receive audio from the client and feed it to the pipeline."""
        try:
            while True:
                audio_chunk = await ws.receive_bytes()
                await pipeline.process(audio_chunk)
        except WebSocketDisconnect:
            logger.info("Audio client disconnected (receiver).")
            await pipeline.stop() # Signal pipeline to shut down

    async def stream_to_client():
        """Task to send pipeline output (synthesized audio) back to the client."""
        try:
            async for audio_output in pipeline.output():
                await ws.send_bytes(audio_output)
            logger.info("Finished sending audio back to client.")
        except WebSocketDisconnect:
            logger.info("Audio client disconnected (sender).")


    # 3. Run the pipeline and I/O tasks concurrently
    try:
        # Start the pipeline processing in the background
        pipeline_task = asyncio.create_task(pipeline.run())
        # Start client I/O tasks
        receiver_task = asyncio.create_task(stream_from_client())
        sender_task = asyncio.create_task(stream_to_client())

        # Wait for all tasks to complete
        await asyncio.gather(pipeline_task, receiver_task, sender_task)

    except Exception as e:
        logger.error(f"Error in audio pipeline: {e}", exc_info=True)
    finally:
        logger.info("Audio client connection closed.")
