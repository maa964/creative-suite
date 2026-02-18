import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPalette

# Ensure the root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from apps.core.logging import setup_logging
    from apps.common.theme import apply_dark_theme
except ImportError:
    pass

class LauncherButton(QPushButton):
    def __init__(self, title, description, color, icon_text, callback):
        super().__init__()
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(180)
        self.callback = callback
        
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon/Symbol
        icon_label = QLabel(icon_text)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        icon_label.setStyleSheet(f"color: {color};")
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #ffffff;")
        
        # Description
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setFont(QFont("Segoe UI", 10))
        desc_label.setStyleSheet("color: #aaaaaa;")
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        
        # Style
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #2b2b2b;
                border: 2px solid #333333;
                border-radius: 15px;
            }}
            QPushButton:hover {{
                background-color: #333333;
                border: 2px solid {color};
            }}
            QPushButton:pressed {{
                background-color: #222222;
            }}
        """)
        
        self.clicked.connect(self.callback)

class CreativeSuiteLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Creative Suite Hub")
        self.setMinimumSize(900, 600)
        
        # Setup Dark Theme
        apply_dark_theme(QApplication.instance())
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(30)
        
        # Header
        header_layout = QVBoxLayout()
        title = QLabel("Creative Suite")
        title.setFont(QFont("Segoe UI", 36, QFont.Bold))
        title.setStyleSheet("color: #ffffff;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Open Source Creative Platform")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet("color: #888888;")
        subtitle.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)
        
        # Grid of Apps
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(20)
        
        # Image Editor Button
        self.btn_image = LauncherButton(
            "Photo & Paint",
            "Advanced Layer-based Image Editing\n(PySide6 Core)",
            "#3498db", # Blue
            "🖼️",
            self.launch_image_editor
        )
        
        # Video Editor Button
        self.btn_video = LauncherButton(
            "Video Editor",
            "Pro-level Video Editing & Sequencing\n(MLT + Timeline)",
            "#9b59b6", # Purple
            "🎬",
            self.launch_video_editor
        )
        
        # Vector Editor Button
        self.btn_vector = LauncherButton(
            "Vector Draw",
            "Scalable Vector Graphics Design\n(SVG + Bezier)",
            "#e67e22", # Orange
            "✒️",
            self.launch_vector_editor
        )
        
        grid_layout.addWidget(self.btn_image)
        grid_layout.addWidget(self.btn_video)
        grid_layout.addWidget(self.btn_vector)
        
        main_layout.addStretch()
        main_layout.addLayout(grid_layout)
        main_layout.addStretch()
        
        # Footer
        footer = QLabel("v0.2.0-alpha • Powered by Python & Qt")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #444444;")
        main_layout.addWidget(footer)
        
    def launch_image_editor(self):
        print("Launching Image Editor...")
        try:
            from apps.image.ui.main import MainWindow as ImageEditorWindow
            self.image_window = ImageEditorWindow()
            self.image_window.show()
        except Exception as e:
            print(f"Error launching Image Editor: {e}")
            import traceback
            traceback.print_exc()

    def launch_video_editor(self):
        print("Launching Video Editor...")
        try:
            from apps.video.main import VideoEditorWindow
            self.video_window = VideoEditorWindow()
            self.video_window.show()
        except Exception as e:
            print(f"Error launching Video Editor: {e}")
            import traceback
            traceback.print_exc()

    def launch_vector_editor(self):
        print("Launching Vector Editor...")
        try:
            from apps.vector.main import VectorEditorWindow
            self.vector_window = VectorEditorWindow()
            self.vector_window.show()
        except Exception as e:
            print(f"Error launching Vector Editor: {e}")
            import traceback
            traceback.print_exc()

def main():
    app = QApplication(sys.argv)
    
    # Use common logging
    try:
        from apps.core.logging import setup_logging
        setup_logging("launcher")
    except ImportError:
        print("Could not import setup_logging")

    window = CreativeSuiteLauncher()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
