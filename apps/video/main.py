"""Video Editor main window."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QSplitter, QFileDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence

try:
    from apps.common.base_window import BaseMainWindow
except ImportError:
    import sys, os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from apps.common.base_window import BaseMainWindow

from apps.video.models import VideoProject
from apps.video.preview_widget import VideoPreviewWidget
from apps.video.project_bin import ProjectBinWidget
from apps.video.timeline_widget import TimelineWidget
from apps.video.transport import TransportBar


class VideoEditorWindow(BaseMainWindow):
    def __init__(self):
        super().__init__(title="Creative Suite - Video Editor", width=1280, height=720)

        self.project = VideoProject()
        self.project.add_default_tracks()

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Top area: Assets + Preview ---
        v_splitter = QSplitter(Qt.Vertical)

        h_splitter = QSplitter(Qt.Horizontal)

        # Project Bin
        self._bin = ProjectBinWidget(self.project)
        self._bin.setMinimumWidth(200)
        self._bin.media_double_clicked.connect(self._on_media_preview)

        # Preview
        self._preview = VideoPreviewWidget()

        h_splitter.addWidget(self._bin)
        h_splitter.addWidget(self._preview)
        h_splitter.setStretchFactor(1, 2)

        v_splitter.addWidget(h_splitter)

        # --- Bottom area: Transport + Timeline ---
        bottom = QWidget()
        bottom_layout = QVBoxLayout(bottom)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)

        # Transport bar
        self._transport = TransportBar()
        bottom_layout.addWidget(self._transport)

        # Timeline
        self._timeline = TimelineWidget(self.project)
        bottom_layout.addWidget(self._timeline)

        v_splitter.addWidget(bottom)
        v_splitter.setStretchFactor(0, 2)
        v_splitter.setStretchFactor(1, 1)

        main_layout.addWidget(v_splitter)

        # --- Signal wiring ---
        self._wire_signals()

        # --- Menu additions ---
        self._setup_extra_menus()

    def _wire_signals(self):
        # Preview -> Transport (position update)
        self._preview.position_changed.connect(self._transport.update_position)
        self._preview.position_changed.connect(self._timeline.set_playhead)
        self._preview.duration_changed.connect(self._transport.update_duration)
        self._preview.playback_state_changed.connect(self._transport.set_playing)

        # Transport -> Preview (controls)
        self._transport.play_clicked.connect(self._preview.play)
        self._transport.pause_clicked.connect(self._preview.pause)
        self._transport.stop_clicked.connect(self._preview.stop)
        self._transport.seek_changed.connect(self._preview.seek)
        self._transport.seek_changed.connect(self._timeline.set_playhead)

        # Timeline -> Preview (playhead seek)
        self._timeline.playhead_moved.connect(self._preview.seek)

    def _setup_extra_menus(self):
        menu_bar = self.menuBar()
        view_menu = menu_bar.addMenu("&View")

        zoom_in = QAction("Timeline Zoom &In", self)
        zoom_in.setShortcut(QKeySequence("Ctrl+="))
        zoom_in.triggered.connect(self._timeline.zoom_in)
        view_menu.addAction(zoom_in)

        zoom_out = QAction("Timeline Zoom &Out", self)
        zoom_out.setShortcut(QKeySequence("Ctrl+-"))
        zoom_out.triggered.connect(self._timeline.zoom_out)
        view_menu.addAction(zoom_out)

    def _on_media_preview(self, media_id: str):
        media = self.project.get_media_item(media_id)
        if media and media.media_type == "video":
            self._preview.load_media(str(media.file_path))
            self.status_bar.showMessage(f"Preview: {media.name}")

    def on_new_file(self):
        self.project = VideoProject()
        self.project.add_default_tracks()
        self._timeline.set_project(self.project)
        self._bin.set_project(self.project)
        self._preview.stop()
        self.status_bar.showMessage("New project created")

    def on_open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Media", "",
            "Media Files (*.mp4 *.mov *.avi *.mkv *.webm *.mp3 *.wav *.png *.jpg);;All Files (*)"
        )
        if file_path:
            self._bin.import_file(file_path)
            self.status_bar.showMessage(f"Imported: {file_path}")
