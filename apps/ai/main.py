"""AI Studio main window."""

import logging

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QMessageBox

try:
    from apps.common.base_window import BaseMainWindow
except ImportError:
    import sys, os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from apps.common.base_window import BaseMainWindow

from apps.core.config import ConfigManager
from apps.ai.models import AIBackendType, AITaskResult, TaskStatus
from apps.ai.services.availability import check_local_availability
from apps.ai.widgets.text_to_image_panel import TextToImagePanel
from apps.ai.widgets.speech_to_text_panel import SpeechToTextPanel
from apps.ai.widgets.bg_removal_panel import BackgroundRemovalPanel
from apps.ai.widgets.settings_panel import AISettingsPanel

LOG = logging.getLogger("creative.ai")


class AIStudioWindow(BaseMainWindow):
    def __init__(self):
        super().__init__(title="Creative Suite - AI Studio", width=1000, height=700)

        self._config = ConfigManager("ai_studio")
        self._availability = check_local_availability()
        self._current_worker = None

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self._tabs = QTabWidget()

        # Settings
        self._settings_panel = AISettingsPanel(self._config)
        self._settings_panel.backend_changed.connect(self._on_backend_changed)

        # Feature panels
        self._txt2img_panel = TextToImagePanel(
            available_models=self._get_txt2img_models()
        )
        self._txt2img_panel.generate_requested.connect(self._on_txt2img_generate)
        self._txt2img_panel.cancel_requested.connect(self._on_cancel_task)

        self._stt_panel = SpeechToTextPanel()
        self._stt_panel.transcribe_requested.connect(self._on_stt_transcribe)
        self._stt_panel.cancel_requested.connect(self._on_cancel_task)

        self._rmbg_panel = BackgroundRemovalPanel()
        self._rmbg_panel.remove_requested.connect(self._on_rmbg_remove)
        self._rmbg_panel.cancel_requested.connect(self._on_cancel_task)

        self._tabs.addTab(self._txt2img_panel, "Text to Image")
        self._tabs.addTab(self._stt_panel, "Speech to Text")
        self._tabs.addTab(self._rmbg_panel, "Background Removal")
        self._tabs.addTab(self._settings_panel, "Settings")

        main_layout.addWidget(self._tabs)

    def _get_backend_type(self) -> AIBackendType:
        return self._settings_panel.get_backend_type()

    def _get_txt2img_models(self) -> list[str]:
        return [
            "stabilityai/stable-diffusion-2-1",
            "stabilityai/stable-diffusion-xl-base-1.0",
            "runwayml/stable-diffusion-v1-5",
        ]

    def _create_service(self, task_type: str):
        backend = self._get_backend_type()

        if backend == AIBackendType.HUGGINGFACE_API:
            api_key = self._settings_panel.get_api_key()
            if not api_key:
                QMessageBox.warning(
                    self, "API Key Required",
                    "Please set your Hugging Face API key in the Settings tab."
                )
                return None
            from apps.ai.services.hf_api_backend import (
                HFApiTextToImage, HFApiSpeechToText, HFApiBackgroundRemoval
            )
            services = {
                "txt2img": lambda: HFApiTextToImage(api_key),
                "stt": lambda: HFApiSpeechToText(api_key),
                "rmbg": lambda: HFApiBackgroundRemoval(api_key),
            }
        else:
            avail = self._availability
            services = {}
            if avail.text_to_image_available:
                from apps.ai.services.local_backend import LocalTextToImage
                services["txt2img"] = LocalTextToImage
            if avail.speech_to_text_available:
                from apps.ai.services.local_backend import LocalSpeechToText
                services["stt"] = LocalSpeechToText
            if avail.background_removal_available:
                from apps.ai.services.local_backend import LocalBackgroundRemoval
                services["rmbg"] = LocalBackgroundRemoval

        factory = services.get(task_type)
        if factory is None:
            QMessageBox.warning(
                self, "Unavailable",
                "The selected backend does not support this task.\n"
                "Check the Settings tab for dependency status."
            )
            return None
        return factory()

    # --- Text to Image ---

    def _on_txt2img_generate(self, params, output_path):
        service = self._create_service("txt2img")
        if not service:
            return
        from apps.ai.workers import TextToImageWorker
        worker = TextToImageWorker(service, params, output_path, parent=self)
        worker.progress.connect(self._txt2img_panel.set_progress)
        worker.status_message.connect(lambda msg: self.status_bar.showMessage(msg))
        worker.finished_result.connect(self._on_txt2img_result)
        self._txt2img_panel.set_running(True)
        self._current_worker = worker
        worker.start()

    def _on_txt2img_result(self, result: AITaskResult):
        self._txt2img_panel.set_running(False)
        self._current_worker = None
        if result.status == TaskStatus.COMPLETED and result.output_path:
            self._txt2img_panel.show_result(result.output_path)
            self.status_bar.showMessage(
                f"Image generated in {result.elapsed_seconds:.1f}s")
        else:
            self._txt2img_panel.show_error(result.error_message or "Unknown error")
            self.status_bar.showMessage("Image generation failed")

    # --- Speech to Text ---

    def _on_stt_transcribe(self, params):
        service = self._create_service("stt")
        if not service:
            return
        from apps.ai.workers import SpeechToTextWorker
        worker = SpeechToTextWorker(service, params, parent=self)
        worker.progress.connect(self._stt_panel.set_progress)
        worker.status_message.connect(lambda msg: self.status_bar.showMessage(msg))
        worker.finished_result.connect(self._on_stt_result)
        self._stt_panel.set_running(True)
        self._current_worker = worker
        worker.start()

    def _on_stt_result(self, result: AITaskResult):
        self._stt_panel.set_running(False)
        self._current_worker = None
        if result.status == TaskStatus.COMPLETED and result.output_text:
            self._stt_panel.show_result(result.output_text)
            self.status_bar.showMessage(
                f"Transcription completed in {result.elapsed_seconds:.1f}s")
        else:
            self._stt_panel.show_error(result.error_message or "Unknown error")
            self.status_bar.showMessage("Transcription failed")

    # --- Background Removal ---

    def _on_rmbg_remove(self, params, output_path):
        service = self._create_service("rmbg")
        if not service:
            return
        from apps.ai.workers import BackgroundRemovalWorker
        worker = BackgroundRemovalWorker(service, params, output_path, parent=self)
        worker.progress.connect(self._rmbg_panel.set_progress)
        worker.status_message.connect(lambda msg: self.status_bar.showMessage(msg))
        worker.finished_result.connect(self._on_rmbg_result)
        self._rmbg_panel.set_running(True)
        self._current_worker = worker
        worker.start()

    def _on_rmbg_result(self, result: AITaskResult):
        self._rmbg_panel.set_running(False)
        self._current_worker = None
        if result.status == TaskStatus.COMPLETED and result.output_path:
            self._rmbg_panel.show_result(result.output_path)
            self.status_bar.showMessage(
                f"Background removed in {result.elapsed_seconds:.1f}s")
        else:
            self._rmbg_panel.show_error(result.error_message or "Unknown error")
            self.status_bar.showMessage("Background removal failed")

    # --- Common ---

    def _on_cancel_task(self):
        if self._current_worker and self._current_worker.isRunning():
            self._current_worker.cancel()
            self.status_bar.showMessage("Task cancelled")

    def _on_backend_changed(self, backend_str: str):
        self.status_bar.showMessage(f"Backend: {backend_str}")
