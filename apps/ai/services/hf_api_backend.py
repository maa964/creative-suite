"""Hugging Face Inference API backend implementations."""

import logging
from pathlib import Path
from typing import Optional, Callable

from apps.ai.models import TextToImageParams, SpeechToTextParams, BackgroundRemovalParams
from apps.ai.services.base import (
    TextToImageServiceBase,
    SpeechToTextServiceBase,
    BackgroundRemovalServiceBase,
)

LOG = logging.getLogger("creative.ai.hf_api")


class HFApiTextToImage(TextToImageServiceBase):
    def __init__(self, api_key: str):
        self._api_key = api_key

    def generate(self, params: TextToImageParams, output_path: Path,
                 progress_callback: Optional[Callable[[int], None]] = None) -> Path:
        from huggingface_hub import InferenceClient

        client = InferenceClient(token=self._api_key)
        if progress_callback:
            progress_callback(10)

        image = client.text_to_image(
            prompt=params.prompt,
            negative_prompt=params.negative_prompt or None,
            model=params.model_id,
            width=params.width,
            height=params.height,
            num_inference_steps=params.num_inference_steps,
            guidance_scale=params.guidance_scale,
        )
        if progress_callback:
            progress_callback(90)

        image.save(str(output_path), format="PNG")
        if progress_callback:
            progress_callback(100)
        return output_path

    def available_models(self) -> list[str]:
        return [
            "stabilityai/stable-diffusion-2-1",
            "stabilityai/stable-diffusion-xl-base-1.0",
            "runwayml/stable-diffusion-v1-5",
        ]


class HFApiSpeechToText(SpeechToTextServiceBase):
    def __init__(self, api_key: str):
        self._api_key = api_key

    def transcribe(self, params: SpeechToTextParams,
                   progress_callback: Optional[Callable[[int], None]] = None) -> str:
        from huggingface_hub import InferenceClient

        client = InferenceClient(token=self._api_key)
        if progress_callback:
            progress_callback(10)

        result = client.automatic_speech_recognition(
            audio=str(params.audio_path),
            model="openai/whisper-large-v3",
        )
        if progress_callback:
            progress_callback(100)
        return result.text if hasattr(result, "text") else str(result)


class HFApiBackgroundRemoval(BackgroundRemovalServiceBase):
    def __init__(self, api_key: str):
        self._api_key = api_key

    def remove_background(self, params: BackgroundRemovalParams, output_path: Path,
                          progress_callback: Optional[Callable[[int], None]] = None) -> Path:
        from huggingface_hub import InferenceClient
        from PIL import Image
        import io

        client = InferenceClient(token=self._api_key)
        if progress_callback:
            progress_callback(10)

        result_image = client.image_segmentation(
            image=str(params.image_path),
            model="briaai/RMBG-1.4",
        )
        if progress_callback:
            progress_callback(90)

        if isinstance(result_image, Image.Image):
            result_image.save(str(output_path), format="PNG")
        else:
            img = Image.open(io.BytesIO(result_image))
            img.save(str(output_path), format="PNG")

        if progress_callback:
            progress_callback(100)
        return output_path
