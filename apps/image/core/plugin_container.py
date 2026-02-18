import subprocess, json, shlex
from pathlib import Path

def run_in_container(plugin_dir: Path):
    cmd = [
        "docker","run","--rm","--network","none","--read-only",
        "-v", f"{plugin_dir}:/plugin:ro",
        "-v", "/tmp/out:/out:rw",
        "cs/plugin-runner:latest", "/plugin"
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    try:
        return json.loads(completed.stdout.strip())
    except:
        return {"ok": False, "error": "invalid JSON", "raw": completed.stdout}
