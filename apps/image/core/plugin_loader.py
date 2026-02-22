
import logging
import json
from pathlib import Path
from typing import List, Dict, Optional

LOG = logging.getLogger(__name__)

class PluginLoader:
    """
    Handles discovery and static metadata loading of plugins.
    Separated from PluginHost which manages runtime execution.
    """
    
    @staticmethod
    def scan_plugins(plugins_dir: Path) -> List[Dict[str, Any]]:
        """
        Scans a directory for plugins (folders with plugin.json).
        Returns a list of valid plugin manifests (augmented with 'path').
        """
        plugins = []
        if not plugins_dir.exists():
            LOG.warning("Plugin directory not found: %s", plugins_dir)
            return plugins

        for p in sorted(plugins_dir.iterdir()):
            if not p.is_dir():
                continue
            
            # Explicitly exclude hidden dirs and __pycache__
            if p.name.startswith(".") or p.name.startswith("__"):
                continue

            manifest_file = p / "plugin.json"
            if manifest_file.exists():
                try:
                    data = json.loads(manifest_file.read_text(encoding="utf-8"))
                    # Basic validation
                    if "name" not in data:
                        LOG.warning(f"Plugin at {p.name} missing 'name' in manifest")
                        continue
                    
                    # Inject path for loader use
                    data["_path"] = str(p)
                    plugins.append(data)
                except Exception as e:
                    LOG.error(f"Failed to load plugin manifest at {p.name}: {e}")
        
        return plugins

    @staticmethod
    def load_manifest(plugin_path: Path) -> Optional[Dict[str, Any]]:
        """Loads a single plugin manifest."""
        mf = plugin_path / "plugin.json"
        if not mf.exists():
            return None
        try:
            return json.loads(mf.read_text(encoding="utf-8"))
        except Exception as e:
            LOG.error(f"Invalid manifest at {plugin_path}: {e}")
            return None
