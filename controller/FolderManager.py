import os
from tkinter import filedialog
import cv2
from PIL import Image, ExifTags
import tkinter as tk

class FolderManager:
    """Klasa do zarządzania folderem."""
    def __init__(self, app):
        self.app = app
        self.image_folder = ""

    def load_folder(self):
        """ Otwiercie okna do wyboru folderu i wczytanie obrazków."""
        self.image_folder = filedialog.askdirectory()
        if self.image_folder:
            self.app.image_files = [f for f in os.listdir(self.image_folder) if
                                    f.endswith(('.jpg', '.jpeg', '.png'))]
            self.app.image_listbox.delete(0, tk.END)
            for image_file in self.app.image_files:
                self.app.image_listbox.insert(tk.END, image_file)
            self.app.current_image_index = 0
            self.load_image()
            self.app.annotations = {}
        else:  # Dodany blok else
            self.app.current_image = None
            self.app.image_label.delete("all")
            self.app.current_image_index = 0
            self.app.image_files = []
            self.app.image_listbox.delete(0, tk.END)

    def load_image(self):
        """ Wyświetl wybrany obraz."""
        if self.app.image_files:
            image_filename = self.app.image_files[self.app.current_image_index]
            image_path = os.path.join(self.image_folder, image_filename)

            # Odczyt danych EXIF
            try:
                image = Image.open(image_path)
                exif_data = image._getexif()

                if exif_data:
                    exif = {
                        ExifTags.TAGS[k]: v
                        for k, v in exif_data.items()
                        if k in ExifTags.TAGS
                    }
                    if image_filename not in self.app.image_data:
                        self.app.image_data[image_filename] = {}
                    self.app.image_data[image_filename]["exif"] = exif
                else:
                    if image_filename not in self.app.image_data:
                        self.app.image_data[image_filename] = {}
                    self.app.image_data[image_filename]["exif"] = {}
                image.close()
            except (AttributeError, IOError, IndexError):
                print(f"Nie można odczytać danych EXIF z pliku: {image_filename}")
                if image_filename not in self.app.image_data:
                    self.app.image_data[image_filename] = {}
                self.app.image_data[image_filename]["exif"] = {}

            self.app.current_image = cv2.imread(image_path)
            self.app.current_image = cv2.cvtColor(self.app.current_image, cv2.COLOR_BGR2RGB)
            self.app.image_manager.display_image()
            self.app.data_manager.clear_data_fields()

            # Inicjalizacja undo_stack i redo_stack
            if "undo_stack" not in self.app.image_data.get(image_filename, {}):
                self.app.image_data.setdefault(image_filename, {})["undo_stack"] = []
            if "redo_stack" not in self.app.image_data.get(image_filename, {}):
                self.app.image_data.setdefault(image_filename, {})["redo_stack"] = []

            # Wczytywanie zapisanych danych
            if image_filename in self.app.image_data:
                image_data = self.app.image_data[image_filename]
                if "predefined_data" in image_data:
                    predefined_data = image_data["predefined_data"]
                    for field_name, value in predefined_data.items():
                        if field_name in self.app.data_manager.predefined_entries:
                            self.app.data_manager.predefined_entries[field_name].insert(0, value)

            # Ustaw adnotacje
            if image_filename not in self.app.annotations:
                self.app.annotations[image_filename] = []

            self.app.image_manager.draw_annotations()

    def image_selected(self, event):
        """Wybór obrazka z listy."""
        self.app.annotation_manager.disable_resizing_mode()
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self.app.current_image_index = index
            self.load_image()