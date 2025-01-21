class HistoryManager:
    """Klasa do zarządzania historią operacji """
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def add_create_annotation_operation(self, image_filename, annotation):
        """Dodanie utworzenia adnotacji do historii. """
        self.undo_stack.append(("create", image_filename, annotation))
        self.redo_stack.clear()  # Wyczyszczenie stosu redo po nowej operacji

    def add_delete_annotation_operation(self, image_filename, deleted_annotation, index):
        """Dodanie usunięcia adnotacji do historii."""
        self.undo_stack.append(("delete", image_filename, deleted_annotation, index))
        self.redo_stack.clear()

    def add_resize_annotation_operation(self, image_filename, index, old_bbox, new_bbox):
        """Dodanie zmiany rozmiaru adnotacji do historii."""
        self.undo_stack.append(("resize", image_filename, index, old_bbox, new_bbox))
        self.redo_stack.clear()

    def add_move_annotation_operation(self, image_filename, index, old_bbox, new_bbox):
        """Dodanie przesunięcia adnotacji do historii."""
        self.undo_stack.append(("move", image_filename, index, old_bbox, new_bbox))
        self.redo_stack.clear()

    def add_change_class_operation(self, image_filename, bbox, old_class, new_class):
        """Dodanie zmiany klasy adnotacji do historii."""
        self.undo_stack.append(("change_class", image_filename, bbox, old_class, new_class))
        self.redo_stack.clear()

    def add_edit_data_operation(self, image_filename, old_predefined_data, old_dynamic_data, new_predefined_data, new_dynamic_data):
        """Dodanie edycji danych do historii."""
        self.undo_stack.append(("edit_data", image_filename, old_predefined_data, old_dynamic_data, new_predefined_data, new_dynamic_data))
        self.redo_stack.clear()

