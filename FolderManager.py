from tkinter import filedialog


class FolderManager:
    def __init__(self, app):
        self.app = app
        self.folders = []
        self.folder_path = None

    def add_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path and folder_path not in self.folders:
            self.folders.append(folder_path)
            self.app.folder_listbox.insert("end", folder_path)

    def remove_folder(self):
        selection = self.app.folder_listbox.curselection()
        if selection:
            index = selection[0]
            self.app.folder_listbox.delete(index)
            del self.folders[index]
            self.app.image_listbox.delete(0, "end")
            self.app.image_display.clear_canvas()

    def on_folder_select(self, event):
        selection = event.widget.curselection()
        if selection:
            folder_index = selection[0]
            self.folder_path = self.folders[folder_index]
            print(f"Wybrano katalog: {self.folder_path}")
            self.app.view_manager.load_images_from_folder(self.folder_path)
