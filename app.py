import os
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import numpy as np
from PIL import Image

from AnnotationManager import AnnotationManager
from CocoManager import CocoManager
from FolderManager import FolderManager
from ImageManager import ImageManager
from DataManager import DataManager
from HistoryManager import HistoryManager

class App:
    """ Integracja komponentó i logiką aplikacji. """
    def __init__(self, master):
        self.master = master
        master.title("Fotograf - Narzędzie do adnotacji zdjęć")

        # Inicjalizacja atrybutów
        self.image_folder = ""
        self.image_files = []
        self.current_image_index = 0
        self.current_image = None
        self.annotations = {}
        self.classes = []
        self.active_class = tk.StringVar(value="")
        self.predefined_fields = ["Rodzaj kamery", "Miejsce", "Data wykonania"]
        self.dynamic_fields = {}
        self.image_data = {} # Dane dla każdego obrazka

        # Inicjalizacja managerów
        self.history_manager = HistoryManager()
        self.annotation_manager = AnnotationManager(self)
        self.coco_manager = CocoManager(self)
        self.folder_manager = FolderManager(self)
        self.image_manager = ImageManager(self)
        self.data_manager = DataManager(self)

        # Inicjalizacja komponentów interfejsu użytkownika
        self.create_widgets()

        # Konfiguracja layoutu
        self.configure_layout()

    def create_widgets(self):
        """Tworzy i rozmieszcza widgety w oknie aplikacji."""
        folder_icon = ctk.CTkImage(Image.open("folder.png"))
        add_class_icon = ctk.CTkImage(Image.open("add_class.png"))
        undo_icon = ctk.CTkImage(Image.open("undo.png"))
        redo_icon = ctk.CTkImage(Image.open("redo.png"))
        save_coco_icon = ctk.CTkImage(Image.open("json.png"))
        load_from_coco = ctk.CTkImage(Image.open("file.png"))
        stats_icon = ctk.CTkImage(Image.open("statistics.png"))
        exif_icon = ctk.CTkImage(Image.open("exif.png"))
        add_field_icon = ctk.CTkImage(Image.open("add.png"))
        exit_icon = ctk.CTkImage(Image.open("exit.png"))
        # Kontener lewej strony
        left_frame = ctk.CTkFrame(self.master, width=140, corner_radius=0)
        left_frame.grid(row=0, column=0, padx=0, pady=5, sticky="nsew")
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_rowconfigure(4, weight=1)

        # Przycisk do wczytywania folderu
        self.file_button = ctk.CTkButton(left_frame, text="Wczytaj folder",image= folder_icon, command=self.folder_manager.load_folder,
                                         width=140, height=30)
        self.file_button.grid(row=0, column=0, padx=5, pady=(10, 5), sticky="ew")

        # Lista zdjęć
        self.image_listbox = tk.Listbox(left_frame, bg="#2E2E2E", fg="#DCE4EE", selectbackground="#2fa572",
                                        selectforeground="white", activestyle="none",
                                        font=("Arial", 12), height=10)
        self.image_listbox.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="nsew")
        self.image_listbox.bind("<<ListboxSelect>>", self.folder_manager.image_selected)

        # Lista klas
        self.class_listbox = tk.Listbox(left_frame, font=("Arial", 12), height=10, selectbackground="#2fa572",
                                        selectforeground="white", bg="#2E2E2E", fg="#DCE4EE", activestyle="none")
        self.class_listbox.grid(row=4, column=0, padx=5, pady=(0, 10), sticky="nsew")
        self.class_listbox.bind("<<ListboxSelect>>", self.annotation_manager.on_class_select)
        self.add_class_button = ctk.CTkButton(left_frame, text="Dodaj klasę", image=add_class_icon,
                                              command=self.annotation_manager.add_class, width=140,
                                              height=30)
        self.add_class_button.grid(row=3, column=0, padx=5, pady=(10, 5), sticky="ew")

        # Obszar wyświetlania obrazu
        self.image_label = tk.Canvas(self.master, bg="#2E2E2E", highlightthickness=0)
        self.image_label.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        # Bindowanie myszy
        self.image_label.bind("<ButtonPress-1>",
                              lambda event: self.annotation_manager.on_mouse_press(event))
        self.image_label.bind("<B1-Motion>",
                              lambda event: self.annotation_manager.on_mouse_drag(event))
        self.image_label.bind("<ButtonRelease-1>",
                              lambda event: self.annotation_manager.on_mouse_release(event))
        self.image_label.bind("<Button-3>",
                              lambda event: self.annotation_manager.on_right_click(event))
        self.image_label.bind("<Motion>",
                              lambda event: self.annotation_manager.on_mouse_motion(event))

        # -Przyciski cofnij i przywróć
        self.undo_button = ctk.CTkButton(left_frame, text="Cofnij", image=undo_icon, command=self.undo, width=140, height=30)
        self.undo_button.grid(row=5, column=0, padx=5, pady=(10, 5), sticky="ew")
        self.redo_button = ctk.CTkButton(left_frame, text="Przywróć", image=redo_icon, command=self.redo, width=140, height=30)
        self.redo_button.grid(row=6, column=0, padx=5, pady=(10, 10), sticky="ew")

        # Prawy panel aplikacji
        right_frame = ctk.CTkFrame(self.master, corner_radius=0)
        right_frame.grid(row=0, column=5, padx=0, pady=5, sticky="nsew")
        right_frame.grid_rowconfigure(6, weight=1)

        # Dane dodatkowe
        self.predefined_data_frame = tk.Frame(right_frame, bg="#2E2E2E")
        self.predefined_data_frame.grid(row=5, column=0, padx=0, pady=5, sticky="w")
        self.data_manager.create_predefined_data_fields()

        self.save_to_coco_button = self.stats_button = ctk.CTkButton(right_frame, text="Zapisz do COCO", image=save_coco_icon, command=self.save_coco, width=140,
                                          height=30)
        self.stats_button.grid(row=0, column=0, padx=5, pady=(10, 5), sticky="ew")

        self.load_from_coco_button = self.stats_button = ctk.CTkButton(right_frame, text="Wczytaj COCO", image=load_from_coco,
                                                                     command=self.load_coco, width=140,
                                                                     height=30)
        self.load_from_coco_button.grid(row=1, column=0, padx=5, pady=(10, 5), sticky="ew")

        self.add_field_button = ctk.CTkButton(right_frame, text="Dodaj pole", image=add_field_icon,
                                              command=self.data_manager.add_dynamic_field, width=10,
                                              height=30)
        self.add_field_button.grid(row=4, column=0, padx=5, pady=(10, 5), sticky="ew")

        self.stats_button = ctk.CTkButton(right_frame, text="Statystyki", image=stats_icon, command=self.show_stats, width=140,
                                          height=30)
        self.stats_button.grid(row=2, column=0, padx=5, pady=(10, 5), sticky="ew")

        self.exif_button = ctk.CTkButton(right_frame, text="Pokaż EXIF", image=exif_icon, command=self.data_manager.show_exif,
                                         width=140,
                                         height=30)
        self.exif_button.grid(row=3, column=0, padx=5, pady=(10, 5), sticky="ew")

        self.exit_button = ctk.CTkButton(right_frame, fg_color="grey", hover_color="red",
                                         text="Wyjście", image=exit_icon, command=self.on_closing,
                                         width=140,
                                         height=30)
        self.exit_button.grid(row=6, column=0, padx=5, pady=(10, 10), sticky="sew")
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def configure_layout(self):
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(5, weight=0)

    def on_closing(self):
        if messagebox.askokcancel("Zamknij", "Uwaga! Niezapisane dane zostaną utracone. Czy na pewno chcesz zamknąć?"):
            self.master.destroy()

    def save_coco(self):
        """Zapisd do formatu COCO """
        self.coco_manager.save_coco(self.image_files, self.annotations, self.classes, self.image_data)

    def load_coco(self):
        """Wczytuje dane z pliku COCO."""
        if self.coco_manager.load_coco(self.image_files, self.annotations, self.classes, self.image_data, self.class_listbox):
            self.folder_manager.image_folder = self.coco_manager.coco_folder
            self.image_files = [f for f in os.listdir(self.folder_manager.image_folder) if
                                f.endswith(('.jpg', '.jpeg', '.png'))]
            self.image_listbox.delete(0, tk.END)
            for image_file in self.image_files:
                self.image_listbox.insert(tk.END, image_file)
            self.current_image_index = 0
            self.folder_manager.load_image()

    def show_stats(self):
        """Statystuki"""
        if not self.annotations:
            messagebox.showwarning("Brak adnotacji", "Najpierw wczytaj obrazy i dodaj adnotacje.")
            return

        stats_window = ctk.CTkToplevel(self.master)
        stats_window.title("Statystyki")
        stats_window.grab_set()

        # Ustaw rozmiar i wyśrodkuj okno
        screen_width = stats_window.winfo_screenwidth()
        screen_height = stats_window.winfo_screenheight()
        window_width = 400
        window_height = 300
        stats_window.geometry(f"{window_width}x{window_height}")
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        stats_window.geometry(f"+{x}+{y}")

        # Oblicz statystyki
        num_images_with_annotations = len(self.annotations)
        annotations_per_image = [len(annotations) for annotations in self.annotations.values()]
        avg_annotations_per_image = np.mean(annotations_per_image) if annotations_per_image else 0
        max_annotations_per_image = max(annotations_per_image) if annotations_per_image else 0
        min_annotations_per_image = min(annotations_per_image) if annotations_per_image else 0
        class_counts = {}
        for image_filename, annotations in self.annotations.items():
            for annotation in annotations:
                class_name = annotation["class"]
                class_counts[class_name] = class_counts.get(class_name, 0) + 1

        # Wyświetl statystyki
        ctk.CTkLabel(stats_window, text=f"Liczba obrazów z adnotacjami: {num_images_with_annotations}").pack(
            pady=(10, 0))
        ctk.CTkLabel(stats_window,
                     text=f"Średnia liczba adnotacji na obraz: {avg_annotations_per_image:.2f}").pack()
        ctk.CTkLabel(stats_window, text=f"Maksymalna liczba adnotacji na obraz: {max_annotations_per_image}").pack()
        ctk.CTkLabel(stats_window, text=f"Minimalna liczba adnotacji na obraz: {min_annotations_per_image}").pack()
        for class_name, count in class_counts.items():
            ctk.CTkLabel(stats_window, text=f"{class_name}: {count}").pack()

    def undo(self):
        """Cofnij"""
        last_operation = self.history_manager.undo_stack.pop() if self.history_manager.undo_stack else None
        if last_operation:
            self.history_manager.redo_stack.append(last_operation)
            # Rozpakowanie krotki
            operation_type, image_filename, *args = last_operation
            if operation_type == "create":
                # Cofnięcie utworzenia adnotacji
                if image_filename in self.annotations:
                    for i, ann in enumerate(self.annotations[image_filename]):
                        if ann.get("bbox") == args[0].get("bbox") and ann.get("class") == args[0].get("class"):
                            self.annotations[image_filename].pop(i)
                            break
            elif operation_type == "delete":
                # Cofnięcie usunięcia adnotacji
                if image_filename not in self.annotations:
                    self.annotations[image_filename] = []
                self.annotations[image_filename].insert(args[1], args[0])  # Przywróć na konkretnej pozycji
                self.annotation_manager.selected_annotation_index = args[1]
            elif operation_type == "resize" or operation_type == "move":
                # Cofnięcie zmiany rozmiaru lub przesunięcia
                self.annotations[image_filename][args[0]]["bbox"] = args[1]  # Przywróć stary stan
                self.annotation_manager.selected_annotation_index = args[0]
            elif operation_type == "change_class":
                # Cofnięcie zmiany klasy
                for i, ann in enumerate(self.annotations.get(image_filename, [])):
                    if ann.get("bbox") == args[0]:  # Porównaj kształt
                        self.annotations[image_filename][i]["class"] = args[1]  # Przywróć starą klasę
                        break
            elif operation_type == "edit_data":
                # Cofnięcie edycji danych
                self.image_data[image_filename]["predefined_data"] = args[0]
                self.image_data[image_filename]["dynamic_data"] = args[1]
                # Aktualizacja pól w interfejsie
                self.data_manager.clear_data_fields()
                if "predefined_data" in self.image_data[image_filename]:
                    for field_name, value in self.image_data[image_filename]["predefined_data"].items():
                        if field_name in self.data_manager.predefined_entries:
                            self.data_manager.predefined_entries[field_name].insert(0, value)
                if "dynamic_data" in self.image_data[image_filename]:
                    for field_name, value in self.image_data[image_filename]["dynamic_data"].items():
                        if field_name in self.data_manager.dynamic_fields:
                            self.data_manager.dynamic_fields[field_name].delete(0, tk.END)
                            self.data_manager.dynamic_fields[field_name].insert(0, value)
            self.image_manager.draw_annotations()

    def redo(self):
        """Przywróć"""
        last_undone_operation = self.history_manager.redo_stack.pop() if self.history_manager.redo_stack else None
        if last_undone_operation:
            self.history_manager.undo_stack.append(last_undone_operation)
            operation_type, image_filename, *args = last_undone_operation
            if operation_type == "create":
                # Ponowne dodanie adnotacji
                if image_filename not in self.annotations:
                    self.annotations[image_filename] = []
                self.annotations[image_filename].append(args[0])
                self.annotation_manager.selected_annotation_index = len(self.annotations[image_filename]) - 1
            elif operation_type == "delete":
                # Ponowne usunięcie adnotacji
                if image_filename in self.annotations:
                    for i, ann in enumerate(self.annotations[image_filename]):
                        if ann.get("bbox") == args[0].get("bbox") and ann.get("class") == args[0].get("class"):
                            self.annotations[image_filename].pop(i)
                            break
            elif operation_type == "resize" or operation_type == "move":
                # Ponowne wykonanie zmiany rozmiaru lub przesunięcia
                self.annotations[image_filename][args[0]]["bbox"] = args[2]  # Przywróć nowy kształt
                self.annotation_manager.selected_annotation_index = args[0]
            elif operation_type == "change_class":
                # Ponowna zmiana klasy
                for i, ann in enumerate(self.annotations.get(image_filename, [])):
                    if ann.get("bbox") == args[0]:  # Porównaj kształt
                        self.annotations[image_filename][i]["class"] = args[2]  # Ustaw nową klasę
                        break
            elif operation_type == "edit_data":
                # Ponowna edycja danych
                self.image_data[image_filename]["predefined_data"] = args[2]
                self.image_data[image_filename]["dynamic_data"] = args[3]
                # Aktualizacja pól w interfejsie
                self.data_manager.clear_data_fields()
                if "predefined_data" in self.image_data[image_filename]:
                    for field_name, value in self.image_data[image_filename]["predefined_data"].items():
                        if field_name in self.data_manager.predefined_entries:
                            self.data_manager.predefined_entries[field_name].insert(0, value)
                if "dynamic_data" in self.image_data[image_filename]:
                    for field_name, value in self.image_data[image_filename]["dynamic_data"].items():
                        if field_name in self.data_manager.dynamic_fields:
                            self.data_manager.dynamic_fields[field_name].delete(0, tk.END)
                            self.data_manager.dynamic_fields[field_name].insert(0, value)
            self.image_manager.draw_annotations()