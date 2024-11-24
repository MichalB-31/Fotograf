import json
from tkinter import filedialog
from PIL import Image, ImageTk

class CocoManager:
    def __init__(self, canvas):
        self.data = {
            "images": [],
            "annotations": [],
            "categories": [],
            "info": {},
        }
        self.annotation_id = 1
        self.category_id_map = {}
        self.annotations = []
        self.categories = [{"id": 1, "name": "default"}]
        self.images = []
        self.canvas = canvas

    def add_image(self, file_name, width, height):
        image_id = len(self.data["images"]) + 1
        self.data["images"].append({
            "id": image_id,
            "file_name": file_name,
            "width": width,
            "height": height
        })
        return image_id

    def add_category(self, object_name):
        if object_name not in self.category_id_map:
            category_id = len(self.data["categories"]) + 1
            self.data["categories"].append({
                "id": category_id,
                "name": object_name,
            })
            self.category_id_map[object_name] = category_id
        return self.category_id_map[object_name]

    def add_annotation(self, image_id, x1, y1, x2, y2, object_name):
        category_id = self.add_category(object_name)

        width = abs(x2 - x1)
        height = abs(y2 - y1)

        self.data["annotations"].append({
            "id": self.annotation_id,
            "image_id": image_id,
            "category_id": category_id,
            "bbox": [x1, y1, width, height],
            "area": width * height,
            "iscrowd": 0
        })
        self.annotation_id += 1

    def add_metadata(self, metadata):
        """Dodaj metadane"""
        self.data["info"].update(metadata)

    def save_to_file(self, file_path):
        import json
        with open(file_path, "w") as f:
            json.dump(self.data, f, indent=4)

    def load_from_coco(self, file_path, view_manager):
        with open(file_path, 'r') as f:
            coco_data = json.load(f)

        images = coco_data.get("images", [])
        annotations = coco_data.get("annotations", [])
        categories = {cat["id"]: cat["name"] for cat in coco_data.get("categories", [])}

        if not images:
            print("Brak obrazów w pliku COCO")
            return

        image_info = images[0]
        image_path = filedialog.askopenfilename(
            title="Wybierz obraz",
            initialfile=image_info["file_name"]
        )
        if not image_path:
            return

        img = Image.open(image_path)
        self.photo_img = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo_img)

        for annotation in annotations:
            if annotation["image_id"] == image_info["id"]:
                bbox = annotation["bbox"]
                x1, y1, x2, y2 = bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3]
                category_name = categories.get(annotation["category_id"], "Unknown")
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2)
                self.canvas.create_text(x1, y1 - 10, text=category_name, anchor="sw", fill="red")


