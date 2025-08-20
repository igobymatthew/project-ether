from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from chatterbox_tts import ChatterboxTTS
import torch
import io
import logging

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("tts_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- Application State ---
app_state = {
    "tts_model": None,
}

# --- Model Loading ---
@app.on_event("startup")
async def startup_event():
    """On startup, load the TTS model."""
    logger.info("TTS service starting up...")
    try:
        app_state["tts_model"] = ChatterboxTTS.from_pretrained(device="cpu")
        logger.info("TTS model loaded successfully.")
    except Exception as e:
        logger.error(f"Could not load ChatterboxTTS model: {e}", exc_info=True)
        # We might want to prevent the app from starting if the model fails to load
        # For now, we'll log the error and continue.
        app_state["tts_model"] = None


class SynthesizeRequest(BaseModel):
    text: str

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/synthesize")
async def synthesize(request: SynthesizeRequest):
    """
    Synthesizes audio from text using the loaded ChatterboxTTS model.
    """
    if app_state["tts_model"] is None:
        raise HTTPException(status_code=503, detail="TTS model is not available.")

    try:
        logger.info(f"Synthesizing text: {request.text}")
        wav = app_state["tts_model"].generate(request.text)

        if wav is None:
            raise HTTPException(status_code=500, detail="TTS model failed to generate audio.")

        # Convert tensor to bytes
        wav_tensor = (wav * 32767).to(torch.int16).cpu()
        audio_bytes = wav_tensor.numpy().tobytes()

        # It's better to stream the response
        return StreamingResponse(io.BytesIO(audio_bytes), media_type="application/octet-stream")

    except Exception as e:
        logger.error(f"Error during TTS synthesis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred during synthesis.")
