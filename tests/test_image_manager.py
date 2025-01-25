import pytest
from unittest.mock import MagicMock
from controller.ImageManager import ImageManager
import tkinter as tk
import cv2
import numpy as np

@pytest.fixture
def image_manager(app):
    app.image_label = tk.Canvas(app.master)
    return ImageManager(app)

def test_display_image(image_manager, app):
    # Tworzymy testowy obraz
    app.current_image = cv2.cvtColor(np.zeros((50, 100, 3), dtype=np.uint8), cv2.COLOR_BGR2RGB)
    app.image_label.winfo_width = MagicMock(return_value=200)
    app.image_label.winfo_height = MagicMock(return_value=150)

    image_manager.display_image()