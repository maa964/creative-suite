"""AI Studio data models."""

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Optional
import uuid


class AIBackendType(Enum):
    HUGGINGFACE_API = auto()
    LOCAL = auto()


class AITaskType(Enum):
    TEXT_TO_IMAGE = auto()
    SPEECH_TO_TEXT = auto()
    BACKGROUND_REMOVAL = auto()


class TaskStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class TextToImageParams:
    prompt: str = ""
    negative_prompt: str = ""
    width: int = 512
    height: int = 512
    num_inference_steps: int = 30
    guidance_scale: float = 7.5
    seed: Optional[int] = None
    model_id: str = "stabilityai/stable-diffusion-2-1"


@dataclass
class SpeechToTextParams:
    audio_path: Path = field(default_factory=Path)
    language: Optional[str] = None
    model_size: str = "base"


@dataclass
class BackgroundRemovalParams:
    image_path: Path = field(default_factory=Path)
    alpha_matting: bool = False
    alpha_matting_foreground_threshold: int = 240
    alpha_matting_background_threshold: int = 10


@dataclass
class AITaskResult:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: AITaskType = AITaskType.TEXT_TO_IMAGE
    status: TaskStatus = TaskStatus.PENDING
    output_path: Optional[Path] = None
    output_text: Optional[str] = None
    error_message: Optional[str] = None
    elapsed_seconds: float = 0.0
