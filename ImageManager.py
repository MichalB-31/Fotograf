import tkinter as tk
import cv2
from PIL import Image, ImageTk, ImageFont, ImageDraw
import numpy as np

class ImageManager:
    """Klasa do zarządzania wyświetlaniem obrazu i adnotacji."""
    def __init__(self, app):
        self.app = app
        self.current_image_tk = None

    def display_image(self):
        """Wyświetl obraz na"""
        if self.app.current_image is not None:
            img_height, img_width, _ = self.app.current_image.shape
            label_width = self.app.image_label.winfo_width()
            label_height = self.app.image_label.winfo_height()

            # Wyśrodkowanie obrazu
            x = (label_width - img_width) // 2
            y = (label_height - img_height) // 2

            # Skalowanie obrazu
            if img_width > label_width or img_height > label_height:
                if img_width > img_height:
                    new_width = label_width
                    new_height = int(img_height * (label_width / img_width))
                else:
                    new_height = label_height
                    new_width = int(img_width * (label_height / img_height))
                self.app.current_image = cv2.resize(self.app.current_image, (new_width, new_height),
                                                    interpolation=cv2.INTER_LANCZOS4)
                x = (label_width - new_width) // 2
                y = (label_height - new_height) // 2

            self.current_image_tk = ImageTk.PhotoImage(image=Image.fromarray(self.app.current_image))
            self.app.image_label.create_image(x, y, anchor=tk.NW, image=self.current_image_tk)

    def draw_annotations(self):
        """Rysuje adnotacje"""
        if self.app.current_image is not None:
            img_copy = self.app.current_image.copy()
            # Załaduj cziconke
            font_path = "Roboto-Regular.ttf"
            try:
                font = ImageFont.truetype(font_path, 20)
            except IOError:
                print(f"Nie można załadować fontu z {font_path}. Używam domyślnego fontu.")
                font = None

            if self.app.image_files:
                image_filename = self.app.image_files[self.app.current_image_index]
                if image_filename in self.app.annotations:
                    for i, annotation in enumerate(self.app.annotations[image_filename]):
                        bbox = annotation["bbox"]
                        class_name = annotation["class"]
                        color = (0, 0, 255) if i == self.app.annotation_manager.selected_annotation_index else (
                        0, 255, 0)

                        cv2.rectangle(img_copy, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), color, 2)

                        if font:
                            img_pil = Image.fromarray(img_copy)
                            draw = ImageDraw.Draw(img_pil)
                            draw.text((bbox[0], bbox[1] - 25), class_name, font=font, fill=color)
                            img_copy = np.array(img_pil)
                        else:
                            cv2.putText(img_copy, class_name, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                                        color, 2)
                        if self.app.annotation_manager.resizing_mode and i == self.app.annotation_manager.selected_annotation_index:
                            self.draw_corner_circles(bbox)

            self.current_image_tk = ImageTk.PhotoImage(image=Image.fromarray(img_copy))
            self.app.image_label.create_image(0, 0, anchor=tk.NW, image=self.current_image_tk)

    def draw_corner_circles(self, bbox):
        """Rogi adnotacji do złapania"""
        self.clear_corner_circles()

        corners = [
            (bbox[0], bbox[1]),  # Top-left
            (bbox[0] + bbox[2], bbox[1] + bbox[3])  # Bottom-right
        ]

        for x, y in corners:
            circle = self.app.image_label.create_oval(
                x - self.app.annotation_manager.circle_radius, y - self.app.annotation_manager.circle_radius,
                x + self.app.annotation_manager.circle_radius, y + self.app.annotation_manager.circle_radius,
                fill="red", outline="black"
            )
            self.app.annotation_manager.corner_circles.append(circle)

    def clear_corner_circles(self):
        """Usuwa oznaczenia z rogów"""
        for circle in self.app.annotation_manager.corner_circles:
            self.app.image_label.delete(circle)
        self.app.annotation_manager.corner_circles = []