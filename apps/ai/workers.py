"""QThread workers for long-running AI tasks."""

import time
import logging
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from apps.ai.models import (
    AITaskResult, AITaskType, TaskStatus,
    TextToImageParams, SpeechToTextParams, BackgroundRemovalParams,
)
from apps.ai.services.base import (
    TextToImageServiceBase,
    SpeechToTextServiceBase,
    BackgroundRemovalServiceBase,
)

LOG = logging.getLogger("creative.ai.workers")


class AIWorker(QThread):
    progress = Signal(int)
    finished_result = Signal(object)
    status_message = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cancelled = False

    def cancel(self):
        self._cancelled = True


class TextToImageWorker(AIWorker):
    def __init__(self, service: TextToImageServiceBase,
                 params: TextToImageParams, output_path: Path, parent=None):
        super().__init__(parent)
        self._service = service
        self._params = params
        self._output_path = output_path

    def run(self):
        result = AITaskResult(task_type=AITaskType.TEXT_TO_IMAGE, status=TaskStatus.RUNNING)
        self.status_message.emit("Generating image...")
        start = time.time()
        try:
            path = self._service.generate(
                self._params, self._output_path,
                progress_callback=lambda p: self.progress.emit(p),
            )
            result.status = TaskStatus.COMPLETED
            result.output_path = path
        except Exception as e:
            LOG.exception("Text-to-image failed: %s", e)
            result.status = TaskStatus.FAILED
            result.error_message = str(e)
        result.elapsed_seconds = time.time() - start
        self.finished_result.emit(result)


class SpeechToTextWorker(AIWorker):
    def __init__(self, service: SpeechToTextServiceBase,
                 params: SpeechToTextParams, parent=None):
        super().__init__(parent)
        self._service = service
        self._params = params

    def run(self):
        result = AITaskResult(task_type=AITaskType.SPEECH_TO_TEXT, status=TaskStatus.RUNNING)
        self.status_message.emit("Transcribing audio...")
        start = time.time()
        try:
            text = self._service.transcribe(
                self._params,
                progress_callback=lambda p: self.progress.emit(p),
            )
            result.status = TaskStatus.COMPLETED
            result.output_text = text
        except Exception as e:
            LOG.exception("Speech-to-text failed: %s", e)
            result.status = TaskStatus.FAILED
            result.error_message = str(e)
        result.elapsed_seconds = time.time() - start
        self.finished_result.emit(result)


class BackgroundRemovalWorker(AIWorker):
    def __init__(self, service: BackgroundRemovalServiceBase,
                 params: BackgroundRemovalParams, output_path: Path, parent=None):
        super().__init__(parent)
        self._service = service
        self._params = params
        self._output_path = output_path

    def run(self):
        result = AITaskResult(task_type=AITaskType.BACKGROUND_REMOVAL, status=TaskStatus.RUNNING)
        self.status_message.emit("Removing background...")
        start = time.time()
        try:
            path = self._service.remove_background(
                self._params, self._output_path,
                progress_callback=lambda p: self.progress.emit(p),
            )
            result.status = TaskStatus.COMPLETED
            result.output_path = path
        except Exception as e:
            LOG.exception("Background removal failed: %s", e)
            result.status = TaskStatus.FAILED
            result.error_message = str(e)
        result.elapsed_seconds = time.time() - start
        self.finished_result.emit(result)
