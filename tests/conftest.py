import pytest
import tkinter as tk
from app import App
from PIL import Image

@pytest.fixture(scope="session")
def app():
    root = tk.Tk()
    app = App(root)
    app.current_image = Image.new("RGB", (100, 100), color="white")
    app.image_files = ["test_image.jpg"]
    app.current_image_index = 0
    app.image_label = tk.Canvas(app.master)
    yield app
    root.destroy()