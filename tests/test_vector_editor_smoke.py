"""Smoke test for Vector Editor instantiation."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_vector_editor_instantiation(qapp):
    from apps.vector.main import VectorEditorWindow
    window = VectorEditorWindow()
    assert window.windowTitle() == "Creative Suite - Vector Editor"
    assert window.scene is not None
    assert window.scene.undo_stack is not None


def test_vector_editor_new_file(qapp):
    from apps.vector.main import VectorEditorWindow
    window = VectorEditorWindow()
    window.on_new_file()
    assert len(window.scene.items()) == 0
