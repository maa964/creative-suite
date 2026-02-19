"""Project bin widget for importing and managing media files."""

from pathlib import Path

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                                QListWidget, QListWidgetItem, QPushButton,
                                QFileDialog, QLabel)
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag

from apps.video.models import VideoProject, MediaItem

MEDIA_FILTER = (
    "Media Files (*.mp4 *.mov *.avi *.mkv *.webm *.mp3 *.wav *.ogg *.flac "
    "*.png *.jpg *.jpeg *.bmp *.gif);;"
    "Video (*.mp4 *.mov *.avi *.mkv *.webm);;"
    "Audio (*.mp3 *.wav *.ogg *.flac);;"
    "Image (*.png *.jpg *.jpeg *.bmp *.gif);;"
    "All Files (*)"
)

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".flac"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}


def _detect_media_type(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in VIDEO_EXTS:
        return "video"
    elif ext in AUDIO_EXTS:
        return "audio"
    elif ext in IMAGE_EXTS:
        return "image"
    return "video"


class DraggableListWidget(QListWidget):
    """QListWidget that supports drag initiation for media items."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setSelectionMode(QListWidget.SingleSelection)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item:
            return
        media_id = item.data(Qt.UserRole)
        if not media_id:
            return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setData("application/x-creative-suite-media-id", media_id.encode("utf-8"))
        drag.setMimeData(mime)
        drag.exec(Qt.CopyAction)


class ProjectBinWidget(QWidget):
    media_selected = Signal(str)  # media_item_id
    media_double_clicked = Signal(str)  # media_item_id — preview

    def __init__(self, project: VideoProject, parent=None):
        super().__init__(parent)
        self._project = project
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        header = QLabel("Project Bin")
        header.setStyleSheet("font-weight: bold; color: #aaaaaa; padding: 4px;")
        layout.addWidget(header)

        self._import_btn = QPushButton("Import Media")
        self._import_btn.clicked.connect(self._on_import)
        layout.addWidget(self._import_btn)

        self._list = DraggableListWidget()
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._list)

        self.setStyleSheet("background-color: #252525; border: 1px solid #333333;")

    def _on_import(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Import Media", "", MEDIA_FILTER
        )
        for f in files:
            self._add_file(Path(f))

    def _add_file(self, path: Path):
        media_type = _detect_media_type(path)
        # Default duration for images: 5 seconds
        duration = 5000 if media_type == "image" else 10000
        item = self._project.add_media(path, duration_ms=duration, media_type=media_type)
        self._add_list_item(item)

    def _add_list_item(self, media: MediaItem):
        prefix = {"video": "[V]", "audio": "[A]", "image": "[I]"}.get(media.media_type, "[?]")
        list_item = QListWidgetItem(f"{prefix} {media.name}")
        list_item.setData(Qt.UserRole, media.id)
        self._list.addItem(list_item)

    def _on_item_clicked(self, item: QListWidgetItem):
        media_id = item.data(Qt.UserRole)
        if media_id:
            self.media_selected.emit(media_id)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        media_id = item.data(Qt.UserRole)
        if media_id:
            self.media_double_clicked.emit(media_id)

    def set_project(self, project: VideoProject):
        self._project = project
        self._list.clear()

    def import_file(self, path: str):
        self._add_file(Path(path))
