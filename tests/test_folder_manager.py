import pytest
import os
from unittest.mock import patch
from FolderManager import FolderManager
from PIL import Image

@pytest.fixture
def folder_manager(app):
    return FolderManager(app)

def test_load_folder_valid(folder_manager, tmp_path, app):
    # Tworzenie przykładowych plików w folderze tymczasowym
    os.makedirs(tmp_path / "images", exist_ok=True)
    image1_path = tmp_path / "images" / "image1.jpg"
    image2_path = tmp_path / "images" / "image2.png"

    # Tworzymy puste obrazy
    Image.new("RGB", (100, 100)).save(image1_path)
    Image.new("RGB", (100, 100)).save(image2_path)

    with patch("tkinter.filedialog.askdirectory", return_value=str(tmp_path / "images")):
        folder_manager.load_folder()

    assert len(app.image_files) == 2
    assert "image1.jpg" in app.image_files
    assert "image2.png" in app.image_files
    assert app.current_image_index == 0

def test_load_folder_invalid(folder_manager, app):
    app.image_files = []

    with patch("tkinter.filedialog.askdirectory", return_value=""):
        folder_manager.load_folder()

    assert len(app.image_files) == 0