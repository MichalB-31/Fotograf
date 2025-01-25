import pytest
from unittest.mock import patch, MagicMock
from controller.AnnotationManager import AnnotationManager
import tkinter as tk
import cv2
import numpy as np

@pytest.fixture
def annotation_manager(app):
    app.image_label = tk.Canvas(app.master)
    return AnnotationManager(app)

def test_add_class_success(annotation_manager, app):
    app.classes = []
    app.class_listbox = MagicMock()
    with patch("customtkinter.CTkInputDialog.get_input", return_value="NowaKlasa"):
        annotation_manager.add_class()

    assert "NowaKlasa" in app.classes

def test_add_class_duplicate(annotation_manager, app):
    app.classes = ["IstniejącaKlasa"]
    app.class_listbox = MagicMock()

    with patch("customtkinter.CTkInputDialog.get_input", return_value="IstniejącaKlasa"):
        with patch("tkinter.messagebox.showerror") as mock_showerror:
            annotation_manager.add_class()

    mock_showerror.assert_called_once_with("Błąd", "Klasa o tej nazwie już istnieje!")

def test_on_mouse_release_adds_annotation(annotation_manager, app):
    app.image_files = ["test_image.jpg"]
    app.current_image_index = 0
    app.active_class.set("Klasa1")

    app.current_image = cv2.cvtColor(np.zeros((100, 100, 3), dtype=np.uint8), cv2.COLOR_BGR2RGB)

    annotation_manager.on_mouse_press(MagicMock(x=10, y=10))
    annotation_manager.on_mouse_drag(MagicMock(x=30, y=30))
    annotation_manager.on_mouse_release(MagicMock(x=30, y=30))

    assert len(app.annotations["test_image.jpg"]) == 1
    assert app.annotations["test_image.jpg"][0]["bbox"] == [10, 10, 20, 20]
    assert app.annotations["test_image.jpg"][0]["class"] == "Klasa1"

def test_change_annotation_name(annotation_manager, app):
    app.image_files = ["test_image.jpg"]
    app.current_image_index = 0
    app.annotations["test_image.jpg"] = [{"bbox": [10, 10, 50, 50], "class": "StaraKlasa"}]
    annotation_manager.selected_annotation_index = 0

    with patch("customtkinter.CTkInputDialog.get_input", return_value="NowaKlasa"):
        annotation_manager.change_annotation_name()

    assert app.annotations["test_image.jpg"][0]["class"] == "NowaKlasa"

def test_delete_selected_annotation(annotation_manager, app):
    app.image_files = ["test_image.jpg"]
    app.current_image_index = 0
    app.annotations["test_image.jpg"] = [{"bbox": [10, 10, 50, 50], "class": "Klasa1"}]
    annotation_manager.selected_annotation_index = 0

    annotation_manager.delete_selected_annotation()

    assert len(app.annotations["test_image.jpg"]) == 0