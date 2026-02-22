"""Text-to-Image generation panel."""

import tempfile
import uuid
from pathlib import Path

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QTextEdit, QSpinBox, QDoubleSpinBox,
                                QPushButton, QProgressBar, QComboBox, QGroupBox)
from PySide6.QtCore import Signal

from apps.ai.models import TextToImageParams
from apps.ai.widgets.image_preview import ImagePreviewWidget


class TextToImagePanel(QWidget):
    generate_requested = Signal(object, object)  # TextToImageParams, Path
    cancel_requested = Signal()

    def __init__(self, available_models: list[str] = None, parent=None):
        super().__init__(parent)
        self._available_models = available_models or []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Prompt
        prompt_group = QGroupBox("Prompt")
        pg_layout = QVBoxLayout(prompt_group)
        self._prompt = QTextEdit()
        self._prompt.setPlaceholderText("Describe the image you want to generate...")
        self._prompt.setMaximumHeight(80)
        pg_layout.addWidget(self._prompt)
        pg_layout.addWidget(QLabel("Negative Prompt:"))
        self._neg_prompt = QTextEdit()
        self._neg_prompt.setPlaceholderText("What to exclude...")
        self._neg_prompt.setMaximumHeight(60)
        pg_layout.addWidget(self._neg_prompt)
        layout.addWidget(prompt_group)

        # Parameters
        params_group = QGroupBox("Parameters")
        params_layout = QVBoxLayout(params_group)

        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("Model:"))
        self._model_combo = QComboBox()
        for m in self._available_models:
            self._model_combo.addItem(m)
        model_row.addWidget(self._model_combo)
        params_layout.addLayout(model_row)

        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("W:"))
        self._width_spin = QSpinBox()
        self._width_spin.setRange(256, 1024)
        self._width_spin.setSingleStep(64)
        self._width_spin.setValue(512)
        size_row.addWidget(self._width_spin)
        size_row.addWidget(QLabel("H:"))
        self._height_spin = QSpinBox()
        self._height_spin.setRange(256, 1024)
        self._height_spin.setSingleStep(64)
        self._height_spin.setValue(512)
        size_row.addWidget(self._height_spin)
        params_layout.addLayout(size_row)

        steps_row = QHBoxLayout()
        steps_row.addWidget(QLabel("Steps:"))
        self._steps_spin = QSpinBox()
        self._steps_spin.setRange(1, 150)
        self._steps_spin.setValue(30)
        steps_row.addWidget(self._steps_spin)
        steps_row.addWidget(QLabel("CFG:"))
        self._cfg_spin = QDoubleSpinBox()
        self._cfg_spin.setRange(1.0, 30.0)
        self._cfg_spin.setValue(7.5)
        self._cfg_spin.setSingleStep(0.5)
        steps_row.addWidget(self._cfg_spin)
        params_layout.addLayout(steps_row)

        seed_row = QHBoxLayout()
        seed_row.addWidget(QLabel("Seed (-1=random):"))
        self._seed_spin = QSpinBox()
        self._seed_spin.setRange(-1, 2147483647)
        self._seed_spin.setValue(-1)
        seed_row.addWidget(self._seed_spin)
        params_layout.addLayout(seed_row)

        layout.addWidget(params_group)

        # Buttons
        btn_row = QHBoxLayout()
        self._generate_btn = QPushButton("Generate")
        self._generate_btn.setStyleSheet(
            "background-color: #2ecc71; color: #fff; font-weight: bold; padding: 8px;"
        )
        self._generate_btn.clicked.connect(self._on_generate)
        btn_row.addWidget(self._generate_btn)
        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setEnabled(False)
        self._cancel_btn.clicked.connect(self.cancel_requested.emit)
        btn_row.addWidget(self._cancel_btn)
        layout.addLayout(btn_row)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        layout.addWidget(self._progress)

        # Preview
        self._preview = ImagePreviewWidget()
        layout.addWidget(self._preview)

    def _on_generate(self):
        prompt = self._prompt.toPlainText().strip()
        if not prompt:
            return
        params = TextToImageParams(
            prompt=prompt,
            negative_prompt=self._neg_prompt.toPlainText().strip(),
            width=self._width_spin.value(),
            height=self._height_spin.value(),
            num_inference_steps=self._steps_spin.value(),
            guidance_scale=self._cfg_spin.value(),
            seed=None if self._seed_spin.value() == -1 else self._seed_spin.value(),
            model_id=(self._model_combo.currentText()
                      if self._model_combo.count() > 0
                      else "stabilityai/stable-diffusion-2-1"),
        )
        output_dir = Path(tempfile.gettempdir()) / "creative_suite_ai"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"txt2img_{uuid.uuid4().hex[:8]}.png"
        self.generate_requested.emit(params, output_path)

    def set_running(self, running: bool):
        self._generate_btn.setEnabled(not running)
        self._cancel_btn.setEnabled(running)
        if running:
            self._progress.setValue(0)

    def set_progress(self, value: int):
        self._progress.setValue(value)

    def show_result(self, path: Path):
        self._preview.set_image(path)

    def show_error(self, message: str):
        self._preview.clear()
