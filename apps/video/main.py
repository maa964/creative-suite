from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QScrollArea, QFrame, QPushButton, QSlider)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QPalette

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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        
        # Time Ruler
        ruler = QLabel("00:00:00     |     00:00:05     |     00:00:10     |     00:00:15")
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
        self.setMinimumSize(640, 360)

class VideoEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Creative Suite - Video Editor")
        self.resize(1280, 720)
        
        # Theme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#1e1e1e"))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Top Section: Preview and Assets
        top_layout = QHBoxLayout()
        
        # Assets Panel
        assets = QLabel("Project Bin")
        assets.setFixedWidth(300)
        assets.setStyleSheet("background-color: #252525; border: 1px solid #333333;")
        assets.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(assets)
        
        # Preview
        preview = VideoPreviewWidget()
        top_layout.addWidget(preview, 1) # Stretch
        
        main_layout.addLayout(top_layout, 2) # 2/3 height
        
        # Controls
        controls = QHBoxLayout()
        controls.addWidget(QPushButton("⏮"))
        controls.addWidget(QPushButton("⏯"))
        controls.addWidget(QPushButton("⏭"))
        controls.addWidget(QSlider(Qt.Horizontal))
        main_layout.addLayout(controls)
        
        # Timeline
        timeline_scroll = QScrollArea()
        timeline_scroll.setWidgetResizable(True)
        timeline_scroll.setWidget(TimelineWidget())
        main_layout.addWidget(timeline_scroll, 1) # 1/3 height
