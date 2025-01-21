import pytest
import json
import os
from unittest.mock import patch
from CocoManager import CocoManager
import cv2
import numpy as np

@pytest.fixture
def coco_manager(app):
    return CocoManager(app)

def test_save_coco_valid(coco_manager, app, tmp_path):
    image_files = ["image1.jpg"]
    annotations = {
        "image1.jpg": [{"bbox": [10, 20, 30, 40], "class": "Klasa1"}]
    }
    classes = ["Klasa1"]
    image_data = {
        "image1.jpg": {"predefined_data": {}, "dynamic_data": {}, "exif": {}}
    }

    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(tmp_path / "image1.jpg"), img)

    app.folder_manager.image_folder = str(tmp_path)

    with patch("tkinter.filedialog.asksaveasfilename", return_value=str(tmp_path / "test.json")):
        coco_manager.save_coco(image_files, annotations, classes, image_data)

    assert os.path.exists(str(tmp_path / "test.json"))

    with open(str(tmp_path / "test.json"), "r") as f:
        data = json.load(f)

    assert len(data["images"]) == 1
    assert len(data["annotations"]) == 1
    assert len(data["categories"]) == 1

def test_load_coco_updates_app_data(coco_manager, app, tmp_path):
    coco_data = {
        "images": [{"id": 1, "width": 100, "height": 100, "file_name": "image1.jpg"}],
        "annotations": [{"id": 1, "image_id": 1, "category_id": 1, "bbox": [10, 20, 30, 40]}],
        "categories": [{"id": 1, "name": "Klasa1"}],
        "info": {"images_data": {"image1.jpg": {"predefined_data": {}, "dynamic_data": {}, "exif": {}}}}
    }

    coco_file_path = tmp_path / "test.json"
    with open(coco_file_path, "w") as f:
        json.dump(coco_data, f)

    with patch("tkinter.filedialog.askopenfilename", return_value=str(coco_file_path)):
        coco_manager.load_coco(app.image_files, app.annotations, app.classes, app.image_data, app.class_listbox)

    assert app.classes == ["Klasa1"]
    assert len(app.annotations["image1.jpg"]) == 1
    assert app.annotations["image1.jpg"][0]["class"] == "Klasa1"