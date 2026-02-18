import json
from pathlib import Path
from typing import Any, Dict

class ConfigManager:
    def __init__(self, app_name: str):
        self.config_dir = Path("config")
        self.config_file = self.config_dir / f"{app_name}.json"
        self.config: Dict[str, Any] = {}
        
        # Ensure config directory exists
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
        self.load()

    def load(self):
        if self.config_file.exists():
            try:
                text = self.config_file.read_text(encoding="utf-8")
                self.config = json.loads(text)
            except Exception as e:
                print(f"Failed to load config: {e}")
                self.config = {}
        else:
            self.config = {}

    def save(self):
        try:
            text = json.dumps(self.config, indent=2, ensure_ascii=False)
            self.config_file.write_text(text, encoding="utf-8")
        except Exception as e:
            print(f"Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        self.config[key] = value
        self.save()
