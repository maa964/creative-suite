# server/app/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil, json, hashlib, os
from . import models, signing_utils

APP_ROOT = Path(__file__).resolve().parents[2]
STORAGE = APP_ROOT / "data"
STORAGE.mkdir(exist_ok=True)
META_FILE = STORAGE / "plugins.json"
if not META_FILE.exists():
    META_FILE.write_text(json.dumps({"plugins": []}, ensure_ascii=False), encoding="utf-8")

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
def approve_plugin(name: str, version: str, admin_key: str = None):
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
