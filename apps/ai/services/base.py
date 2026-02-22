"""Abstract base classes for AI services."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Callable

from apps.ai.models import (
    TextToImageParams,
    SpeechToTextParams,
    BackgroundRemovalParams,
)


class TextToImageServiceBase(ABC):
    @abstractmethod
    def generate(
        self,
        params: TextToImageParams,
        output_path: Path,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> Path:
        ...

    @abstractmethod
    def available_models(self) -> list[str]:
        ...


class SpeechToTextServiceBase(ABC):
    @abstractmethod
    def transcribe(
        self,
        params: SpeechToTextParams,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> str:
        ...


class BackgroundRemovalServiceBase(ABC):
    @abstractmethod
    def remove_background(
        self,
        params: BackgroundRemovalParams,
        output_path: Path,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> Path:
        ...
