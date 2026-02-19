"""Runtime availability checks for optional ML dependencies."""

import importlib
from dataclasses import dataclass


@dataclass
class LocalAvailability:
    torch: bool = False
    diffusers: bool = False
    transformers: bool = False
    whisper: bool = False
    rembg: bool = False

    @property
    def text_to_image_available(self) -> bool:
        return self.torch and self.diffusers

    @property
    def speech_to_text_available(self) -> bool:
        return self.torch and self.whisper

    @property
    def background_removal_available(self) -> bool:
        return self.rembg


def check_local_availability() -> LocalAvailability:
    result = LocalAvailability()
    for attr, module_name in [
        ("torch", "torch"),
        ("diffusers", "diffusers"),
        ("transformers", "transformers"),
        ("whisper", "whisper"),
        ("rembg", "rembg"),
    ]:
        try:
            importlib.import_module(module_name)
            setattr(result, attr, True)
        except ImportError:
            pass
    return result
