from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QScrollArea, QFrame, QPushButton, QSlider, QSplitter)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QPalette, QIcon

# Import BaseMainWindow dynamically if needed
try:
    from apps.common.base_window import BaseMainWindow
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from apps.common.base_window import BaseMainWindow

class TimelineTrack(QFrame):
    def __init__(self, name, color):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setFixedHeight(50)
        self.setStyleSheet(f"background-color: #333333; border: 1px solid #444444;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QLabel(name)
        header.setFixedWidth(100)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("background-color: #2a2a2a; color: #aaaaaa; border-right: 1px solid #444444;")
        layout.addWidget(header)
        
        # Clip area
        self.clip_area = QWidget()
        self.clip_area.setStyleSheet(f"background-color: {color}; opacity: 0.3;")
        layout.addWidget(self.clip_area)

class TimelineWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Set a minimum width to ensure scrolling works
        self.setMinimumWidth(2000)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        
        # Time Ruler
        ruler = QLabel("00:00:00     |     00:00:05     |     00:00:10     |     00:00:15     |     00:00:20")
        ruler.setFixedHeight(20)
        ruler.setStyleSheet("background-color: #222222; color: #888888; padding-left: 100px;")
        layout.addWidget(ruler)
        
        # Tracks
        layout.addWidget(TimelineTrack("V1", "#34495e")) # Dark Blue
        layout.addWidget(TimelineTrack("V2", "#34495e"))
        layout.addWidget(TimelineTrack("A1", "#2c3e50")) # Darker Blue
        layout.addWidget(TimelineTrack("A2", "#2c3e50"))
        
        layout.addStretch()

class VideoPreviewWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setText("Video Preview\n(MLT Backend Placeholder)")
        self.setStyleSheet("background-color: #000000; color: #ffffff; font-size: 20px;")
        self.setMinimumSize(320, 180)

class VideoEditorWindow(BaseMainWindow):
    def __init__(self):
        super().__init__(title="Creative Suite - Video Editor", width=1280, height=720)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main Splitter (Vertical: Top [Assets+Preview] / Bottom [Timeline])
        v_splitter = QSplitter(Qt.Vertical)
        
        # Top Splitter (Horizontal: Assets / Preview)
        h_splitter = QSplitter(Qt.Horizontal)
        
        # Assets Panel
        assets = QLabel("Project Bin\n(Drag clips here)")
        assets.setStyleSheet("background-color: #252525; border: 1px solid #333333; color: #888888;")
        assets.setAlignment(Qt.AlignCenter)
        assets.setMinimumWidth(200)
        
        # Preview
        self.preview = VideoPreviewWidget()
        
        h_splitter.addWidget(assets)
        h_splitter.addWidget(self.preview)
        h_splitter.setStretchFactor(1, 2) # Make preview wider
        
        v_splitter.addWidget(h_splitter)
        
        # Timeline Area
        timeline_container = QWidget()
        timeline_layout = QVBoxLayout(timeline_container)
        timeline_layout.setContentsMargins(0, 0, 0, 0)
        
        # Controls Bar
        controls = QHBoxLayout()
        controls.setContentsMargins(10, 5, 10, 5)
        
        self.btn_play = QPushButton("▶")
        self.btn_play.setCheckable(True)
        self.btn_play.clicked.connect(self.toggle_playback)
        self.btn_play.setFixedSize(40, 30)
        
        controls.addWidget(QPushButton("⏮"))
        controls.addWidget(self.btn_play)
        controls.addWidget(QPushButton("⏭"))
        
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(0, 1000)
        self.time_slider.valueChanged.connect(self.on_seek)
        controls.addWidget(self.time_slider)
        
        timeline_layout.addLayout(controls)
        
        # Scrollable Timeline
        timeline_scroll = QScrollArea()
        timeline_scroll.setWidgetResizable(True)
        timeline_scroll.setWidget(TimelineWidget())
        timeline_layout.addWidget(timeline_scroll)
        
        v_splitter.addWidget(timeline_container)
        v_splitter.setStretchFactor(1, 1) # Equal weight initially or timeline smaller
        
        main_layout.addWidget(v_splitter)

    def toggle_playback(self, checked):
        if checked:
            self.btn_play.setText("⏸")
            self.status_bar.showMessage("Playing...")
        else:
            self.btn_play.setText("▶")
            self.status_bar.showMessage("Paused")
            
    def on_seek(self, value):
        # Stub for seeking
        self.status_bar.showMessage(f"Seek: {value}")

    def on_open_file(self):
        # Override BaseMainWindow stub
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Media", "", "Video Files (*.mp4 *.mov *.avi);;All Files (*)")
        if file_path:
            self.status_bar.showMessage(f"Imported: {file_path}")

