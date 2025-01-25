import pytest
from controller.HistoryManager import HistoryManager

@pytest.fixture
def history_manager():
    return HistoryManager()

def test_add_create_annotation_operation(history_manager):
    history_manager.add_create_annotation_operation("image1.jpg", {"bbox": [0, 0, 10, 10], "class": "Klasa1"})
    assert len(history_manager.undo_stack) == 1