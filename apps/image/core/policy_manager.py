# app/core/policy_manager.py
import logging
from pathlib import Path
from typing import Dict, Any
import json

LOG = logging.getLogger("creative.policy")

# Default allowed bases - adjust per deployment
SAFE_BASE_DIRS = [Path.home() / "projects", Path("/srv/creative")]

def normalize_paths(paths):
    out = []
    for p in paths:
        try:
            p = Path(p).expanduser().resolve()
        except Exception:
            LOG.warning("invalid path: %s", p)
            continue
        # enforce whitelist (prevent binding arbitrary /etc or /root)
        allowed = False
        for base in SAFE_BASE_DIRS:
            try:
                if str(p).startswith(str(base)):
                    allowed = True
                    break
            except Exception:
                pass
        if not allowed:
            LOG.warning("path %s is not within allowed bases, skipping", p)
            continue
        out.append(str(p))
    return out

def build_docker_args(plugin_dir: Path, policy: Dict[str, Any], out_dir: Path):
    args = [
        "--rm",
        "--pids-limit", str(int(policy.get("pids_limit", 64))),
        "--memory", f"{int(policy.get('memory_mb',256))}m",
        "--cpus", str(policy.get("cpus", 0.5)),
        "--security-opt", "no-new-privileges",
        "--cap-drop", "ALL",
    ]
    if policy.get("network", False) is False:
        args += ["--network", "none"]
    # read-only root FS
    args += ["--read-only"]
    # mount plugin (read-only)
    args += ["-v", f"{str(plugin_dir)}:/plugin:ro"]
    # create dedicated out dir
    args += ["-v", f"{str(out_dir)}:/out:rw"]
    # allowed host paths as read-only
    allowed = normalize_paths(policy.get("allowed_paths", []))
    for p in allowed:
        args += ["-v", f"{p}:{p}:ro"] 
    # write_paths must be subset of allowed_paths; mount rw
    write_paths = normalize_paths(policy.get("write_paths", []))
    for p in write_paths:
        args += ["-v", f"{p}:{p}:rw"]
    return args
