"""Speech-to-Text transcription panel."""

from pathlib import Path

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QTextEdit, QPushButton, QProgressBar,
                                QComboBox, QGroupBox, QFileDialog)
from PySide6.QtCore import Signal
from PySide6.QtGui import QGuiApplication

from apps.ai.models import SpeechToTextParams


class SpeechToTextPanel(QWidget):
    transcribe_requested = Signal(object)  # SpeechToTextParams
    cancel_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._audio_path: Path | None = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Audio file
        file_group = QGroupBox("Audio File")
        fg_layout = QVBoxLayout(file_group)
        file_row = QHBoxLayout()
        self._file_label = QLabel("No file selected")
        self._file_label.setStyleSheet("color: #aaa;")
        file_row.addWidget(self._file_label, 1)
        self._browse_btn = QPushButton("Browse...")
        self._browse_btn.clicked.connect(self._browse_audio)
        file_row.addWidget(self._browse_btn)
        fg_layout.addLayout(file_row)
        layout.addWidget(file_group)

        # Settings
        settings_group = QGroupBox("Settings")
        sg_layout = QVBoxLayout(settings_group)

        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("Model Size:"))
        self._model_combo = QComboBox()
        for size in ["tiny", "base", "small", "medium", "large"]:
            self._model_combo.addItem(size)
        self._model_combo.setCurrentText("base")
        model_row.addWidget(self._model_combo)
        sg_layout.addLayout(model_row)

        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("Language (blank=auto):"))
        self._lang_combo = QComboBox()
        self._lang_combo.setEditable(True)
        self._lang_combo.addItems(["", "en", "ja", "zh", "ko", "fr", "de", "es"])
        lang_row.addWidget(self._lang_combo)
        sg_layout.addLayout(lang_row)

        layout.addWidget(settings_group)

        # Buttons
        btn_row = QHBoxLayout()
        self._transcribe_btn = QPushButton("Transcribe")
        self._transcribe_btn.setStyleSheet(
            "background-color: #3498db; color: #fff; font-weight: bold; padding: 8px;"
        )
        self._transcribe_btn.clicked.connect(self._on_transcribe)
        btn_row.addWidget(self._transcribe_btn)
        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setEnabled(False)
        self._cancel_btn.clicked.connect(self.cancel_requested.emit)
        btn_row.addWidget(self._cancel_btn)
        layout.addLayout(btn_row)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        layout.addWidget(self._progress)

        # Output
        output_group = QGroupBox("Transcription Output")
        og_layout = QVBoxLayout(output_group)
        self._output_text = QTextEdit()
        self._output_text.setReadOnly(True)
        self._output_text.setPlaceholderText("Transcription will appear here...")
        og_layout.addWidget(self._output_text)

        copy_row = QHBoxLayout()
        copy_row.addStretch()
        self._copy_btn = QPushButton("Copy to Clipboard")
        self._copy_btn.setEnabled(False)
        self._copy_btn.clicked.connect(self._copy_to_clipboard)
        copy_row.addWidget(self._copy_btn)
        og_layout.addLayout(copy_row)

        layout.addWidget(output_group)

    def _browse_audio(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Audio File", "",
            "Audio Files (*.mp3 *.wav *.flac *.ogg *.m4a *.webm *.mp4);;All Files (*)"
        )
        if path:
            self._audio_path = Path(path)
            self._file_label.setText(self._audio_path.name)
            self._file_label.setStyleSheet("color: #fff;")

    def _on_transcribe(self):
        if not self._audio_path:
            return
        params = SpeechToTextParams(
            audio_path=self._audio_path,
            language=self._lang_combo.currentText() or None,
            model_size=self._model_combo.currentText(),
        )
        self.transcribe_requested.emit(params)

    def _copy_to_clipboard(self):
        text = self._output_text.toPlainText()
        if text:
            QGuiApplication.clipboard().setText(text)

    def set_running(self, running: bool):
        self._transcribe_btn.setEnabled(not running)
        self._cancel_btn.setEnabled(running)
        if running:
            self._progress.setValue(0)

    def set_progress(self, value: int):
        self._progress.setValue(value)

    def show_result(self, text: str):
        self._output_text.setPlainText(text)
        self._copy_btn.setEnabled(True)

    def show_error(self, message: str):
        self._output_text.setPlainText(f"Error: {message}")
