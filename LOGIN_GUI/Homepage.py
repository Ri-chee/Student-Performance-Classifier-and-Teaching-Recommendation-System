import tkinter as tk
from tkinter import messagebox
import json

with open("session.json", "r") as f:
    session = json.load(f)

UID = session["UID"]



root = tk.Tk()
label = tk.Label(root, text="GeeksForGeeks.org!")
label.pack()

root.mainloop()