"""Background Removal panel."""

import tempfile
import uuid
from pathlib import Path

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QProgressBar, QCheckBox,
                                QGroupBox, QFileDialog, QSplitter)
from PySide6.QtCore import Signal, Qt

from apps.ai.models import BackgroundRemovalParams
from apps.ai.widgets.image_preview import ImagePreviewWidget


class BackgroundRemovalPanel(QWidget):
    remove_requested = Signal(object, object)  # BackgroundRemovalParams, Path
    cancel_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._image_path: Path | None = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # File selection
        file_group = QGroupBox("Input Image")
        fg_layout = QVBoxLayout(file_group)
        file_row = QHBoxLayout()
        self._file_label = QLabel("No image selected")
        self._file_label.setStyleSheet("color: #aaa;")
        file_row.addWidget(self._file_label, 1)
        self._browse_btn = QPushButton("Browse...")
        self._browse_btn.clicked.connect(self._browse_image)
        file_row.addWidget(self._browse_btn)
        fg_layout.addLayout(file_row)
        layout.addWidget(file_group)

        # Options
        opts_group = QGroupBox("Options")
        og_layout = QVBoxLayout(opts_group)
        self._alpha_matting_cb = QCheckBox("Alpha Matting (higher quality, slower)")
        og_layout.addWidget(self._alpha_matting_cb)
        layout.addWidget(opts_group)

        # Buttons
        btn_row = QHBoxLayout()
        self._remove_btn = QPushButton("Remove Background")
        self._remove_btn.setStyleSheet(
            "background-color: #e67e22; color: #fff; font-weight: bold; padding: 8px;"
        )
        self._remove_btn.clicked.connect(self._on_remove)
        btn_row.addWidget(self._remove_btn)
        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setEnabled(False)
        self._cancel_btn.clicked.connect(self.cancel_requested.emit)
        btn_row.addWidget(self._cancel_btn)
        layout.addLayout(btn_row)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        layout.addWidget(self._progress)

        # Before / After preview
        preview_label_row = QHBoxLayout()
        preview_label_row.addWidget(QLabel("Input"))
        preview_label_row.addWidget(QLabel("Result"))
        layout.addLayout(preview_label_row)

        preview_splitter = QSplitter(Qt.Horizontal)
        self._input_preview = ImagePreviewWidget()
        self._output_preview = ImagePreviewWidget()
        preview_splitter.addWidget(self._input_preview)
        preview_splitter.addWidget(self._output_preview)
        layout.addWidget(preview_splitter)

    def _browse_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.webp);;All Files (*)"
        )
        if path:
            self._image_path = Path(path)
            self._file_label.setText(self._image_path.name)
            self._file_label.setStyleSheet("color: #fff;")
            self._input_preview.set_image(self._image_path)

    def _on_remove(self):
        if not self._image_path:
            return
        params = BackgroundRemovalParams(
            image_path=self._image_path,
            alpha_matting=self._alpha_matting_cb.isChecked(),
        )
        output_dir = Path(tempfile.gettempdir()) / "creative_suite_ai"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"rmbg_{uuid.uuid4().hex[:8]}.png"
        self.remove_requested.emit(params, output_path)

    def set_running(self, running: bool):
        self._remove_btn.setEnabled(not running)
        self._cancel_btn.setEnabled(running)
        if running:
            self._progress.setValue(0)

    def set_progress(self, value: int):
        self._progress.setValue(value)

    def show_result(self, path: Path):
        self._output_preview.set_image(path)

    def show_error(self, message: str):
        self._output_preview.clear()
