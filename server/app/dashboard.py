# server/app/dashboard.py
"""Dashboard API endpoints for plugin store administration."""

from fastapi import APIRouter, Depends
from pathlib import Path
import json
from datetime import datetime, timezone

from .auth import get_current_user_from_token, require_scope
from .plugins import load_meta, STORAGE

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_stats(user: dict = Depends(get_current_user_from_token)):
    """Get plugin store statistics."""
    meta = load_meta()
    plugins = meta.get("plugins", [])

    total = len(plugins)
    approved = sum(1 for p in plugins if p.get("approved"))
    pending = total - approved

    # Calculate total storage size
    total_size = 0
    for p in plugins:
        pkg_dir = Path(p.get("path", ""))
        if pkg_dir.exists():
            for f in pkg_dir.rglob("*"):
                if f.is_file():
                    total_size += f.stat().st_size

    return {
        "total_plugins": total,
        "approved_plugins": approved,
        "pending_plugins": pending,
        "storage_bytes": total_size,
        "storage_mb": round(total_size / (1024 * 1024), 2)
    }


@router.get("/plugins")
async def list_all_plugins(user: dict = Depends(get_current_user_from_token)):
    """List all plugins with detailed info for dashboard."""
    meta = load_meta()
    plugins = []

    for p in meta.get("plugins", []):
        pkg_dir = Path(p.get("path", ""))
        manifest_path = pkg_dir / "manifest.json"

        plugin_info = {
            "name": p.get("name"),
            "version": p.get("version"),
            "approved": p.get("approved", False),
            "hash": p.get("hash"),
            "uploaded_by": p.get("uploaded_by", "unknown"),
            "approved_by": p.get("approved_by"),
        }

        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                plugin_info["description"] = manifest.get("description", "")
                plugin_info["author"] = manifest.get("author", "")
                plugin_info["homepage"] = manifest.get("homepage", "")
            except Exception:
                pass

        # Get file stats
        pkg_path = pkg_dir / "package.tar.gz"
        if pkg_path.exists():
            stat = pkg_path.stat()
            plugin_info["size_bytes"] = stat.st_size
            plugin_info["uploaded_at"] = datetime.fromtimestamp(stat.st_mtime).isoformat()

        plugins.append(plugin_info)

    return {"plugins": plugins}


@router.get("/pending")
async def list_pending_plugins(user: dict = Depends(require_scope("admin"))):
    """List plugins pending approval (admin only)."""
    meta = load_meta()
    pending = [
        p for p in meta.get("plugins", [])
        if not p.get("approved")
    ]
    return {"pending": pending, "count": len(pending)}


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "storage_path": str(STORAGE),
        "storage_exists": STORAGE.exists()
    }
