import os, sys, pathlib, uvicorn, site
ROOT = pathlib.Path(__file__).resolve().parents[1]
TTS_SITE = ROOT / "vendor" / "tts_site"
site.addsitedir(str(TTS_SITE))
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
# Optional: set backend choice (fallback | chatterbox)
os.environ.setdefault("TTS_BACKEND", "chatterbox")
uvicorn.run("app.api.tts.main:app", host="0.0.0.0", port=8010, reload=False)
