import os, sys, pathlib, uvicorn, site
ROOT = pathlib.Path(__file__).resolve().parents[1]
API_SITE = ROOT / "vendor" / "api_site"
site.addsitedir(str(API_SITE))
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
os.environ.setdefault("ETHER_LLM_MODEL", str(ROOT / "models" / "llama-7b.Q4_K_M.gguf"))
uvicorn.run("app.api.main.main:app", host="0.0.0.0", port=8000, reload=False)
