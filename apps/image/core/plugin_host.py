import logging
import json
import traceback
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

class PluginHost:
    def __init__(self, plugins_root: Path, app_api: Dict[str, Any] = None, timeout_seconds: int = 30):
        self.plugins_root = Path(plugins_root)
        self.app_api = app_api or {}
        self.registered = {}  # name -> manifest or error info
        self.timeout_seconds = timeout_seconds

    def _load_manifest(self, plugin_dir: Path):
        mf = plugin_dir / "plugin.json"
        if not mf.exists():
            raise FileNotFoundError(f"manifest not found: {mf}")
        try:
            data = json.loads(mf.read_text(encoding='utf-8'))
            return data
        except Exception as e:
            raise RuntimeError(f"invalid manifest {mf}: {e}") from e

    def _run_plugin_subprocess(self, plugin_dir: Path):
        runner = Path(__file__).resolve().parent / "plugin_register_runner.py"
        cmd = [sys.executable, str(runner), str(plugin_dir)]
        try:
            completed = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout_seconds)
            stdout = completed.stdout.strip()
            stderr = completed.stderr.strip()
            if stderr:
                LOG.debug("plugin subprocess stderr: %s", stderr)
            try:
                data = json.loads(stdout) if stdout else {"ok": False, "error": "no output"}
            except Exception:
                data = {"ok": False, "error": "invalid JSON output", "raw": stdout, "stderr": stderr}
            return data
        except subprocess.TimeoutExpired as te:
            LOG.exception("plugin subprocess timeout: %s", te)
            return {"ok": False, "error": "timeout expired"}
        except Exception as e:
            LOG.exception("plugin subprocess failed: %s", e)
            return {"ok": False, "error": str(e)}

    def register_all(self, timeout_seconds: int = None):
        self.registered = {}
        if timeout_seconds is None:
            timeout_seconds = self.timeout_seconds
        if not self.plugins_root.exists():
            LOG.warning("plugins root not found: %s", self.plugins_root)
            return self.registered
        for p in sorted(self.plugins_root.iterdir()):
            if not p.is_dir():
                continue
            try:
                manifest = self._load_manifest(p)
                name = manifest.get('name') or p.name
                # use subprocess runner for safety
                try:
                    data = self._run_plugin_subprocess(p)
                except Exception as e:
                    LOG.exception('subprocess runner failed for %s: %s', p, e)
                    self.registered[name] = {'ok': False, 'error': str(e)}
                    continue
                if data.get('ok') is True:
                    self.registered[name] = {'ok': True, 'manifest': data.get('manifest')}
                else:
                    self.registered[name] = {'ok': False, 'error': data.get('error'), 'raw': data.get('raw'), 'traceback': data.get('traceback')}
            except Exception as e:
                LOG.exception('failed processing plugin dir %s: %s', p, e)
                self.registered[p.name] = {'ok': False, 'error': str(e)}
        return self.registered
