import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar
from PIL import Image, ImageTk
import os

class Fotograf:
    def __init__(self, root):
        self.root = root
        self.root.title("Fotograf")
        self.root.geometry("800x600")

        # Przycisk wyboru folderu
        self.select_folder_btn = tk.Button(root, text="Wybierz folder", command=self.select_folder)
        self.select_folder_btn.pack(pady=10)

        # Lista zdjęć po wybraniu folderu, na razie bęzie to tak prosto
        self.image_listbox = Listbox(root, width=30, height=20)
        self.image_listbox.pack(side=tk.LEFT, padx=10, pady=10)
        self.image_listbox.bind("<<ListboxSelect>>", self.on_image_select)

        # Do scrollowania zdjęć
        scrollbar = Scrollbar(root)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.image_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.image_listbox.yview)

        # Wyświetlania zdjęcia
        self.canvas = tk.Canvas(root, width=600, height=400, bg="gray")
        self.canvas.pack(pady=10)

        # Przechowywanie ścieżki do folderu i zdjęć
        self.folder_path = None
        self.image_files = []
        self.current_image_index = 0

    def select_folder(self):
        # Okno do wyboru folderu
        self.folder_path = filedialog.askdirectory()
        if not self.folder_path:
            return

        # Przegląanie plików w folderze
        self.image_files = [f for f in os.listdir(self.folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]

        if not self.image_files:
            messagebox.showinfo("Info", "Brak zdjęć w wybranym folderze.")
            return

        # Wyczyszczenie listy i dodanie nazw plików
        self.image_listbox.delete(0, tk.END)
        for img_file in self.image_files:
            self.image_listbox.insert(tk.END, img_file)

    def on_image_select(self, event):
        # Do zapamięania wybranego zdjęcia
        selection = event.widget.curselection()
        if selection:
            self.current_image_index = selection[0]
            self.display_image()

    def display_image(self):
        # Ładowanie i wyświetlanie obrazu
        img_path = os.path.join(self.folder_path, self.image_files[self.current_image_index])
        img = Image.open(img_path)
        img.thumbnail((600, 400))
        self.photo_img = ImageTk.PhotoImage(img)

        self.canvas.create_image(300, 200, image=self.photo_img)

if __name__ == "__main__":
    root = tk.Tk()
    app = Fotograf(root)
    root.mainloop()
