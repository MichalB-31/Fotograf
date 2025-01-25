import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import customtkinter as ctk

class AnnotationManager:
    """Klasa do zarządzania adnotacjami"""
    def __init__(self, app):
        self.app = app
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.rect = None
        self.selected_annotation_index = None
        self.moving = False
        self.resizing = False
        self.resize_corner = None
        self.resizing_mode = False
        self.circle_radius = 5
        self.corner_circles = []
        self.temp_old_bbox = None

    def on_class_select(self, event):
        """Zaznaczenie klasy na liście klas."""
        widget = event.widget
        selection = widget.curselection()
        if selection:
            index = selection[0]
            class_name = widget.get(index)
            self.app.active_class.set(class_name)
        else:
            self.app.active_class.set("")

    def add_class(self):
        """Dodanie nowej klasy do listy klas."""
        dialog = ctk.CTkInputDialog(text="Nazwa nowej klasy:", title="Dodaj klasę")

        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        dialog_width = 300
        dialog_height = 150
        dialog.geometry(f"{dialog_width}x{dialog_height}")
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        dialog.geometry(f"+{x}+{y}")

        new_class = dialog.get_input()

        if new_class:
            if new_class not in self.app.classes:
                self.app.classes.append(new_class)
                self.app.class_listbox.insert(tk.END, new_class)
            else:
                messagebox.showerror("Błąd", "Klasa o tej nazwie już istnieje!")

    def on_mouse_press(self, event):
        """Rozpoczyna rysowanie, przesuwanie lub zmianę rozmiaru adnotacji."""
        self.ix, self.iy = event.x, event.y
        clicked_x, clicked_y = event.x, event.y
        if self.resizing_mode and self.selected_annotation_index is not None:
            image_filename = self.app.image_files[self.app.current_image_index]
            bbox = self.app.annotations[image_filename][self.selected_annotation_index]["bbox"]

            tolerance = self.circle_radius + 5
            if abs(clicked_x - bbox[0]) < tolerance and abs(clicked_y - bbox[1]) < tolerance:
                self.moving = True
                self.temp_old_bbox = bbox.copy()
            elif abs(clicked_x - (bbox[0] + bbox[2])) < tolerance and abs(clicked_y - (bbox[1] + bbox[3])) < tolerance:
                self.resizing = True
                self.resize_corner = "bottom_right"
                self.temp_old_bbox = bbox.copy()
            else:
                self.disable_resizing_mode()
                self.app.image_manager.draw_annotations()

        elif not self.resizing:
            self.selected_annotation_index = None
            self.drawing = True
            self.disable_resizing_mode()
            self.app.image_manager.draw_annotations()

    def on_mouse_drag(self, event):
        """Rysuje,przesuwa lub zmienia rozmiar adnotacji."""
        if self.drawing:
            cur_x = event.x
            cur_y = event.y

            if self.rect:
                self.app.image_label.delete(self.rect)

            img_copy = self.app.current_image.copy()
            img_copy_with_rect = cv2.rectangle(img_copy, (self.ix, self.iy), (cur_x, cur_y), (0, 255, 0), 2)
            self.app.image_manager.current_image_tk = ImageTk.PhotoImage(image=Image.fromarray(img_copy_with_rect))
            self.app.image_label.create_image(0, 0, anchor=tk.NW, image=self.app.image_manager.current_image_tk)

        elif self.resizing and self.selected_annotation_index is not None:
            cur_x = event.x
            cur_y = event.y
            image_filename = self.app.image_files[self.app.current_image_index]
            bbox = self.app.annotations[image_filename][self.selected_annotation_index]["bbox"]
            bbox[2] = cur_x - bbox[0]
            bbox[3] = cur_y - bbox[1]

            # Zabezpieczenie przed ujemnymi wartościami
            if bbox[2] < 0:
                bbox[0] += bbox[2]
                bbox[2] = abs(bbox[2])
            if bbox[3] < 0:
                bbox[1] += bbox[3]
                bbox[3] = abs(bbox[3])

            self.app.image_manager.draw_annotations()

        elif self.moving and self.selected_annotation_index is not None:
            cur_x = event.x
            cur_y = event.y
            image_filename = self.app.image_files[self.app.current_image_index]
            bbox = self.app.annotations[image_filename][self.selected_annotation_index]["bbox"]

            dx = cur_x - self.ix
            dy = cur_y - self.iy

            bbox[0] += dx
            bbox[1] += dy

            self.ix = cur_x
            self.iy = cur_y
            self.app.image_manager.draw_annotations()

    def on_mouse_release(self, event):
        """ Kończy rysowanie, przesuwanie lub zmianę rozmiaru adnotacji."""
        if self.drawing:
            self.drawing = False
            x0, y0 = self.ix, self.iy
            x1, y1 = event.x, event.y
            x_min, x_max = sorted((x0, x1))
            y_min, y_max = sorted((y0, y1))

            if self.app.image_files and (x_max - x_min) > 0 and (y_max - y_min) > 0:
                image_filename = self.app.image_files[self.app.current_image_index]
                if not self.app.active_class.get():
                    messagebox.showwarning("Brak klasy", "Wybierz klasę z listy przed dodaniem adnotacji.")
                    self.app.image_manager.draw_annotations()
                    return

                # Dodanie adnotacji
                new_annotation = {
                    "bbox": [x_min, y_min, x_max - x_min, y_max - y_min],
                    "class": self.app.active_class.get()
                }
                # Dodanie operacji do historii
                self.app.history_manager.add_create_annotation_operation(image_filename, new_annotation)
                if image_filename not in self.app.annotations:
                    self.app.annotations[image_filename] = []
                self.app.annotations[image_filename].append(new_annotation)
                self.app.image_manager.draw_annotations()

        elif self.resizing and self.selected_annotation_index is not None:
            self.resizing = False
            image_filename = self.app.image_files[self.app.current_image_index]
            new_bbox = self.app.annotations[image_filename][self.selected_annotation_index]["bbox"]

            if self.temp_old_bbox != new_bbox:
                self.app.history_manager.add_resize_annotation_operation(image_filename,
                                                                         self.selected_annotation_index,
                                                                         self.temp_old_bbox, new_bbox)
                self.app.image_manager.draw_annotations()

        elif self.moving and self.selected_annotation_index is not None:
            self.moving = False
            image_filename = self.app.image_files[self.app.current_image_index]
            new_bbox = self.app.annotations[image_filename][self.selected_annotation_index]["bbox"]

            if self.temp_old_bbox != new_bbox:
                self.app.history_manager.add_move_annotation_operation(image_filename,
                                                                       self.selected_annotation_index,
                                                                       self.temp_old_bbox, new_bbox)
                self.app.image_manager.draw_annotations()

    def on_right_click(self, event):
        """Otwiera menu kontekstowe dla adnotacji."""
        clicked_x = event.x
        clicked_y = event.y
        self.selected_annotation_index = None
        self.resize_corner = None

        if self.app.image_files:
            image_filename = self.app.image_files[self.app.current_image_index]
            if image_filename in self.app.annotations:
                for i, annotation in enumerate(self.app.annotations[image_filename]):
                    bbox = annotation["bbox"]

                    tolerance = 10
                    if bbox[0] - tolerance <= clicked_x <= bbox[0] + bbox[2] + tolerance and bbox[
                        1] - tolerance <= clicked_y <= bbox[1] + bbox[3] + tolerance:
                        self.selected_annotation_index = i
                        break

                if self.selected_annotation_index is not None:
                    context_menu = tk.Menu(self.app.master, tearoff=0)
                    context_menu.add_command(label="Zmień nazwę", command=self.change_annotation_name)
                    context_menu.add_command(label="Usuń", command=self.delete_selected_annotation)
                    context_menu.add_command(label="Dostosuj", command=self.enable_resizing_mode)

                    try:
                        context_menu.tk_popup(event.x_root, event.y_root)
                    finally:
                        context_menu.grab_release()
        self.app.image_manager.draw_annotations()

    def on_mouse_motion(self, event):
        """Zmiana kursora w zależności od kontekstu"""
        if self.resizing_mode and self.selected_annotation_index is not None:
            image_filename = self.app.image_files[self.app.current_image_index]
            bbox = self.app.annotations[image_filename][self.selected_annotation_index]["bbox"]
            tolerance = self.circle_radius + 5

            if abs(event.x - bbox[0]) < tolerance and abs(event.y - bbox[1]) < tolerance:
                self.app.image_label.config(cursor="hand2")
            elif abs(event.x - (bbox[0] + bbox[2])) < tolerance and abs(event.y - (bbox[1] + bbox[3])) < tolerance:
                self.app.image_label.config(cursor="sizing")
            else:
                self.app.image_label.config(cursor="")
        else:
            self.app.image_label.config(cursor="")

    def change_annotation_name(self):
        """Zmiana nazwę klasy wybranej adnotacji."""
        if self.selected_annotation_index is not None and self.app.image_files:
            image_filename = self.app.image_files[self.app.current_image_index]
            if image_filename in self.app.annotations:
                old_class = self.app.annotations[image_filename][self.selected_annotation_index]["class"]

                dialog = ctk.CTkInputDialog(text="Nowa nazwa klasy:", title="Zmień nazwę klasy", )
                screen_width = dialog.winfo_screenwidth()
                screen_height = dialog.winfo_screenheight()

                dialog_width = 300
                dialog_height = 150
                dialog.geometry(f"{dialog_width}x{dialog_height}")

                x = (screen_width - dialog_width) // 2
                y = (screen_height - dialog_height) // 2
                dialog.geometry(f"+{x}+{y}")
                new_class_name = dialog.get_input()

                if new_class_name and new_class_name != old_class:
                    bbox = self.app.annotations[image_filename][self.selected_annotation_index]["bbox"]
                    self.app.history_manager.add_change_class_operation(image_filename, bbox, old_class, new_class_name)
                    self.app.annotations[image_filename][self.selected_annotation_index]["class"] = new_class_name
                    self.app.image_manager.draw_annotations()

                    # Dodanie nowej klasy do listyjeśli nie istnieje
                    if new_class_name not in self.app.classes:
                        self.app.classes.append(new_class_name)
                        self.app.class_listbox.insert(tk.END, new_class_name)

    def delete_selected_annotation(self):
        """Usuń wybraną adnotacje"""
        if self.selected_annotation_index is not None and self.app.image_files:
            image_filename = self.app.image_files[self.app.current_image_index]
            if image_filename in self.app.annotations:
                deleted_annotation = self.app.annotations[image_filename].pop(self.selected_annotation_index)
                self.app.history_manager.add_delete_annotation_operation(image_filename, deleted_annotation,
                                                                        self.selected_annotation_index)
                self.selected_annotation_index = None
                self.disable_resizing_mode()
                self.app.image_manager.draw_annotations()

    def enable_resizing_mode(self):
        """Włącz tryb zmiany rozmiaru adnotacji."""
        self.resizing_mode = True
        self.app.image_manager.draw_annotations()

    def disable_resizing_mode(self):
        """ Wyłącz tryb zmiany rozmiaru adnotacji."""
        self.resizing_mode = False
        self.resize_corner = None
        self.app.image_manager.clear_corner_circles()
        self.app.image_manager.draw_annotations()

