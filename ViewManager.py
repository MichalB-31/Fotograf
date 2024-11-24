import os
from PIL import Image, ImageTk
import tkinter as tk
from AnnotationManager import AnnotationManager
from tkinter import simpledialog
from CocoManager import CocoManager
from tkinter import filedialog


class ViewManager:

    def __init__(self, app):
        self.app = app
        self.canvas = None
        self.image_files = []
        self.current_image_index = 0
        self.current_image_scale = 1.0
        self.photo_img = None
        self.current_img_path = None
        self.annotation_mode_active = False
        self.annotation_manager = None
        self.selected_annotation = False
        self.folder_path = None
        self.metadata = {}

    def create_canvas(self):
        """Do stworzenia kontrolek"""
        self.canvas = tk.Canvas(self.app.root, bg="white", scrollregion=(0, 0, 2000, 2000))
        self.canvas.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=10, pady=10)

        self.annotation_manager = AnnotationManager(self.canvas)

        h_scroll = tk.Scrollbar(self.app.root, orient="horizontal", command=self.canvas.xview)
        v_scroll = tk.Scrollbar(self.app.root, orient="vertical", command=self.canvas.yview)
        self.canvas.config(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        h_scroll.grid(row=2, column=2, sticky="ew")
        v_scroll.grid(row=0, column=3, sticky="ns")

        self.canvas.bind("<ButtonPress-1>", self.annotation_manager.select_annotation)
        self.canvas.bind_all("<BackSpace>", self.annotation_manager.delete_selected_annotation)
        self.create_context_menu()
        self.coco_exporter = CocoManager(self.canvas)

    def display_image(self, img_path):
        """Wyświetlenie grafiki"""
        img = Image.open(img_path)
        img = img.resize(
            (int(img.width * self.current_image_scale), int(img.height * self.current_image_scale)),
            Image.LANCZOS
        )
        self.photo_img = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo_img)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def load_images_from_folder(self, folder_path):
        """Pokazuje obrazy z folderu na liście"""
        self.folder_path = folder_path
        self.image_files = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        self.app.image_listbox.delete(0, "end")
        for img_file in self.image_files:
            self.app.image_listbox.insert("end", img_file)

    def on_image_select(self, event):
        """Wybranie danego obrazu"""
        selection = event.widget.curselection()
        if selection:
            self.current_image_index = selection[0]
            img_path = os.path.join(self.folder_path, self.image_files[self.current_image_index])
            self.current_img_path = img_path
            self.display_image(img_path)
        else:
            print("Nie wybrano obrazu.")

    def clear_canvas(self):
        self.canvas.delete("all")

    def update_image(self):
        if self.current_img_path:
            self.display_image(self.current_img_path)

    def zoom_in(self):
        self.current_image_scale += 0.1
        self.update_image()

    def zoom_out(self):
        if self.current_image_scale > 0.1:
            self.current_image_scale -= 0.1
            self.update_image()

    def start_annotation_mode(self):
        if not self.annotation_mode_active:
            self.annotation_manager.annotation_name = simpledialog.askstring(
                "Adnotacja", "Podaj nazwę adnotacji:"
            ) or "Brak danych"

            self.annotation_mode_active = True

            self.app.add_annotation_btn.config(text="Zmień adnotację")

        self.canvas.bind("<ButtonPress-1>", self.annotation_manager.start_annotation)
        self.canvas.bind("<B1-Motion>", self.annotation_manager.update_annotation)
        self.canvas.bind("<ButtonRelease-1>", self.annotation_manager.finish_annotation)

    def change_annotation_name(self):
        self.annotation_manager.annotation_name = simpledialog.askstring(
            "Zmień adnotacje", "Podaj nazwę adnotacji:"
        ) or "Bez nazwy"

    def finish_annotation(self, event):
        self.annotation_manager.finish_annotation(event)
        self.annotation_mode_active = False

    def clear_selection(self):
        if self.selected_annotation:
            self.canvas.itemconfig(self.selected_annotation["rect"], outline="red")
            self.selected_annotation = None

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.canvas, tearoff=0)
        self.context_menu.add_command(label="Zmień nazwę", command=self.annotation_manager.change_annotation_name)
        self.context_menu.add_command(label="Usuń", command=self.annotation_manager.delete_selected_annotation)
        self.context_menu.add_command(label="Edytuj", command=self.annotation_manager.enter_edit_mode)
        self.context_menu.add_command(label="Zakończ edycję", command=self.annotation_manager.exit_edit_mode)

        self.canvas.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        self.annotation_manager.select_annotation(event)
        if self.annotation_manager.selected_annotation:
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def save_annotations_to_coco(self):
        if not self.current_img_path:
            print("No image loaded.")
            return

        img_width, img_height = self.photo_img.width(), self.photo_img.height()
        img_id = self.coco_exporter.add_image(
            file_name=self.current_img_path.split("/")[-1],
            width=img_width,
            height=img_height
        )

        for annotation in self.annotation_manager.annotations:
            x1, y1 = annotation["x1"], annotation["y1"]
            x2, y2 = annotation["x2"], annotation["y2"]
            object_name = annotation["name"]
            self.coco_exporter.add_annotation(img_id, x1, y1, x2, y2, object_name)

        save_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if save_path:
            self.coco_exporter.save_to_file(save_path)

    def load_annotations(self):
        file_path = filedialog.askopenfilename(
            title="Load Annotations",
            filetypes=[("JSON files", "*.json")]
        )
        if not file_path:  # Jeśli użytkownik anulował to przerwij
            return

        # Załaduj adnotacje
        self.coco_exporter.load_from_coco(file_path, self)


