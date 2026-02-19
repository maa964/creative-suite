"""Reusable image preview widget with save functionality."""

import shutil
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                                QHBoxLayout, QFileDialog)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal


class ImagePreviewWidget(QWidget):
    image_saved = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_path: Optional[Path] = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._image_label = QLabel("No image generated")
        self._image_label.setAlignment(Qt.AlignCenter)
        self._image_label.setMinimumSize(256, 256)
        self._image_label.setStyleSheet(
            "background-color: #1a1a1a; color: #666; border: 1px solid #333;"
        )
        layout.addWidget(self._image_label)

        btn_row = QHBoxLayout()
        self._save_btn = QPushButton("Save As...")
        self._save_btn.setEnabled(False)
        self._save_btn.clicked.connect(self._on_save)
        btn_row.addStretch()
        btn_row.addWidget(self._save_btn)
        layout.addLayout(btn_row)

    def set_image(self, path: Path):
        self._current_path = path
        pixmap = QPixmap(str(path))
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self._image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self._image_label.setPixmap(scaled)
            self._save_btn.setEnabled(True)

    def clear(self):
        self._image_label.clear()
        self._image_label.setText("No image generated")
        self._save_btn.setEnabled(False)
        self._current_path = None

    def _on_save(self):
        if not self._current_path:
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "", "PNG Files (*.png);;All Files (*)"
        )
        if file_path:
            if not file_path.endswith(".png"):
                file_path += ".png"
            shutil.copy2(str(self._current_path), file_path)
            self.image_saved.emit(file_path)
