    CreativeStudio - Permission UI & PolicyManager scaffold

    Files included:

    - app/ui/plugin_permissions.py : PySide6-based permissions UI widget
    - app/core/policy_manager.py : Policy to docker args builder with path normalization
    - config/policies.json : sample policy file

Usage:
- From your main app, you can open the widget with:
    from app.ui.plugin_permissions import PluginPermissionsWidget
    w = PluginPermissionsWidget(['sample_plugin','sample_plugin_ai'])
    w.show()

- PolicyManager.build_docker_args(plugin_dir, policy, out_dir) returns a list of docker args (without 'docker run')

Security notes:
- Adjust SAFE_BASE_DIRS in policy_manager.py to match allowed host paths for your deployment.
- Always validate and audit policies before granting GPU/network access.

Generated for masahiro.
