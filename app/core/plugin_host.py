# app/core/plugin_host.py
import importlib
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
    def __init__(self, plugins_root: Path, app_api: Dict[str, Any] = None):
        self.plugins_root = Path(plugins_root)
        self.app_api = app_api or {}
        self.registered = {}  # name -> manifest or error info

    def _load_manifest(self, plugin_dir: Path):
        mf = plugin_dir / "plugin.json"
        if not mf.exists():
            raise FileNotFoundError(f"manifest not found: {mf}")
        try:
            data = json.loads(mf.read_text(encoding='utf-8'))
            return data
        except Exception as e:
            raise RuntimeError(f"invalid manifest {mf}: {e}") from e

    def _import_entry(self, entry: str):
        # entry format: module.path:callable_name
        if ':' not in entry:
            raise ValueError('entry must be module:callable')
        module_path, callable_name = entry.split(':', 1)
        mod = importlib.import_module(module_path)
        func = getattr(mod, callable_name)
        return func

    def _run_plugin_subprocess(self, plugin_dir: Path):
        """サンドボックスで register を呼び出す"""
        cmd = [sys.executable, str(Path(__file__).parent / "plugin_register_runner.py"), str(plugin_dir)]
        try:
            completed = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            stdout = completed.stdout.strip()
            try:
                data = json.loads(stdout)
            except Exception:
                data = {"ok": False, "error": "invalid JSON output", "raw": stdout}
            return data
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "timeout expired"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def register_all(self, timeout_seconds: int = 30):
        """Scan plugins_root, attempt to register each plugin.
        Returns dict: {plugin_name: {'ok':True,'manifest':...} or {'ok':False,'error': '...'}}"""
        self.registered = {}
        if not self.plugins_root.exists():
            LOG.warning("plugins root not found: %s", self.plugins_root)
            return self.registered
        for p in sorted(self.plugins_root.iterdir()):
            if not p.is_dir():
                continue
            try:
                manifest = self._load_manifest(p)
                name = manifest.get('name') or p.name
                entry = manifest.get('entry')
                if not entry:
                    raise RuntimeError('entry not specified in manifest')
                try:
                    func = self._import_entry(entry)
                except Exception as e:
                    LOG.exception('import entry failed: %s', e)
                    self.registered[name] = {'ok': False, 'error': f'import_error: {e}'}
                    continue
                # Call register with app_api; catch exceptions from plugin
                try:
                    # Common patterns:
                    # 1) module object with register(app_api) -> func.register(...)
                    # 2) module-level callable register(app_api) -> func(self.app_api)
                    result = None
                    # prefer calling register method if present
                    if hasattr(func, 'register'):
                        try:
                            result = func.register(self.app_api)  # type: ignore
                        except Exception:
                            # fall back to calling func if it's callable
                            if callable(func):
                                result = func(self.app_api)
                    elif callable(func):
                        result = func(self.app_api)
                    # normalize result to manifest-like dict
                    if isinstance(result, dict):
                        self.registered[name] = {'ok': True, 'manifest': result}
                    else:
                        # plugin may not return manifest; mark ok but no manifest
                        self.registered[name] = {'ok': True, 'manifest': None}
                except Exception as e:
                    LOG.exception('plugin register failed for %s: %s', name, e)
                    tb = traceback.format_exc()
                    self.registered[name] = {'ok': False, 'error': str(e), 'traceback': tb}
            except Exception as e:
                LOG.exception('failed processing plugin dir %s: %s', p, e)
                self.registered[p.name] = {'ok': False, 'error': str(e)}
        return self.registered
