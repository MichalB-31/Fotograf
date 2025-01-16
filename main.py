import tkinter as tk
import customtkinter as ctk
from app import App

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

root = tk.Tk()
root.configure(background='#2fa572')
app = App(root)
root.state("zoomed")
root.mainloop()