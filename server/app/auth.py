# server/app/auth.py
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, APIKeyHeader
from typing import Optional
from datetime import datetime, timedelta
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, API_KEYS
import jwt
import json
from pathlib import Path
from pydantic import BaseModel
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 token URL (used by clients)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# API key header name
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
API_KEY_HEADER = api_key_header

USERS_DB_PATH = Path(__file__).resolve().parents[1] / "users_db.json"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: Optional[list] = []

# --- user utils (very small, file-based for prototype) ---
def _load_users():
    if not USERS_DB_PATH.exists():
        # default admin user: admin / admin (hashed)
        default = {"admin": {"username": "admin", "full_name": "Administrator", "hashed_password": pwd_context.hash("admin"), "scopes": ["admin"]}}
        USERS_DB_PATH.write_text(json.dumps(default, indent=2), encoding="utf-8")
    return json.loads(USERS_DB_PATH.read_text(encoding="utf-8"))

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    users = _load_users()
    return users.get(username)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire.isoformat()})
    # include subject
    encoded_jwt = jwt.encode({"sub": data.get("sub"), "scopes": data.get("scopes", []), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Dependencies ---

async def get_current_user_from_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        scopes = payload.get("scopes", [])
        if username is None:
            raise credentials_exception
        token_data = {"username": username, "scopes": scopes}
    except Exception:
        raise credentials_exception
    user = get_user(token_data["username"])
    if user is None:
        raise credentials_exception
    return {"username": user["username"], "scopes": token_data["scopes"]}

def require_scope(required_scope: str):
    async def inner(user = Depends(get_current_user_from_token)):
        scopes = user.get("scopes", [])
        if required_scope not in scopes:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return user
    return inner

# API Key dependency (for automation scripts)
async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key and api_key in API_KEYS:
        return api_key
    raise HTTPException(status_code=401, detail="Invalid or missing API Key")
