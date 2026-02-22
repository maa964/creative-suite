"""Tests for AI dependency availability checking."""

from apps.ai.services.availability import check_local_availability, LocalAvailability


def test_availability_returns_dataclass():
    result = check_local_availability()
    assert isinstance(result, LocalAvailability)


def test_availability_bool_fields():
    result = check_local_availability()
    assert isinstance(result.torch, bool)
    assert isinstance(result.diffusers, bool)
    assert isinstance(result.transformers, bool)
    assert isinstance(result.whisper, bool)
    assert isinstance(result.rembg, bool)


def test_text_to_image_requires_torch_and_diffusers():
    avail = LocalAvailability(torch=True, diffusers=True)
    assert avail.text_to_image_available is True
    avail2 = LocalAvailability(torch=True, diffusers=False)
    assert avail2.text_to_image_available is False
    avail3 = LocalAvailability(torch=False, diffusers=True)
    assert avail3.text_to_image_available is False


def test_speech_to_text_requires_torch_and_whisper():
    avail = LocalAvailability(torch=True, whisper=True)
    assert avail.speech_to_text_available is True
    avail2 = LocalAvailability(torch=False, whisper=True)
    assert avail2.speech_to_text_available is False


def test_background_removal_requires_rembg():
    avail = LocalAvailability(rembg=True)
    assert avail.background_removal_available is True
    avail2 = LocalAvailability(rembg=False)
    assert avail2.background_removal_available is False


def test_all_unavailable_by_default():
    avail = LocalAvailability()
    assert avail.text_to_image_available is False
    assert avail.speech_to_text_available is False
    assert avail.background_removal_available is False
