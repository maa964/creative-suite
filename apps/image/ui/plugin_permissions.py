# app/ui/plugin_permissions.py
import json
import logging
from pathlib import Path
from typing import Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QFormLayout, QLineEdit, QSpinBox,
    QPushButton, QCheckBox, QLabel, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt

LOG = logging.getLogger("creative.permissions")
POLICY_FILE = Path("config/policies.json")

DEFAULT_POLICY_TEMPLATE = {
    "network": False,
    "gpu": False,
    "memory_mb": 256,
    "cpus": 0.5,
    "pids_limit": 64,
    "timeout_sec": 30,
    "allowed_paths": [],  # list of host paths (read-only or read-write controlled separately)
    "write_paths": []     # subset allowed for write
}

class PolicyStore:
    def __init__(self, path: Path = POLICY_FILE):
        self.path = Path(path)
        self._data: Dict[str, Any] = {}
        self.load()

    def load(self):
        try:
            if self.path.exists():
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            else:
                self._data = {}
        except Exception as e:
            LOG.exception("failed to load policies: %s", e)
            self._data = {}

    def save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            LOG.exception("failed to save policies: %s", e)
            raise

    def get(self, plugin_name: str):
        return self._data.get(plugin_name, None)

    def set(self, plugin_name: str, policy: Dict[str, Any]):
        self._data[plugin_name] = policy
        self.save()

    def list_plugins(self):
        return list(self._data.keys())

class PluginPermissionsWidget(QWidget):
    def __init__(self, available_plugins: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plugin Permissions")
        self.policy_store = PolicyStore()
        self.available_plugins = available_plugins

        self.layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        for p in available_plugins:
            self.list_widget.addItem(p)
        self.layout.addWidget(QLabel("Installed Plugins:"))
        self.layout.addWidget(self.list_widget)

        # Detail form
        self.form = QFormLayout()
        self.network_cb = QCheckBox("Allow network access")
        self.gpu_cb = QCheckBox("Allow GPU access")
        self.memory_sb = QSpinBox(); self.memory_sb.setRange(64, 65536); self.memory_sb.setValue(256)
        self.cpus_input = QLineEdit("0.5")
        self.timeout_sb = QSpinBox(); self.timeout_sb.setRange(1, 3600); self.timeout_sb.setValue(30)
        self.allowed_paths_input = QLineEdit()
        self.write_paths_input = QLineEdit()
        self.template_combo = QComboBox()
        self.template_combo.addItems(["Safe (default)", "Standard", "High privilege"])

        self.form.addRow("Template:", self.template_combo)
        self.form.addRow("Network:", self.network_cb)
        self.form.addRow("GPU:", self.gpu_cb)
        self.form.addRow("Memory (MB):", self.memory_sb)
        self.form.addRow("CPUs (float):", self.cpus_input)
        self.form.addRow("Timeout (sec):", self.timeout_sb)
        self.form.addRow("Allowed paths (comma):", self.allowed_paths_input)
        self.form.addRow("Write paths (comma):", self.write_paths_input)

        self.save_btn = QPushButton("Save Policy")
        self.save_btn.clicked.connect(self.save_policy)

        self.layout.addLayout(self.form)
        self.layout.addWidget(self.save_btn)

        self.list_widget.currentTextChanged.connect(self.on_select)

    def on_select(self, plugin_name):
        if not plugin_name:
            return
        policy = self.policy_store.get(plugin_name)
        if not policy:
            policy = DEFAULT_POLICY_TEMPLATE.copy()
        self.network_cb.setChecked(bool(policy.get("network")))
        self.gpu_cb.setChecked(bool(policy.get("gpu")))
        self.memory_sb.setValue(int(policy.get("memory_mb", 256)))
        self.cpus_input.setText(str(policy.get("cpus", 0.5)))
        self.timeout_sb.setValue(int(policy.get("timeout_sec", 30)))
        self.allowed_paths_input.setText(",".join(policy.get("allowed_paths", [])))
        self.write_paths_input.setText(",".join(policy.get("write_paths", [])))

    def save_policy(self):
        plugin = self.list_widget.currentItem()
        if not plugin:
            QMessageBox.warning(self, "選択されていません", "プラグインを選択してください。")
            return
        name = plugin.text()
        try:
            policy = {
                "network": self.network_cb.isChecked(),
                "gpu": self.gpu_cb.isChecked(),
                "memory_mb": int(self.memory_sb.value()),
                "cpus": float(self.cpus_input.text()),
                "timeout_sec": int(self.timeout_sb.value()),
                "allowed_paths": [p.strip() for p in self.allowed_paths_input.text().split(",") if p.strip()],
                "write_paths": [p.strip() for p in self.write_paths_input.text().split(",") if p.strip()],
            }
            self.policy_store.set(name, policy)
            QMessageBox.information(self, "保存しました", f"{name} のポリシーを保存しました。")
        except Exception as e:
            LOG.exception("failed to save policy: %s", e)
            QMessageBox.critical(self, "保存失敗", f"ポリシーの保存中にエラーが発生しました:\n{e}")
