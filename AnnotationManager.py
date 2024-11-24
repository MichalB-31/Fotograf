from tkinter import simpledialog

class AnnotationManager:
    def __init__(self, canvas):
        self.canvas = canvas
        self.annotations = []
        self.current_annotation = None
        self.annotation_name = ""
        self.selected_annotation = None
        self.resize_mode = None
        self.resize_margin = 10
        self.edit_mode = None

    def start_annotation(self, event):
        """Rozpoczyna adnotowanie"""
        self.current_annotation = {
            "x1": event.x,
            "y1": event.y,
            "rect": self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="red"),
            "name": self.annotation_name
        }

    def display_annotations(self):
        """Wyświetlanie adnotacji"""
        for annotation in self.annotations:
            self.canvas.create_rectangle(
                annotation["x1"], annotation["y1"], annotation["x2"], annotation["y2"],
                outline="red", width=2
            )
            self.canvas.create_text(annotation["x1"], annotation["y1"] - 10,
                                    text=annotation["name"], anchor="sw", fill="red")

    def update_annotation(self, event):
        """Zmiana adnotacji w trakcie tworzenia - przeciagania myszką"""
        if self.current_annotation:
            print(f"Aktualizowanie adnotacji na: ({event.x}, {event.y})") # do testu
            self.canvas.coords(
                self.current_annotation["rect"],
                self.current_annotation["x1"],
                self.current_annotation["y1"],
                event.x,
                event.y
            )

    def finish_annotation(self, event):
        """Stworzenie adnotacji"""
        if self.current_annotation:
            x1, y1 = self.current_annotation["x1"], self.current_annotation["y1"]
            x2, y2 = event.x, event.y

            if abs(x2 - x1) > 5 and abs(y2 - y1) > 5:
                self.current_annotation["x2"], self.current_annotation["y2"] = x2, y2
                self.current_annotation["text"] = self.canvas.create_text(
                    x1, y1 - 10, text=self.current_annotation["name"], anchor="sw", fill="red"
                )
                self.annotations.append(self.current_annotation)
            else:
                self.canvas.delete(self.current_annotation["rect"])
            self.current_annotation = None


    def select_annotation(self, event):
        """Funkcja do wyboru adnotacji na potrzeby edycji, usuwania"""
        self.selected_annotation = None
        margin = 5
        print("Wywołanie select") # test

        for annotation in self.annotations:
            x1, y1, x2, y2 = annotation["x1"], annotation["y1"], annotation["x2"], annotation["y2"]

            if (x1 - margin) <= event.x <= (x2 + margin) and (y1 - margin) <= event.y <= (y2 + margin):
                self.selected_annotation = annotation
                self.canvas.itemconfig(annotation["rect"], outline="blue")
                print(f"Select na ({x1}, {y1}), ({x2}, {y2})")
                break
            else:
                self.canvas.itemconfig(annotation["rect"], outline="red")

    def change_annotation_name(self):
        """Zamiana nazwy adnotacji"""
        if self.selected_annotation:
            new_name = simpledialog.askstring("Zmień nazwę", "Podaj nową nazwę:")
            if new_name:
                self.selected_annotation["name"] = new_name
                self.canvas.itemconfig(self.selected_annotation["text"], text=new_name)

    def delete_selected_annotation(self):
        """Usuwanie adnotacji"""
        if self.selected_annotation:
            self.canvas.delete(self.selected_annotation["rect"])
            self.canvas.delete(self.selected_annotation["text"])
            self.annotations.remove(self.selected_annotation)
            self.selected_annotation = None

    def enter_edit_mode(self):
        """Wejscie w tryb edycji"""
        if self.selected_annotation:
            self.canvas.itemconfig(self.selected_annotation["rect"], outline="green")
            self.edit_mode = True
            self.canvas.bind("<ButtonPress-1>", self.start_drag_side)
            self.canvas.bind("<B1-Motion>", self.drag_side)
            self.canvas.bind("<ButtonRelease-1>", self.finish_drag_side)

    def start_drag_side(self, event):
        """Rozpoznanie boku prostokąta do edycji i rozpoczecie przeciagania"""
        if not self.edit_mode or not self.selected_annotation:
            return

        # Pobranie współrzędnych adnotacji
        rect_coords = self.canvas.coords(self.selected_annotation["rect"])
        if not rect_coords:
            print("Nie można pobrać współrzędnych prostokąta.")
            return

        x, y = event.x, event.y
        x1, y1, x2, y2 = rect_coords

        # Znajdz o który bok chodzi
        margin = 5
        if abs(y - y1) <= margin:
            self.editing_side = "top"
        elif abs(y - y2) <= margin:
            self.editing_side = "bottom"
        elif abs(x - x1) <= margin:
            self.editing_side = "left"
        elif abs(x - x2) <= margin:
            self.editing_side = "right"

    def drag_side(self, event):
        """Przeciąganie wybranego boku"""
        if not self.editing_side:
            return

        x, y = event.x, event.y
        x1, y1, x2, y2 = self.canvas.coords(self.selected_annotation["rect"])

        if self.editing_side == "top":
            self.canvas.coords(self.selected_annotation["rect"], x1, y, x2, y2)
        elif self.editing_side == "bottom":
            self.canvas.coords(self.selected_annotation["rect"], x1, y1, x2, y)
        elif self.editing_side == "left":
            self.canvas.coords(self.selected_annotation["rect"], x, y1, x2, y2)
        elif self.editing_side == "right":
            self.canvas.coords(self.selected_annotation["rect"], x1, y1, x, y2)

    def finish_drag_side(self, event):
        """Kończy przeciąganie boku"""
        self.editing_side = None

    def exit_edit_mode(self):
        """Zakończ tryb edycji i przywróć możliwość dodawania nowych adnotacji"""
        if not self.edit_mode:
            return

        print("Zakończono edycję.")
        self.edit_mode = False
        self.selected_annotation = None

        # Przywrócenie zdarzeń do trybu dodawania adnotacji
        self.canvas.bind("<ButtonPress-1>", self.start_annotation)
        self.canvas.bind("<B1-Motion>", self.update_annotation)
        self.canvas.bind("<ButtonRelease-1>", self.finish_annotation)






