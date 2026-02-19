"""Video preview widget using QMediaPlayer + QVideoWidget."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import Signal, QUrl, Qt


class VideoPreviewWidget(QWidget):
    position_changed = Signal(int)      # ms
    duration_changed = Signal(int)      # ms
    playback_state_changed = Signal(bool)  # is_playing

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._video_widget = QVideoWidget()
        self._video_widget.setMinimumSize(320, 180)

        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._player.setVideoOutput(self._video_widget)
        self._player.setAudioOutput(self._audio_output)

        # Placeholder label (shown when no media loaded)
        self._placeholder = QLabel("Video Preview")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setStyleSheet(
            "background-color: #000000; color: #666666; font-size: 18px;"
        )
        self._placeholder.setMinimumSize(320, 180)

        layout.addWidget(self._placeholder)
        layout.addWidget(self._video_widget)
        self._video_widget.hide()

        # Forward signals
        self._player.positionChanged.connect(self.position_changed.emit)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.playbackStateChanged.connect(self._on_state_changed)

        self._current_path = ""

    def load_media(self, path: str):
        self._current_path = path
        self._player.setSource(QUrl.fromLocalFile(path))
        self._placeholder.hide()
        self._video_widget.show()

    def play(self):
        self._player.play()

    def pause(self):
        self._player.pause()

    def stop(self):
        self._player.stop()

    def seek(self, ms: int):
        self._player.setPosition(ms)

    def is_playing(self) -> bool:
        return self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def duration(self) -> int:
        return self._player.duration()

    def _on_duration_changed(self, duration: int):
        self.duration_changed.emit(duration)

    def _on_state_changed(self, state):
        is_playing = (state == QMediaPlayer.PlaybackState.PlayingState)
        self.playback_state_changed.emit(is_playing)
