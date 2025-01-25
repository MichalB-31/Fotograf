import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import customtkinter as ctk
from PIL import ExifTags, Image
import re

class DataManager:
    """Klasa do zarządzania danymi dodatkowymi i EXIF."""
    def __init__(self, app):
        self.app = app
        self.predefined_fields = ["Marka", "Model", "Opis", "Autor", "Czas naświetlania", "Przesłona",
                                  "ISO", "Czas otwarcia migawki", "Oprogramowanie", "Data wykonania"]
        self.predefined_entries = {}
        self.dynamic_fields = {}

    def create_predefined_data_fields(self):
        """Tworzy pola do wprowadzania predefiniowanych danych."""
        for i, field_name in enumerate(self.predefined_fields):
            if field_name == "Data wykonania":
                label = ctk.CTkLabel(self.app.predefined_data_frame, text=f"{field_name}:")
                label.grid(row=i, column=0, sticky="w", padx=5, pady=2)
                entry = DateEntry(self.app.predefined_data_frame)
                entry.grid(row=i + 1, column=0, padx=(5, 0), sticky="ew", pady=2)
            else:
                label = ctk.CTkLabel(self.app.predefined_data_frame, text=f"{field_name}:")
                label.grid(row=i, column=0, sticky="w", padx=5, pady=2)
                entry = ctk.CTkEntry(self.app.predefined_data_frame)
                entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
            entry.bind("<KeyRelease>", self.save_current_image_data)
            self.predefined_entries[field_name] = entry

        self.app.predefined_data_frame.grid_columnconfigure(1, weight=1)

    def clear_data_fields(self):
        for entry in self.predefined_entries.values():
            entry.delete(0, tk.END)

    def save_current_image_data(self, event=None):
        """Zapisuje dane wprowadzone w polach do słownika"""
        if self.app.image_files:
            image_filename = self.app.image_files[self.app.current_image_index]
            if image_filename not in self.app.image_data:
                self.app.image_data[image_filename] = {}

            predefined_data = {}
            for field_name, entry in self.predefined_entries.items():
                if field_name == "Data wykonania":
                    value = entry.get_date().strftime('%Y-%m-%d')
                else:
                    value = entry.get().strip()
                if value:
                    predefined_data[field_name] = value

            dynamic_data = {}
            for field_name, entry in self.dynamic_fields.items():
                value = entry.get().strip()
                if value:
                    dynamic_data[field_name] = value

            # Dodanie operacji do historii tylko, gdy dane się zmieniły
            if self.app.image_data[image_filename].get("predefined_data", {}) != predefined_data or \
                    self.app.image_data[image_filename].get("dynamic_data", {}) != dynamic_data:
                self.app.history_manager.add_edit_data_operation(image_filename,
                                                                 self.app.image_data[image_filename].get(
                                                                     "predefined_data", {}),
                                                                 self.app.image_data[image_filename].get("dynamic_data",
                                                                                                        {}),
                                                                 predefined_data, dynamic_data)

            self.app.image_data[image_filename]["predefined_data"] = predefined_data
            self.app.image_data[image_filename]["dynamic_data"] = dynamic_data

    def show_exif(self):
        """Wyświetla dane EXIF w nowym oknie."""
        if not self.app.image_files:
            messagebox.showwarning("Brak obrazów", "Najpierw wczytaj folder z obrazami.")
            return

        image_filename = self.app.image_files[self.app.current_image_index]
        if image_filename not in self.app.image_data or "exif" not in self.app.image_data[image_filename]:
            messagebox.showinfo("Brak danych EXIF", "Brak danych EXIF dla tego obrazu.")
            return

        exif_data = self.app.image_data[image_filename]["exif"]

        exif_window = ctk.CTkToplevel(self.app.master)
        exif_window.title(f"Dane EXIF - {image_filename}")
        exif_window.geometry("500x400")

        screen_width = exif_window.winfo_screenwidth()
        screen_height = exif_window.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 400) // 2
        exif_window.geometry(f"+{x}+{y}")

        # Wyświetl dane EXIF
        text_area = ctk.CTkTextbox(exif_window, wrap=tk.WORD)
        text_area.pack(fill="both", expand=True, padx=10, pady=10)
        text_area.configure(state="normal")
        for tag, value in exif_data.items():
            text_area.insert(tk.END, f"{tag}: {value}\n")
        text_area.configure(state="disabled")
        exif_window.grab_set()




