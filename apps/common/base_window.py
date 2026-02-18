from PySide6.QtWidgets import QMainWindow, QMenu, QMenuBar, QStatusBar, QMessageBox, QFileDialog
from PySide6.QtGui import QAction, QIcon, QKeySequence, QPalette, QColor
from PySide6.QtCore import Qt

class BaseMainWindow(QMainWindow):
    def __init__(self, title="Creative Suite App", width=1200, height=800):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(width, height)
        
        # Setup Menu Bar
        self.setup_menu()
        
        # Setup Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def setup_menu(self):
        menu_bar = self.menuBar()
        
        # File Menu
        file_menu = menu_bar.addMenu("&File")
        
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.on_new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.on_open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.on_save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu (Placeholder)
        edit_menu = menu_bar.addMenu("&Edit")
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        edit_menu.addAction(undo_action)
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        edit_menu.addAction(redo_action)
        
        # Help Menu
        help_menu = menu_bar.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    # Stub methods to be overridden by child classes
    def on_new_file(self):
        self.status_bar.showMessage("New File created (Stub)")

    def on_open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File")
        if file_path:
            self.status_bar.showMessage(f"Opened: {file_path}")

    def on_save_file(self):
        self.status_bar.showMessage("File Saved (Stub)")

    def on_about(self):
        QMessageBox.about(self, "About Creative Suite",
                          "Creative Suite v0.50\n\nOpen Source Creative Tools Integration Environment")
