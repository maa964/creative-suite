from pathlib import Path
from app.core.plugin_host import PluginHost

def test_pluginhost_registers_plugins():
    repo_root = Path(__file__).resolve().parents[1]
    plugins_dir = repo_root / 'plugins'
    assert plugins_dir.exists()

    host = PluginHost(plugins_dir, app_api={'name':'testhost'}, timeout_seconds=5)
    results = host.register_all()
    assert 'sample_plugin' in results
    assert 'sample_plugin_ai' in results
    assert results['sample_plugin_ai']['ok'] is True
