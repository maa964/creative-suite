# server/app/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Security
from pathlib import Path
import shutil, json, hashlib, os
from . import models, signing_utils
from . import auth

APP_ROOT = Path(__file__).resolve().parents[2]
STORAGE = APP_ROOT / "data"
STORAGE.mkdir(exist_ok=True)
META_FILE = STORAGE / "plugins.json"
if not META_FILE.exists():
    META_FILE.write_text(json.dumps({"plugins": []}, ensure_ascii=False), encoding="utf-8")

from .auth import oauth2_scheme, authenticate_user, create_access_token, get_api_key, require_scope, get_current_user_from_token
from .config import ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import Depends, Form
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI(title="CreativeStudio Plugin Store (prototype)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_meta():
    return json.loads(META_FILE.read_text(encoding="utf-8"))

def save_meta(meta):
    META_FILE.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

@app.get("/plugins")
def list_plugins():
    meta = load_meta()
    return meta

@app.post("/plugins/upload")
async def upload_plugin(manifest: UploadFile = File(...), package: UploadFile = File(...)):
    # manifest: small json file, package: tarball
    mf = json.loads(await manifest.read())
    name = mf.get("name")
    version = mf.get("version", "0.0.0")
    if not name:
        raise HTTPException(status_code=400, detail="manifest missing name")
    # compute hash of package
    data = await package.read()
    sha = hashlib.sha256(data).hexdigest()
    pkg_dir = STORAGE / f"{name}-{version}"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    pkg_path = pkg_dir / "package.tar.gz"
    pkg_path.write_bytes(data)
    # save manifest
    mf['hash'] = f"sha256:{sha}"
    (pkg_dir / "manifest.json").write_text(json.dumps(mf, ensure_ascii=False, indent=2), encoding="utf-8")
    meta = load_meta()
    meta['plugins'].append({"name": name, "version": version, "path": str(pkg_dir), "hash": mf['hash'], "approved": False})
    save_meta(meta)
    return {"ok": True, "name": name, "version": version, "hash": mf['hash']}

@app.post("/plugins/{name}/{version}/approve")
def approve_plugin(name: str, version: str, admin_key: str = None, token: str = Depends(auth.oauth2_scheme), api_key: str = Depends(auth.API_KEY_HEADER)):
    # Allow either a valid admin OAuth token OR a valid API key header
    allowed = False
    # check API key first
    try:
        if api_key:
            # require_admin_api_key will raise if invalid
            auth.require_admin_api_key(api_key)
            allowed = True
    except Exception:
        allowed = False
    if not allowed:
        # check token and admin scope
        try:
            user = auth.get_current_user(token)
            if 'admin' in user.get('scopes', []):
                allowed = True
        except Exception:
            allowed = False

    if not allowed:
        raise HTTPException(status_code=401, detail="Not authorized to approve plugins")

    meta = load_meta()
    for p in meta['plugins']:
        if p['name']==name and p['version']==version:
            if p.get('approved'):
                return {"ok": False, "reason":"already approved"}
            # sign package hash using server-side key (if present)
            pkg_dir = Path(p['path'])
            manifest = json.loads((pkg_dir / "manifest.json").read_text(encoding="utf-8"))
            signature = signing_utils.sign_manifest(manifest)
            manifest['signature'] = signature
            (pkg_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            p['approved'] = True
            p['signature'] = signature
            save_meta(meta)
            return {"ok": True, "signature": signature}
    raise HTTPException(status_code=404, detail="plugin not found")

@app.get("/plugins/{name}/{version}/download")
def download_plugin(name: str, version: str):
    meta = load_meta()
    for p in meta['plugins']:
        if p['name']==name and p['version']==version and p.get('approved'):
            pkg_dir = Path(p['path'])
            return FileResponse(str(pkg_dir / "package.tar.gz"), media_type="application/gzip", filename=f"{name}-{version}.tar.gz")
    raise HTTPException(status_code=404, detail="plugin not found or not approved")

@app.get("/plugins/{name}/{version}/manifest")
def get_manifest(name: str, version: str):
    meta = load_meta()
    for p in meta['plugins']:
        if p['name']==name and p['version']==version:
            pkg_dir = Path(p['path'])
            return json.loads((pkg_dir / "manifest.json").read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail="plugin not found")

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = auth.create_token(user['username'], user.get('scopes', []), expires_minutes=60)
    return {"access_token": token, "token_type": "bearer"}
@app.post("/token")
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 password grant token endpoint"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["username"], "scopes": user.get("scopes", [])}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
