# server/app/config.py
from pathlib import Path
import os

APP_ROOT = Path(__file__).resolve().parents[1]
KEYS_DIR = APP_ROOT / "keys"
KEYS_DIR.mkdir(parents=True, exist_ok=True)

# JWT settings (in prod, put SECRET_KEY in env/secret manager)
SECRET_KEY = os.environ.get("CS_STORE_JWT_SECRET") or "replace_this_with_a_strong_secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("CS_STORE_TOKEN_EXPIRE_MIN", "60"))

# API keys (simple list for prototype; in prod, use DB + rotation)
API_KEYS = [k for k in (os.environ.get("CS_STORE_API_KEYS") or "changemeapikey").split(",")]
