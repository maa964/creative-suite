"""Transport controls bar (play/pause/stop, timecode, seek)."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QSlider
from PySide6.QtCore import Qt, Signal


def ms_to_timecode(ms: int) -> str:
    total_s = ms // 1000
    h = total_s // 3600
    m = (total_s % 3600) // 60
    s = total_s % 60
    f = (ms % 1000) // 33  # ~30fps frame display
    return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"


class TransportBar(QWidget):
    play_clicked = Signal()
    pause_clicked = Signal()
    stop_clicked = Signal()
    seek_changed = Signal(int)  # ms

    def __init__(self, parent=None):
        super().__init__(parent)
        self._duration_ms = 0
        self._is_seeking = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        # Back
        self._btn_back = QPushButton("\u23ee")
        self._btn_back.setFixedSize(32, 28)
        self._btn_back.clicked.connect(lambda: self.seek_changed.emit(0))
        layout.addWidget(self._btn_back)

        # Play/Pause
        self._btn_play = QPushButton("\u25b6")
        self._btn_play.setFixedSize(40, 28)
        self._btn_play.setCheckable(True)
        self._btn_play.clicked.connect(self._on_play_toggled)
        layout.addWidget(self._btn_play)

        # Stop
        self._btn_stop = QPushButton("\u23f9")
        self._btn_stop.setFixedSize(32, 28)
        self._btn_stop.clicked.connect(self._on_stop)
        layout.addWidget(self._btn_stop)

        # Forward
        self._btn_fwd = QPushButton("\u23ed")
        self._btn_fwd.setFixedSize(32, 28)
        self._btn_fwd.clicked.connect(lambda: self.seek_changed.emit(self._duration_ms))
        layout.addWidget(self._btn_fwd)

        layout.addSpacing(8)

        # Timecode display
        self._timecode = QLabel("00:00:00:00")
        self._timecode.setStyleSheet("color: #00ff00; font-family: 'Consolas'; font-size: 14px;")
        self._timecode.setFixedWidth(110)
        layout.addWidget(self._timecode)

        # Seek slider
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(0, 1000)
        self._slider.sliderPressed.connect(self._on_slider_pressed)
        self._slider.sliderReleased.connect(self._on_slider_released)
        self._slider.sliderMoved.connect(self._on_slider_moved)
        layout.addWidget(self._slider)

        # Duration label
        self._duration_label = QLabel("/ 00:00:00")
        self._duration_label.setStyleSheet("color: #888888;")
        layout.addWidget(self._duration_label)

    def _on_play_toggled(self, checked):
        if checked:
            self._btn_play.setText("\u23f8")
            self.play_clicked.emit()
        else:
            self._btn_play.setText("\u25b6")
            self.pause_clicked.emit()

    def _on_stop(self):
        self._btn_play.setChecked(False)
        self._btn_play.setText("\u25b6")
        self.stop_clicked.emit()

    def _on_slider_pressed(self):
        self._is_seeking = True

    def _on_slider_released(self):
        self._is_seeking = False
        if self._duration_ms > 0:
            ms = int(self._slider.value() / 1000 * self._duration_ms)
            self.seek_changed.emit(ms)

    def _on_slider_moved(self, value):
        if self._duration_ms > 0:
            ms = int(value / 1000 * self._duration_ms)
            self._timecode.setText(ms_to_timecode(ms))

    def update_position(self, ms: int):
        self._timecode.setText(ms_to_timecode(ms))
        if not self._is_seeking and self._duration_ms > 0:
            pos = int(ms / self._duration_ms * 1000)
            self._slider.setValue(pos)

    def update_duration(self, ms: int):
        self._duration_ms = ms
        self._duration_label.setText(f"/ {ms_to_timecode(ms)}")

    def set_playing(self, is_playing: bool):
        self._btn_play.setChecked(is_playing)
        self._btn_play.setText("\u23f8" if is_playing else "\u25b6")
