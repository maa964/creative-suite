"""Smoke tests for AI Studio window instantiation."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_ai_studio_instantiation(qapp):
    from apps.ai.main import AIStudioWindow
    window = AIStudioWindow()
    assert window.windowTitle() == "Creative Suite - AI Studio"


def test_ai_studio_has_four_tabs(qapp):
    from apps.ai.main import AIStudioWindow
    window = AIStudioWindow()
    assert window._tabs.count() == 4


def test_ai_studio_tab_labels(qapp):
    from apps.ai.main import AIStudioWindow
    window = AIStudioWindow()
    labels = [window._tabs.tabText(i) for i in range(window._tabs.count())]
    assert "Text to Image" in labels
    assert "Speech to Text" in labels
    assert "Background Removal" in labels
    assert "Settings" in labels


def test_ai_studio_default_backend_is_api(qapp):
    from apps.ai.main import AIStudioWindow
    from apps.ai.models import AIBackendType
    window = AIStudioWindow()
    assert window._get_backend_type() == AIBackendType.HUGGINGFACE_API
