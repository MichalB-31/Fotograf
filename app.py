import tkinter as tk
from tkinter import Listbox, Scrollbar
from FolderManager import FolderManager
from ViewManager import ViewManager
from AnnotationManager import AnnotationManager

class Fotograf:
    def __init__(self, root):
        self.root = root
        self.root.title("Fotograf")
        self.root.geometry("900x600")  # Ustawienie rozmiaru okna

        # Zarządzanie komponentami
        self.folder_manager = FolderManager(self)
        self.view_manager = ViewManager(self)
        self.annotation_manager = AnnotationManager(self)

        # Struktura układu
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_columnconfigure(2, weight=1)

        # Sekcja list katalogów i zdjęć
        self.sidebar_frame = tk.Frame(root, padx=10, pady=10)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="ns")

        tk.Label(self.sidebar_frame, text="Katalogi", font=("Arial", 12)).pack(anchor="w", pady=(0, 5))
        self.folder_listbox = Listbox(self.sidebar_frame, width=25, height=15)
        self.folder_listbox.pack(pady=(0, 10), fill="x")
        self.folder_listbox.bind("<<ListboxSelect>>", self.folder_manager.on_folder_select)

        tk.Label(self.sidebar_frame, text="Zdjęcia", font=("Arial", 12)).pack(anchor="w", pady=(10, 5))
        self.image_listbox = Listbox(self.sidebar_frame, width=25, height=15)
        self.image_listbox.pack(fill="x")
        self.image_listbox.bind("<<ListboxSelect>>", self.view_manager.on_image_select)

        scrollbar = Scrollbar(self.sidebar_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        self.image_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.image_listbox.yview)

        # Przycisk zarządzania katalogami
        self.add_folder_btn = tk.Button(self.sidebar_frame, text="Dodaj katalog", command=self.folder_manager.add_folder)
        self.add_folder_btn.pack(fill="x", pady=(10, 5))

        self.remove_folder_btn = tk.Button(self.sidebar_frame, text="Usuń katalog", command=self.folder_manager.remove_folder)
        self.remove_folder_btn.pack(fill="x")

        # Sekcja Canvas do wyświetlania zdjęcia
        self.canvas_frame = tk.Frame(root, padx=10, pady=10, relief="ridge", bd=2)
        self.canvas_frame.grid(row=0, column=1, rowspan=2, columnspan=2, sticky="nsew")
        self.view_manager.create_canvas()

        # Panel sterowania
        self.controls_frame = tk.Frame(root, padx=10, pady=10)
        self.controls_frame.grid(row=2, column=0, columnspan=3, sticky="ew")
        self.controls_frame.grid_columnconfigure(2, weight=1)

        self.add_annotation_btn = tk.Button(self.controls_frame, text="Dodaj adnotację",
                                            command=self.start_annotation_mode)
        self.add_annotation_btn.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.save_button = tk.Button(self.controls_frame, text="Zapisz adnotacje",
                                     command=self.view_manager.save_annotations_to_coco)
        self.save_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.load_button = tk.Button(self.controls_frame, text="Załaduj adnotacje",
                                     command=self.view_manager.load_annotations)
        self.load_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")

        self.zoom_in_btn = tk.Button(self.controls_frame, text="🔍+", command=self.view_manager.zoom_in)
        self.zoom_in_btn.grid(row=0, column=3, padx=5, pady=5, sticky="e")

        self.zoom_out_btn = tk.Button(self.controls_frame, text="🔍-", command=self.view_manager.zoom_out)
        self.zoom_out_btn.grid(row=0, column=4, padx=5, pady=5, sticky="e")

        self.metadata_btn = tk.Button(
            self.controls_frame, text="Dodaj metadane", command=self.view_manager.open_metadata_window
        )
        self.metadata_btn.grid(row=0, column=5, padx=5, pady=5, sticky="e")

    def start_annotation_mode(self):
        if self.view_manager.annotation_mode_active:
            self.view_manager.change_annotation_name()
        else:
            self.view_manager.start_annotation_mode()


if __name__ == "__main__":
    root = tk.Tk()
    app = Fotograf(root)
    root.mainloop()
