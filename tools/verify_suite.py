import sys
import os
from PySide6.QtWidgets import QApplication

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def verify():
    print("Initializing QApplication...")
    app = QApplication(sys.argv)
    
    print("Importing Image Editor...")
    try:
        from app.ui.main import MainWindow as ImageEditor
        # Just instantiate strictly to check for import/init errors, don't show
        # Need to mock any strict dependencies if they fail, but let's try real first
        print("PASS: Image Editor Import")
    except ImportError as e:
        print(f"FAIL: Image Editor Import - {e}")
        return

    print("Importing Launcher...")
    try:
        from launcher.main import CreativeSuiteLauncher
        launcher = CreativeSuiteLauncher()
        print("PASS: Launcher Instantiation")
    except Exception as e:
        print(f"FAIL: Launcher Instantiation - {e}")
        import traceback
        traceback.print_exc()
        return

    print("Importing Video Editor...")
    try:
        from apps.video.main import VideoEditorWindow
        video = VideoEditorWindow()
        print("PASS: Video Editor Instantiation")
    except Exception as e:
        print(f"FAIL: Video Editor Instantiation - {e}")
        traceback.print_exc()
        return

    print("Importing Vector Editor...")
    try:
        from apps.vector.main import VectorEditorWindow
        vector = VectorEditorWindow()
        print("PASS: Vector Editor Instantiation")
    except Exception as e:
        print(f"FAIL: Vector Editor Instantiation - {e}")
        traceback.print_exc()
        return
    
    print("ALL CHECKS PASSED")

if __name__ == "__main__":
    verify()
