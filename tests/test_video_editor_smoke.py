"""Smoke test for Video Editor instantiation."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_video_editor_instantiation(qapp):
    from apps.video.main import VideoEditorWindow
    window = VideoEditorWindow()
    assert window.windowTitle() == "Creative Suite - Video Editor"
    assert window.project is not None
    assert len(window.project.tracks) == 4
    assert window.project.tracks[0].name == "V1"


def test_video_editor_new_project(qapp):
    from apps.video.main import VideoEditorWindow
    window = VideoEditorWindow()
    window.on_new_file()
    assert len(window.project.tracks) == 4
    assert len(window.project.media_items) == 0
