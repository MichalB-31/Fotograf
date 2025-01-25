import pytest
from unittest.mock import patch
from controller.DataManager import DataManager
import tkinter as tk

@pytest.fixture
def data_manager(app):
    app.predefined_data_frame = tk.Frame(app.master)
    return DataManager(app)

def test_add_dynamic_field_success(data_manager):
    with patch("customtkinter.CTkInputDialog.get_input", return_value="NowePole"):
        data_manager.add_dynamic_field()

    assert "NowePole" in data_manager.dynamic_fields

def test_save_current_image_data(data_manager, app):
    app.image_files = ["test_image.jpg"]
    app.current_image_index = 0

    data_manager.predefined_entries["Rodzaj kamery"] = tk.Entry(app.predefined_data_frame)
    data_manager.predefined_entries["Rodzaj kamery"].insert(0, "Kamera Testowa")

    data_manager.save_current_image_data()

    assert app.image_data["test_image.jpg"]["predefined_data"]["Rodzaj kamery"] == "Kamera Testowa"

def test_clear_dynamic_fields(data_manager, app):
    data_manager.dynamic_fields["Pole 1"] = tk.Entry(app.master)
    data_manager.dynamic_fields["Pole 2"] = tk.Entry(app.master)

    data_manager.clear_dynamic_fields()

    assert len(data_manager.dynamic_fields) == 0