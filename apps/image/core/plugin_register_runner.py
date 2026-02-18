import os, sys, json
from pathlib import Path

def main():
    plugin_dir = Path(sys.argv[1])
    out_dir = Path(os.getenv("CS_OUT_DIR", "/out"))
    result = {"ok": True, "plugin": plugin_dir.name}
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "register.json", "w") as f:
        json.dump(result, f)
    print(json.dumps(result))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))
