
import sys
import os
import logging
from pathlib import Path

from PySide6.QtWidgets import QApplication, QDockWidget, QFileDialog, QMessageBox, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QAction

# Adjust path to find 'apps' module if run directly
if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from apps.common.base_window import BaseMainWindow
from apps.image.core.layer_manager import LayerManager
from apps.image.core.canvas import ImageCanvas, ImageCanvasView
from apps.image.ui.layer_panel import LayerPanel
from apps.image.core.plugin_host import PluginHost
from apps.image.core.project_io import ProjectIO
from apps.core.logging import setup_logging

LOG = setup_logging("image_editor")
APP_ROOT = Path(__file__).resolve().parents[3]

class MainWindow(BaseMainWindow):
    def __init__(self):
        super().__init__(title="Photo & Paint", width=1280, height=800)
        
        # 1. Core Logic
        self.layer_manager = LayerManager(800, 600)
        
        # 2. Central Canvas View
        self.canvas_scene = ImageCanvas(self.layer_manager)
        self.canvas_view = ImageCanvasView(self.canvas_scene)
        self.setCentralWidget(self.canvas_view)
        
        # 3. Docks
        self.layer_panel = LayerPanel(self.layer_manager)
        self.layer_dock = QDockWidget("Layers", self)
        self.layer_dock.setWidget(self.layer_panel)
        self.layer_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.layer_dock)
        
        # 4. Plugins
        self._init_plugins()
        
        self.status_bar.showMessage("Ready")

    def _init_plugins(self):
        try:
            plugins_dir = APP_ROOT / "plugins"
            if plugins_dir.exists():
                self.plugin_host = PluginHost(plugins_dir, app_api={'name': 'CreativeStudioHost'})
                results = self.plugin_host.register_all()
                LOG.info(f"Plugins loaded: {results}")
                if results:
                    self.status_bar.showMessage(f"Loaded {len(results)} plugins")
            else:
                LOG.warning(f"Plugins directory not found: {plugins_dir}")
        except Exception as e:
            LOG.exception("Failed to initialize plugins")
            self.status_bar.showMessage("Plugin load failed")

    def on_new_file(self):
        self.layer_manager = LayerManager(800, 600)
        self.canvas_scene = ImageCanvas(self.layer_manager)
        self.canvas_view.setScene(self.canvas_scene)
        
        # Re-create panel to bind to new manager
        self.layer_dock.setWidget(None)
        self.layer_panel = LayerPanel(self.layer_manager)
        self.layer_dock.setWidget(self.layer_panel)
        
        self.status_bar.showMessage("New canvas created (800x600)")

    def on_open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", 
            "Images/Projects (*.png *.jpg *.jpeg *.bmp *.svg *.webp *.csp *.json);;All Files (*)"
        )
        if not file_path:
            return

        if file_path.endswith(".csp") or file_path.endswith(".json"):
            # Load Project
            try:
                new_manager = ProjectIO.load_project(file_path)
                self.layer_manager = new_manager
                self.canvas_scene = ImageCanvas(self.layer_manager)
                self.canvas_view.setScene(self.canvas_scene)
                
                # Re-bind UI
                self.layer_dock.setWidget(None)
                self.layer_panel = LayerPanel(self.layer_manager)
                self.layer_dock.setWidget(self.layer_panel)

                self.status_bar.showMessage(f"Project loaded: {file_path}")
            except Exception as e:
                LOG.exception("Failed to load project")
                QMessageBox.critical(self, "Load Error", f"Failed to load project:\n{e}")
        else:
            # Import Image as Layer
            image = QImage(file_path)
            if not image.isNull():
                self.layer_manager.add_image_layer(image, os.path.basename(file_path))
                self.status_bar.showMessage(f"Imported layer: {file_path}")
            else:
                QMessageBox.warning(self, "Error", "Failed to load image file.")
                self.status_bar.showMessage("Open failed")

    def on_save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project", "", 
            "Creative Studio Project (*.csp);;JSON (*.json)"
        )
        if file_path:
            try:
                ProjectIO.save_project(self.layer_manager, file_path)
                self.status_bar.showMessage(f"Project saved: {file_path}")
            except Exception as e:
                LOG.exception("Failed to save project")
                QMessageBox.critical(self, "Save Error", f"Failed to save project:\n{e}")


def main():
    app = QApplication(sys.argv)
    
    # Apply theme/style here if needed
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
