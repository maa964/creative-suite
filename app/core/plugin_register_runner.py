# このファイルを各プラグイン subprocess で呼び出す
import sys
import json
from pathlib import Path
import importlib
import traceback

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"ok": False, "error": "plugin_dir arg missing"}))
        sys.exit(1)
    plugin_dir = Path(sys.argv[1])
    manifest_path = plugin_dir / "plugin.json"
    if not manifest_path.exists():
        print(json.dumps({"ok": False, "error": "manifest not found"}))
        sys.exit(1)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entry = manifest.get("entry")
        if not entry:
            raise ValueError("entry not specified")
        module_path, callable_name = entry.split(":")
        mod = importlib.import_module(module_path)
        func = getattr(mod, callable_name)
        app_api = {"name": "sandbox"}  # minimal API for subprocess
        result = None
        if hasattr(func, "register"):
            result = func.register(app_api)
        elif callable(func):
            result = func(app_api)
        output = {"ok": True, "manifest": result if isinstance(result, dict) else None}
    except Exception as e:
        output = {"ok": False, "error": str(e), "traceback": traceback.format_exc()}
    print(json.dumps(output))

if __name__ == "__main__":
    main()
