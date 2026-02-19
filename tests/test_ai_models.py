"""Unit tests for AI Studio data models."""

from pathlib import Path
from apps.ai.models import (
    AIBackendType, AITaskType, TaskStatus,
    TextToImageParams, SpeechToTextParams, BackgroundRemovalParams,
    AITaskResult,
)


def test_backend_types():
    assert AIBackendType.HUGGINGFACE_API is not None
    assert AIBackendType.LOCAL is not None


def test_task_types():
    types = list(AITaskType)
    assert AITaskType.TEXT_TO_IMAGE in types
    assert AITaskType.SPEECH_TO_TEXT in types
    assert AITaskType.BACKGROUND_REMOVAL in types


def test_task_status_values():
    statuses = list(TaskStatus)
    assert TaskStatus.PENDING in statuses
    assert TaskStatus.RUNNING in statuses
    assert TaskStatus.COMPLETED in statuses
    assert TaskStatus.FAILED in statuses
    assert TaskStatus.CANCELLED in statuses


def test_text_to_image_params_defaults():
    params = TextToImageParams()
    assert params.prompt == ""
    assert params.width == 512
    assert params.height == 512
    assert params.num_inference_steps == 30
    assert params.guidance_scale == 7.5
    assert params.seed is None
    assert "stable-diffusion" in params.model_id


def test_speech_to_text_params_defaults():
    params = SpeechToTextParams()
    assert params.audio_path == Path()
    assert params.language is None
    assert params.model_size == "base"


def test_background_removal_params_defaults():
    params = BackgroundRemovalParams()
    assert params.image_path == Path()
    assert params.alpha_matting is False
    assert params.alpha_matting_foreground_threshold == 240
    assert params.alpha_matting_background_threshold == 10


def test_task_result_unique_ids():
    r1 = AITaskResult()
    r2 = AITaskResult()
    assert r1.id != r2.id


def test_task_result_defaults():
    result = AITaskResult()
    assert result.status == TaskStatus.PENDING
    assert result.output_path is None
    assert result.output_text is None
    assert result.error_message is None
    assert result.elapsed_seconds == 0.0
