import tkinter as tk
import customtkinter as ctk
from PIL import Image

class MainWindow:
    """Klasa reprezentująca główne okno aplikacji."""
    def __init__(self, app):
        self.app = app
        self.master = app.master

        self.create_widgets()
        self.configure_layout()

    def create_widgets(self):
        """Tworzy widgety w aplikacji."""
        folder_icon = ctk.CTkImage(Image.open("resources/folder.png"))
        add_class_icon = ctk.CTkImage(Image.open("resources/add_class.png"))
        undo_icon = ctk.CTkImage(Image.open("resources/undo.png"))
        redo_icon = ctk.CTkImage(Image.open("resources/redo.png"))
        save_coco_icon = ctk.CTkImage(Image.open("resources/json.png"))
        load_from_coco = ctk.CTkImage(Image.open("resources/file.png"))
        stats_icon = ctk.CTkImage(Image.open("resources/statistics.png"))
        exif_icon = ctk.CTkImage(Image.open("resources/exif.png"))
        exit_icon = ctk.CTkImage(Image.open("resources/exit.png"))

        # Kontener lewej strony
        left_frame = ctk.CTkFrame(self.master, width=140, corner_radius=0)
        left_frame.grid(row=0, column=0, padx=0, pady=5, sticky="nsew")
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_rowconfigure(4, weight=1)

        # Przycisk do wczytywania folderu
        self.file_button = ctk.CTkButton(left_frame, text="Wczytaj folder",image= folder_icon, command=self.app.folder_manager.load_folder,
                                         width=140, height=30)
        self.file_button.grid(row=0, column=0, padx=5, pady=(10, 5), sticky="ew")

        # Lista zdjęć
        self.image_listbox = tk.Listbox(left_frame, bg="#2E2E2E", fg="#DCE4EE", selectbackground="#2fa572",
                                        selectforeground="white", activestyle="none",
                                        font=("Arial", 12), height=10)
        self.image_listbox.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="nsew")
        self.image_listbox.bind("<<ListboxSelect>>", self.app.folder_manager.image_selected)

        # Lista klas
        self.class_listbox = tk.Listbox(left_frame, font=("Arial", 12), height=10, selectbackground="#2fa572",
                                        selectforeground="white", bg="#2E2E2E", fg="#DCE4EE", activestyle="none")
        self.class_listbox.grid(row=4, column=0, padx=5, pady=(0, 10), sticky="nsew")
        self.class_listbox.bind("<<ListboxSelect>>", self.app.annotation_manager.on_class_select)
        self.add_class_button = ctk.CTkButton(left_frame, text="Dodaj klasę", image=add_class_icon,
                                              command=self.app.annotation_manager.add_class, width=140,
                                              height=30)
        self.add_class_button.grid(row=3, column=0, padx=5, pady=(10, 5), sticky="ew")

        # Obszar wyświetlania obrazu
        self.image_label = tk.Canvas(self.master, bg="#2E2E2E", highlightthickness=0)
        self.image_label.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        # Bindowanie myszy
        self.image_label.bind("<ButtonPress-1>",
                              lambda event: self.app.annotation_manager.on_mouse_press(event))
        self.image_label.bind("<B1-Motion>",
                              lambda event: self.app.annotation_manager.on_mouse_drag(event))
        self.image_label.bind("<ButtonRelease-1>",
                              lambda event: self.app.annotation_manager.on_mouse_release(event))
        self.image_label.bind("<Button-3>",
                              lambda event: self.app.annotation_manager.on_right_click(event))
        self.image_label.bind("<Motion>",
                              lambda event: self.app.annotation_manager.on_mouse_motion(event))

        # -Przyciski cofnij i przywróć
        self.undo_button = ctk.CTkButton(left_frame, text="Cofnij", image=undo_icon, command=self.app.undo, width=140, height=30)
        self.undo_button.grid(row=5, column=0, padx=5, pady=(10, 5), sticky="ew")
        self.redo_button = ctk.CTkButton(left_frame, text="Przywróć", image=redo_icon, command=self.app.redo, width=140, height=30)
        self.redo_button.grid(row=6, column=0, padx=5, pady=(10, 10), sticky="ew")

        # Prawy panel aplikacji
        right_frame = ctk.CTkFrame(self.master, corner_radius=0)
        right_frame.grid(row=0, column=5, padx=0, pady=5, sticky="nsew")
        right_frame.grid_rowconfigure(6, weight=1)

        # Dane dodatkowe
        self.predefined_data_frame = tk.Frame(right_frame, bg="#2E2E2E")
        self.predefined_data_frame.grid(row=5, column=0, padx=0, pady=5, sticky="w")
        self.app.data_manager.create_predefined_data_fields()

        self.save_to_coco_button = ctk.CTkButton(right_frame, text="Zapisz do COCO", image=save_coco_icon, command=self.app.save_coco, width=140,
                                          height=30)
        self.save_to_coco_button.grid(row=0, column=0, padx=5, pady=(10, 5), sticky="ew")

        self.load_from_coco_button = ctk.CTkButton(right_frame, text="Wczytaj COCO", image=load_from_coco,
                                                                     command=self.app.load_coco, width=140,
                                                                     height=30)
        self.load_from_coco_button.grid(row=1, column=0, padx=5, pady=(10, 5), sticky="ew")

        self.stats_button = ctk.CTkButton(right_frame, text="Statystyki", image=stats_icon, command=self.app.show_stats, width=140,
                                          height=30)
        self.stats_button.grid(row=2, column=0, padx=5, pady=(10, 5), sticky="ew")

        self.exif_button = ctk.CTkButton(right_frame, text="Pokaż EXIF", image=exif_icon, command=self.app.data_manager.show_exif,
                                         width=140,
                                         height=30)
        self.exif_button.grid(row=3, column=0, padx=5, pady=(10, 5), sticky="ew")

        self.exit_button = ctk.CTkButton(right_frame, fg_color="grey", hover_color="red",
                                         text="Wyjście", image=exit_icon, command=self.app.on_closing,
                                         width=140,
                                         height=30)
        self.exit_button.grid(row=6, column=0, padx=5, pady=(10, 10), sticky="sew")
        self.master.protocol("WM_DELETE_WINDOW", self.app.on_closing)

    def configure_layout(self):
        """Konfiguruje układ okna głównego."""
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(5, weight=0)