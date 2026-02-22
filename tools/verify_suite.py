import sys
import os
import traceback
from PySide6.QtWidgets import QApplication

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def verify():
    with open("verify_result.log", "w", encoding="utf-8") as f:
        def log(msg):
            print(msg, flush=True)
            f.write(msg + "\n")
            
        app = None
        try:
            log("Initializing QApplication...")
            app = QApplication(sys.argv)
        except Exception as e:
            log(f"FAIL: QApplication Init - {e}")
            traceback.print_exc(file=f)
            return

        log("Importing Image Editor...")
        try:
            # Import dynamically to avoid top-level import errors
            import apps.image.ui.main
            # Instantiate
            # Note: MainWindow might require QApplication instance to be running? No, instantiating is usually fine.
            from apps.image.ui.main import MainWindow
            mw = MainWindow()
            log("PASS: Image Editor Instantiation")
        except Exception as e:
            log(f"FAIL: Image Editor Error - {e}")
            traceback.print_exc(file=f)
            return

        log("Importing Launcher...")
        try:
            from launcher.main import CreativeSuiteLauncher
            launcher = CreativeSuiteLauncher()
            log("PASS: Launcher Instantiation")
        except Exception as e:
            log(f"FAIL: Launcher Instantiation - {e}")
            traceback.print_exc(file=f)
            return

        log("Importing Video Editor...")
        try:
            from apps.video.main import VideoEditorWindow
            video = VideoEditorWindow()
            log("PASS: Video Editor Instantiation")
        except Exception as e:
            log(f"FAIL: Video Editor Instantiation - {e}")
            traceback.print_exc(file=f)
            return

        log("Importing Vector Editor...")
        try:
            from apps.vector.main import VectorEditorWindow
            vector = VectorEditorWindow()
            log("PASS: Vector Editor Instantiation")
        except Exception as e:
            log(f"FAIL: Vector Editor Instantiation - {e}")
            traceback.print_exc(file=f)
            return
        
        log("ALL CHECKS PASSED")

if __name__ == "__main__":
    verify()
