# app/ui/main.py
import sys
import json
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel
from PySide6.QtCore import Qt

from apps.image.core.plugin_host import PluginHost
from apps.core.logging import setup_logging  # 追加

# Use common logging setup
LOG = setup_logging("image_editor")

APP_ROOT = Path(__file__).resolve().parents[3]

def safe_load_plugins(plugin_dir: Path):
    plugins = []
    try:
        if not plugin_dir.exists():
            LOG.info("plugin dir not found: %s", plugin_dir)
            return plugins
        for p in plugin_dir.iterdir():
            if p.is_dir() and (p / "plugin.json").exists():
                try:
                    cfg = json.loads((p / "plugin.json").read_text(encoding="utf-8"))
                    # minimal validation
                    if "name" not in cfg or "entry" not in cfg:
                        LOG.warning("invalid plugin manifest: %s", p)
                        continue
                    plugins.append((p.name, cfg))
                except Exception as e:
                    LOG.exception("failed to load plugin %s: %s", p, e)
    except Exception as e:
        LOG.exception("plugin scanning failed: %s", e)
    return plugins

from PySide6.QtGui import QAction, QKeySequence

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CreativeStudio Prototype")
        self.setMinimumSize(900, 600)
        
        self.setup_menu()

        try:
            self.label = QLabel("Welcome to CreativeStudio (Prototype)\nplugins will be listed in app.log", alignment=Qt.AlignCenter)
            self.setCentralWidget(self.label)
            plugins = safe_load_plugins(APP_ROOT / "plugins")
            LOG.info("loaded plugins: %s", [p[0] for p in plugins])

            # PluginHost を使って登録（ホスト側で例外吸収・ログ化）
            try:
                host = PluginHost(APP_ROOT / 'plugins', app_api={'name':'CreativeStudioHost'})
                reg = host.register_all()
                LOG.info('plugin host registration results: %s', reg)
            except Exception as e:
                LOG.exception('PluginHost registration error: %s', e)

        except Exception as e:
            LOG.exception("UI init failed: %s", e)
            QMessageBox.critical(self, "初期化エラー", f"UIの初期化に失敗しました:\n{e}")

    def setup_menu(self):
        menu_bar = self.menuBar()
        
        # File Menu
        file_menu = menu_bar.addMenu("&File")
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help Menu
        help_menu = menu_bar.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    def on_about(self):
        QMessageBox.about(self, "About CreativeStudio",
                          "CreativeStudio (Photo & Paint)\n\nPart of Creative Suite v0.50")

def main():
    try:
        app = QApplication(sys.argv)
        mw = MainWindow()
        mw.show()
        sys.exit(app.exec())
    except Exception as e:
        LOG.exception("fatal error: %s", e)
        # Try to display a dialog if possible, without re-importing QApplication at function scope
        try:
            app_instance = None
            try:
                app_instance = QApplication.instance()
            except Exception:
                app_instance = None

            if 'QMessageBox' in globals() and (app_instance is not None or 'QApplication' in globals()):
                try:
                    QMessageBox.critical(None, "致命的エラー", f"アプリが異常終了しました:\n{e}")
                except Exception:
                    print("fatal (dialog failed):", e)
            else:
                print("fatal:", e)
        except Exception as inner:
            LOG.exception("failed to show fatal dialog: %s", inner)
            print("fatal:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
