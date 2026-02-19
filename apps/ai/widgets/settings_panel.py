"""AI Settings panel for backend configuration."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QComboBox, QPushButton, QGroupBox,
                                QMessageBox)
from PySide6.QtCore import Signal, Qt

from apps.ai.models import AIBackendType
from apps.ai.services.availability import check_local_availability, LocalAvailability
from apps.core.config import ConfigManager


class AISettingsPanel(QWidget):
    backend_changed = Signal(str)

    def __init__(self, config: ConfigManager, parent=None):
        super().__init__(parent)
        self._config = config
        self._availability = check_local_availability()
        self._setup_ui()
        self._load_config()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Backend selection
        backend_group = QGroupBox("Backend")
        bg_layout = QVBoxLayout(backend_group)
        backend_row = QHBoxLayout()
        backend_row.addWidget(QLabel("Inference Backend:"))
        self._backend_combo = QComboBox()
        self._backend_combo.addItem("Hugging Face API", "api")
        self._backend_combo.addItem("Local Execution", "local")
        self._backend_combo.currentIndexChanged.connect(self._on_backend_changed)
        backend_row.addWidget(self._backend_combo)
        bg_layout.addLayout(backend_row)
        layout.addWidget(backend_group)

        # API Key
        api_group = QGroupBox("Hugging Face API")
        ag_layout = QVBoxLayout(api_group)
        key_row = QHBoxLayout()
        key_row.addWidget(QLabel("API Key:"))
        self._api_key_edit = QLineEdit()
        self._api_key_edit.setEchoMode(QLineEdit.Password)
        self._api_key_edit.setPlaceholderText("hf_...")
        key_row.addWidget(self._api_key_edit)
        ag_layout.addLayout(key_row)

        save_row = QHBoxLayout()
        save_row.addStretch()
        self._save_btn = QPushButton("Save API Key")
        self._save_btn.clicked.connect(self._save_api_key)
        save_row.addWidget(self._save_btn)
        ag_layout.addLayout(save_row)
        layout.addWidget(api_group)

        # Local availability
        local_group = QGroupBox("Local Dependencies Status")
        lg_layout = QVBoxLayout(local_group)

        deps = [
            ("PyTorch", self._availability.torch),
            ("Diffusers", self._availability.diffusers),
            ("Transformers", self._availability.transformers),
            ("Whisper", self._availability.whisper),
            ("rembg", self._availability.rembg),
        ]
        for name, available in deps:
            status = "Installed" if available else "Not Installed"
            color = "#2ecc71" if available else "#e74c3c"
            label = QLabel(f"{name}: <span style='color:{color}'>{status}</span>")
            label.setTextFormat(Qt.RichText)
            lg_layout.addWidget(label)

        lg_layout.addWidget(QLabel(""))
        features = [
            ("Text-to-Image (local)", self._availability.text_to_image_available),
            ("Speech-to-Text (local)", self._availability.speech_to_text_available),
            ("Background Removal (local)", self._availability.background_removal_available),
        ]
        for name, available in features:
            status = "Ready" if available else "Unavailable (use API)"
            color = "#2ecc71" if available else "#e67e22"
            label = QLabel(f"{name}: <span style='color:{color}'>{status}</span>")
            label.setTextFormat(Qt.RichText)
            lg_layout.addWidget(label)

        layout.addWidget(local_group)
        layout.addStretch()

    def _load_config(self):
        backend = self._config.get("ai_backend", "api")
        idx = 0 if backend == "api" else 1
        self._backend_combo.setCurrentIndex(idx)
        api_key = self._config.get("hf_api_key", "")
        if api_key:
            self._api_key_edit.setText(api_key)

    def _on_backend_changed(self, index):
        backend = self._backend_combo.currentData()
        self._config.set("ai_backend", backend)
        self.backend_changed.emit(backend)

    def _save_api_key(self):
        key = self._api_key_edit.text().strip()
        self._config.set("hf_api_key", key)
        QMessageBox.information(self, "Saved", "API key saved.")

    def get_backend_type(self) -> AIBackendType:
        data = self._backend_combo.currentData()
        return AIBackendType.HUGGINGFACE_API if data == "api" else AIBackendType.LOCAL

    def get_api_key(self) -> str:
        return self._api_key_edit.text().strip()

    def get_availability(self) -> LocalAvailability:
        return self._availability
