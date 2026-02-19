# server/app/plugins.py
"""Plugin management API endpoints."""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from pathlib import Path
import json
import hashlib

from . import signing_utils, security_scan
from .auth import get_current_user_from_token, require_scope

router = APIRouter(prefix="/plugins", tags=["plugins"])

APP_ROOT = Path(__file__).resolve().parents[1]
STORAGE = APP_ROOT / "data"
STORAGE.mkdir(exist_ok=True)
META_FILE = STORAGE / "plugins.json"

if not META_FILE.exists():
    META_FILE.write_text(json.dumps({"plugins": []}, ensure_ascii=False), encoding="utf-8")


def load_meta() -> dict:
    """Load plugin metadata from JSON file."""
    return json.loads(META_FILE.read_text(encoding="utf-8"))


def save_meta(meta: dict) -> None:
    """Save plugin metadata to JSON file."""
    META_FILE.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


@router.get("/")
def list_plugins():
    """List all registered plugins."""
    return load_meta()


@router.get("/{name}/{version}")
def get_plugin(name: str, version: str):
    """Get plugin details by name and version."""
    meta = load_meta()
    for p in meta["plugins"]:
        if p["name"] == name and p["version"] == version:
            return p
    raise HTTPException(status_code=404, detail="Plugin not found")


@router.post("/upload")
async def upload_plugin(
    manifest: UploadFile = File(...),
    package: UploadFile = File(...),
    user: dict = Depends(get_current_user_from_token)
):
    """Upload a new plugin package."""
    mf = json.loads(await manifest.read())
    name = mf.get("name")
    version = mf.get("version", "0.0.0")

    if not name:
        raise HTTPException(status_code=400, detail="Manifest missing 'name' field")

    # Read package data
    data = await package.read()

    # Security scan
    ok, report = security_scan.scan_package(data)
    if not ok:
        raise HTTPException(
            status_code=400,
            detail=f"Security scan failed: {report.get('issues', [])}"
        )

    # Compute hash
    sha = hashlib.sha256(data).hexdigest()

    # Save package
    pkg_dir = STORAGE / f"{name}-{version}"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    pkg_path = pkg_dir / "package.tar.gz"
    pkg_path.write_bytes(data)

    # Save manifest with hash
    mf["hash"] = f"sha256:{sha}"
    mf["uploaded_by"] = user.get("username", "unknown")
    (pkg_dir / "manifest.json").write_text(
        json.dumps(mf, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Update metadata
    meta = load_meta()
    # Remove existing entry if updating
    meta["plugins"] = [
        p for p in meta["plugins"]
        if not (p["name"] == name and p["version"] == version)
    ]
    meta["plugins"].append({
        "name": name,
        "version": version,
        "path": str(pkg_dir),
        "hash": mf["hash"],
        "approved": False,
        "uploaded_by": user.get("username", "unknown")
    })
    save_meta(meta)

    return {"ok": True, "name": name, "version": version, "hash": mf["hash"]}


@router.post("/{name}/{version}/approve")
def approve_plugin(
    name: str,
    version: str,
    user: dict = Depends(require_scope("admin"))
):
    """Approve a plugin for distribution (admin only)."""
    meta = load_meta()
    for p in meta["plugins"]:
        if p["name"] == name and p["version"] == version:
            if p.get("approved"):
                return {"ok": False, "reason": "Already approved"}

            # Sign the manifest
            pkg_dir = Path(p["path"])
            manifest = json.loads((pkg_dir / "manifest.json").read_text(encoding="utf-8"))
            signature = signing_utils.sign_manifest(manifest)
            manifest["signature"] = signature
            (pkg_dir / "manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            p["approved"] = True
            p["signature"] = signature
            p["approved_by"] = user.get("username", "unknown")
            save_meta(meta)

            return {"ok": True, "signature": signature}

    raise HTTPException(status_code=404, detail="Plugin not found")


@router.delete("/{name}/{version}")
def delete_plugin(
    name: str,
    version: str,
    user: dict = Depends(require_scope("admin"))
):
    """Delete a plugin (admin only)."""
    meta = load_meta()
    for i, p in enumerate(meta["plugins"]):
        if p["name"] == name and p["version"] == version:
            pkg_dir = Path(p["path"])
            if pkg_dir.exists():
                import shutil
                shutil.rmtree(pkg_dir, ignore_errors=True)
            meta["plugins"].pop(i)
            save_meta(meta)
            return {"ok": True}

    raise HTTPException(status_code=404, detail="Plugin not found")


@router.get("/{name}/{version}/download")
def download_plugin(name: str, version: str):
    """Download an approved plugin package."""
    meta = load_meta()
    for p in meta["plugins"]:
        if p["name"] == name and p["version"] == version:
            if not p.get("approved"):
                raise HTTPException(status_code=403, detail="Plugin not approved")
            pkg_dir = Path(p["path"])
            pkg_path = pkg_dir / "package.tar.gz"
            if not pkg_path.exists():
                raise HTTPException(status_code=404, detail="Package file not found")
            return FileResponse(
                str(pkg_path),
                media_type="application/gzip",
                filename=f"{name}-{version}.tar.gz"
            )

    raise HTTPException(status_code=404, detail="Plugin not found")


@router.get("/{name}/{version}/manifest")
def get_manifest(name: str, version: str):
    """Get plugin manifest."""
    meta = load_meta()
    for p in meta["plugins"]:
        if p["name"] == name and p["version"] == version:
            pkg_dir = Path(p["path"])
            manifest_path = pkg_dir / "manifest.json"
            if not manifest_path.exists():
                raise HTTPException(status_code=404, detail="Manifest not found")
            return json.loads(manifest_path.read_text(encoding="utf-8"))

    raise HTTPException(status_code=404, detail="Plugin not found")
