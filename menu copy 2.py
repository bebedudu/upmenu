# mute / unmute speaker is continously checked and updated and now menu is in center of screen

import tkinter as tk
from tkinter import messagebox
import os
import ctypes
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.command = command
        self.text = text
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.create_rounded_rect(10, 10, 190, 50, 20, fill="lightgrey")
        self.text_id = self.create_text(100, 30, text=self.text, font=("Arial", 12))

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def _on_press(self, event):
        self.config(relief="sunken")

    def _on_release(self, event):
        self.config(relief="raised")
        self.command()

    def update_text(self, new_text):
        self.itemconfig(self.text_id, text=new_text)

def shut_down():
    if messagebox.askokcancel("Confirmation", "Are you sure you want to shut down?"):
        os.system("shutdown /s /t 1")

def restart():
    if messagebox.askokcancel("Confirmation", "Are you sure you want to restart?"):
        os.system("shutdown /r /t 1")

def show_desktop():
    ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)  # Press Windows key
    ctypes.windll.user32.keybd_event(0x44, 0, 0, 0)  # Press D key
    ctypes.windll.user32.keybd_event(0x44, 0, 2, 0)  # Release D key
    ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)  # Release Windows key

def is_speaker_muted():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    return volume.GetMute()

def mute_speakers():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMute(1, None)
    print("Speakers muted.")
    mute_button.update_text("Unmute Speaker")
    mute_button.command = unmute_speakers

def unmute_speakers():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMute(0, None)
    print("Speakers unmuted.")
    mute_button.update_text("Mute Speaker")
    mute_button.command = mute_speakers

def task_view():
    ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)  # Press Windows key
    ctypes.windll.user32.keybd_event(0x09, 0, 0, 0)  # Press Tab key
    ctypes.windll.user32.keybd_event(0x09, 0, 2, 0)  # Release Tab key
    ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)  # Release Windows key

root = tk.Tk()
root.title("Rounded Rectangular Menu")

# Center the window on the screen
window_width = 800
window_height = 200
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)
root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

buttons = [
    ("Shut Down", shut_down),
    ("Restart", restart),
    ("Show Desktop", show_desktop),
    ("Task View", task_view)
]

button_widgets = []

for text, command in buttons:
    button = RoundedButton(root, text, command, width=200, height=60)
    button_widgets.append(button)

mute_button = RoundedButton(root, "Mute Speaker" if not is_speaker_muted() else "Unmute Speaker", mute_speakers if not is_speaker_muted() else unmute_speakers, width=200, height=60)
button_widgets.insert(3, mute_button)

def arrange_buttons(event=None):
    for widget in root.winfo_children():
        widget.grid_forget()
    width = root.winfo_width()
    columns = max(1, width // 210)
    total_button_width = columns * 210
    left_margin = max(0, (width - total_button_width) // 2)
    for i, button in enumerate(button_widgets):
        button.grid(row=i // columns, column=i % columns, padx=(left_margin if i % columns == 0 else 10, 10), pady=10)

def update_mute_button():
    if is_speaker_muted():
        mute_button.update_text("Unmute Speaker")
        mute_button.command = unmute_speakers
    else:
        mute_button.update_text("Mute Speaker")
        mute_button.command = mute_speakers
    root.after(1000, update_mute_button)  # Check every second

root.bind("<Configure>", arrange_buttons)
arrange_buttons()
update_mute_button()

root.mainloop()
