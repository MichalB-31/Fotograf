import json
import os
from tkinter import filedialog
import tkinter as tk
import cv2

class CocoManager:
    """Klasa do zarządzania plikami COCO (zapis i odczyt)."""
    def __init__(self, app):
        self.app = app
        self.coco_folder = ""

    def save_coco(self, image_files, annotations, classes, image_data):

        def serialize_exif(exif_data):
            serialized = {}
            for k, v in exif_data.items():
                if isinstance(v, tuple):
                    serialized[k] = tuple(float(x) if isinstance(x, (int, float)) else str(x) for x in v)
                elif isinstance(v, bytes):
                    serialized[k] = v.decode('utf-8', errors='replace')
                else:
                    serialized[k] = str(v)
            return serialized

        coco_data = {
            "images": [],
            "annotations": [],
            "categories": [{"id": i + 1, "name": class_name} for i, class_name in enumerate(classes)],
            "info": {
                "images_data": {
                    image_filename: {
                        "predefined_data": image_data.get(image_filename, {}).get("predefined_data", {}),
                        "exif": serialize_exif(image_data.get(image_filename, {}).get("exif", {}))
                    } for image_filename in image_files
                }
            }
        }

        annotation_id = 1
        for image_id, image_filename in enumerate(image_files):
            annotations_for_image = annotations.get(image_filename, [])
            if image_filename in image_files:
                image_path = os.path.join(self.app.folder_manager.image_folder, image_filename)

                if not os.path.exists(image_path):
                    print(f"Błąd: Obraz {image_path} nie istnieje.")
                    continue

                img = cv2.imread(image_path)

                if img is None:
                    print(f"Błąd: Nie można wczytać obrazu {image_path}.")
                    continue

                height, width, _ = img.shape

                coco_data["images"].append({
                    "id": image_id + 1,
                    "width": width,
                    "height": height,
                    "file_name": image_filename,
                })

                for annotation in annotations_for_image:
                    bbox = annotation["bbox"]
                    class_name = annotation["class"]
                    category_id = classes.index(class_name) + 1

                    coco_data["annotations"].append({
                        "id": annotation_id,
                        "image_id": image_id + 1,
                        "category_id": category_id,
                        "bbox": bbox,
                        "area": bbox[2] * bbox[3],
                        "iscrowd": 0,
                    })
                    annotation_id += 1

        output_file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(coco_data, f, indent=4, ensure_ascii=False)

    def load_coco(self, image_files, annotations, classes, image_data, class_listbox):
        """Wczytuje adnotacje, dane i EXIF z pliku COCO."""
        coco_file = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if coco_file:
            with open(coco_file, "r") as f:
                coco_data = json.load(f)

            classes.clear()
            classes.extend([category["name"] for category in coco_data["categories"]])
            class_listbox.delete(0, tk.END)
            for class_name in classes:
                class_listbox.insert(tk.END, class_name)

            annotations.clear()
            for image_data_entry in coco_data["images"]:
                image_filename = image_data_entry["file_name"]
                annotations[image_filename] = []

            for annotation_data in coco_data["annotations"]:
                image_id = annotation_data["image_id"]
                image_filename = next((img["file_name"] for img in coco_data["images"] if img["id"] == image_id), None)
                if image_filename:
                    annotations[image_filename].append({
                        "bbox": annotation_data["bbox"],
                        "class": classes[annotation_data["category_id"] - 1]
                    })
            image_data.clear()

            # Wczytywanie danych dodatkowych i EXIF z pliku COCO
            for image_filename, img_data in coco_data["info"]["images_data"].items():
                image_data[image_filename] = {
                    "predefined_data": img_data.get("predefined_data", {}),
                    "exif": img_data.get("exif", {}),
                    "undo_stack": [],
                    "redo_stack": []
                }

            self.coco_folder = os.path.dirname(coco_file)
            return True
        return False