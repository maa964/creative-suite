# server/app/config.py
from pathlib import Path
import os

APP_ROOT = Path(__file__).resolve().parents[1]
KEYS_DIR = APP_ROOT / "keys"
KEYS_DIR.mkdir(parents=True, exist_ok=True)

# JWT settings (in prod, put SECRET_KEY in env/secret manager)
SECRET_KEY = os.environ.get("CS_STORE_JWT_SECRET")
if not SECRET_KEY:
    import secrets
    SECRET_KEY = secrets.token_urlsafe(32)
    import warnings
    warnings.warn("CS_STORE_JWT_SECRET not set. Using random key (tokens will invalidate on restart).", stacklevel=2)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("CS_STORE_TOKEN_EXPIRE_MIN", "60"))

# API keys (simple list for prototype; in prod, use DB + rotation)
_api_keys_env = os.environ.get("CS_STORE_API_KEYS", "")
API_KEYS = [k.strip() for k in _api_keys_env.split(",") if k.strip()]

# Upload size limits
MAX_MANIFEST_SIZE = int(os.environ.get("CS_STORE_MAX_MANIFEST_KB", "64")) * 1024  # 64KB default
MAX_PACKAGE_SIZE = int(os.environ.get("CS_STORE_MAX_PACKAGE_MB", "100")) * 1024 * 1024  # 100MB default
