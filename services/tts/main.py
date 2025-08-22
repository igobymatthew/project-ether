from fastapi import FastAPI, Response, Query
from pydantic import BaseModel
import os, io, math, struct
import numpy as np

app = FastAPI()
BACKEND = os.getenv("TTS_BACKEND", "fallback")  # fallback | browser | chatterbox (future)

class TTSIn(BaseModel):
    text: str
    voice: str | None = None

@app.get("/health")
def health():
    return {"ok": True, "backend": BACKEND}

def _fallback_wav_bytes(text: str, sr: int = 22050) -> bytes:
    dur = min(2.0 + 0.025 * len(text or "test"), 6.0)
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    sig = 0.25*np.sin(2*math.pi*190*t) + 0.18*np.sin(2*math.pi*310*t) + 0.03*np.random.randn(len(t))
    env_head = np.linspace(0.2, 1.0, int(0.05*sr))
    env_tail = np.linspace(1.0, 0.0, int(0.08*sr))
    a = np.ones_like(sig)
    a[:env_head.size] = env_head
    a[-env_tail.size:] = np.minimum(a[-env_tail.size:], env_tail)
    sig = (sig * a * 0.6).astype(np.float32)

    pcm = (sig * 32767).astype(np.int16).tobytes()
    data_size = len(pcm)
    buf = io.BytesIO()
    buf.write(b"RIFF")
    buf.write(struct.pack("<I", 36 + data_size))
    buf.write(b"WAVEfmt ")
    buf.write(struct.pack("<IHHIIHH", 16, 1, 1, sr, sr*2, 2, 16))
    buf.write(b"data")
    buf.write(struct.pack("<I", data_size))
    buf.write(pcm)
    return buf.getvalue()

@app.post("/tts")
def tts(body: TTSIn):
    # Future: branch on BACKEND == 'chatterbox' to synth real speech
    wav = _fallback_wav_bytes(body.text)
    return Response(content=wav, media_type="audio/wav")

@app.get("/tts_stream")
def tts_stream(text: str = Query(""), voice: str | None = None):
    # Simple non-chunked fallback (still works for browsers)
    wav = _fallback_wav_bytes(text)
    return Response(content=wav, media_type="audio/wav")
