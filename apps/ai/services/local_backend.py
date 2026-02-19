"""Local model execution backend implementations."""

import logging
from pathlib import Path
from typing import Optional, Callable

from apps.ai.models import TextToImageParams, SpeechToTextParams, BackgroundRemovalParams
from apps.ai.services.base import (
    TextToImageServiceBase,
    SpeechToTextServiceBase,
    BackgroundRemovalServiceBase,
)

LOG = logging.getLogger("creative.ai.local")


class LocalTextToImage(TextToImageServiceBase):
    def __init__(self):
        self._pipe = None
        self._current_model = ""

    def generate(self, params: TextToImageParams, output_path: Path,
                 progress_callback: Optional[Callable[[int], None]] = None) -> Path:
        import torch
        from diffusers import StableDiffusionPipeline

        if progress_callback:
            progress_callback(5)

        if self._pipe is None or self._current_model != params.model_id:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if device == "cuda" else torch.float32
            self._pipe = StableDiffusionPipeline.from_pretrained(
                params.model_id, torch_dtype=dtype
            )
            self._pipe.to(device)
            self._current_model = params.model_id

        if progress_callback:
            progress_callback(20)

        generator = None
        if params.seed is not None:
            generator = torch.Generator(device=self._pipe.device).manual_seed(params.seed)

        def step_callback(pipe, step, timestep, kwargs):
            if progress_callback:
                pct = 20 + int((step / params.num_inference_steps) * 70)
                progress_callback(min(pct, 90))
            return kwargs

        result = self._pipe(
            prompt=params.prompt,
            negative_prompt=params.negative_prompt or None,
            width=params.width,
            height=params.height,
            num_inference_steps=params.num_inference_steps,
            guidance_scale=params.guidance_scale,
            generator=generator,
            callback_on_step_end=step_callback,
        )
        image = result.images[0]
        image.save(str(output_path), format="PNG")
        if progress_callback:
            progress_callback(100)
        return output_path

    def available_models(self) -> list[str]:
        return [
            "stabilityai/stable-diffusion-2-1",
            "runwayml/stable-diffusion-v1-5",
        ]


class LocalSpeechToText(SpeechToTextServiceBase):
    def __init__(self):
        self._model = None
        self._model_size = ""

    def transcribe(self, params: SpeechToTextParams,
                   progress_callback: Optional[Callable[[int], None]] = None) -> str:
        import whisper

        if progress_callback:
            progress_callback(5)

        if self._model is None or self._model_size != params.model_size:
            self._model = whisper.load_model(params.model_size)
            self._model_size = params.model_size

        if progress_callback:
            progress_callback(20)

        result = self._model.transcribe(
            str(params.audio_path),
            language=params.language,
        )
        if progress_callback:
            progress_callback(100)
        return result["text"]


class LocalBackgroundRemoval(BackgroundRemovalServiceBase):
    def remove_background(self, params: BackgroundRemovalParams, output_path: Path,
                          progress_callback: Optional[Callable[[int], None]] = None) -> Path:
        from rembg import remove
        from PIL import Image

        if progress_callback:
            progress_callback(10)

        input_img = Image.open(str(params.image_path))
        if progress_callback:
            progress_callback(30)

        output_img = remove(
            input_img,
            alpha_matting=params.alpha_matting,
            alpha_matting_foreground_threshold=params.alpha_matting_foreground_threshold,
            alpha_matting_background_threshold=params.alpha_matting_background_threshold,
        )
        if progress_callback:
            progress_callback(90)

        output_img.save(str(output_path), format="PNG")
        if progress_callback:
            progress_callback(100)
        return output_path
