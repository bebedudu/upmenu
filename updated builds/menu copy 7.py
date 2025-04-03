# added more buttons and made the menu more compact

import tkinter as tk
from tkinter import messagebox
import os
import ctypes
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import atexit
import sys
import subprocess

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.command = command
        self.text = text
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.configure(bg="#222222", highlightthickness=0, highlightbackground="lightgray")
        
        # Store the rectangle id for later modification
        self.rect_id = self.create_rounded_rect(10, 10, 190, 50, 20, fill="lightgray", outline="#ffffff")
        self.text_id = self.create_text(100, 30, text=self.text, font=("Arial", 12), fill="black")
        self.config(cursor="hand2")

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
        # Just modify the existing rectangle instead of creating a new one
        self.itemconfig(self.rect_id, fill="#333333", outline="lightgray")
        self.itemconfig(self.text_id, fill="white")

    def _on_release(self, event):
        # Restore original colors of existing rectangle
        self.itemconfig(self.rect_id, fill="lightgray", outline="#333333")
        self.itemconfig(self.text_id, fill="black")
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

# Add a global variable to track mouse position
last_mouse_position = (0, 0)
hide_timer = None

# Add a global variable to track the audio interface
audio_interface = None

class AudioController:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioController, cls).__new__(cls)
            cls._instance._init_audio()
        return cls._instance
    
    def _init_audio(self):
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))
    
    def __del__(self):
        if hasattr(self, 'interface') and self.interface:
            try:
                self.interface.Release()
            except:
                pass

def is_speaker_muted():
    try:
        controller = AudioController()
        return controller.volume.GetMute()
    except Exception as e:
        print(f"Error checking mute status: {e}")
        return False

def mute_speakers():
    try:
        controller = AudioController()
        controller.volume.SetMute(1, None)
        print("Speakers muted.")
        mute_button.update_text("Unmute Speaker")
        mute_button.command = unmute_speakers
    except Exception as e:
        print(f"Error muting speakers: {e}")

def unmute_speakers():
    try:
        controller = AudioController()
        controller.volume.SetMute(0, None)
        print("Speakers unmuted.")
        mute_button.update_text("Mute Speaker")
        mute_button.command = mute_speakers
    except Exception as e:
        print(f"Error unmuting speakers: {e}")

def task_view():
    ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)  # Press Windows key
    ctypes.windll.user32.keybd_event(0x09, 0, 0, 0)  # Press Tab key
    ctypes.windll.user32.keybd_event(0x09, 0, 2, 0)  # Release Tab key
    ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)  # Release Windows key

def lock_screen():
    ctypes.windll.user32.LockWorkStation()


def restart_programs():
    python = sys.executable
    subprocess.Popen([python] + sys.argv)
    root.destroy()
    
def close_menu():
    root.destroy()

root = tk.Tk()
root.title("Rounded Rectangular Menu")
root.overrideredirect(True)  # Remove window decorations
root.attributes("-topmost", True)  # Keep window always on top

# Add rounded corners to the window
root.attributes("-transparentcolor", "white")
root.configure(bg="white", highlightthickness=0)

# Function to create rounded rectangle
def create_rounded_rect(canvas, x1, y1, x2, y2, radius=25, **kwargs):
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
    return canvas.create_polygon(points, **kwargs, smooth=True)

# Add the create_rounded_rect method to the Canvas class
tk.Canvas.create_rounded_rect = create_rounded_rect

# Now create the canvas and draw the rounded rectangle
canvas = tk.Canvas(root, width=800, height=200, bg="white", highlightthickness=0, highlightbackground="lightgray")
canvas.pack()

# Draw rounded rectangle
radius = 20
canvas.create_rounded_rect(0, 0, 800, 200, radius, fill="#222222", outline="lightgray")

# Center the window on the screen
window_width = 800
window_height = 200  # Reduced height for single row
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_top = 0  # Always at top of screen
position_right = int(screen_width / 2 - window_width / 2)
root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

# Initially hide the window
root.withdraw()

# Create a frame to hold the buttons using grid
button_frame = tk.Frame(canvas, bg="#222222")
button_frame.place(relx=0.5, rely=0.5, anchor="center")

buttons = [
    ("Shut Down", shut_down),
    ("Restart", restart),
    ("Show/Hide Desktop", show_desktop),
    ("Task View", task_view),
    ("Lock Screen", lock_screen),
    ("Restart Programs", restart_programs),
    ("Close Menu", close_menu)
]

button_widgets = []

for text, command in buttons:
    button = RoundedButton(button_frame, text, command, width=200, height=60)
    button_widgets.append(button)

mute_button = RoundedButton(button_frame, "Mute Speaker" if not is_speaker_muted() else "Unmute Speaker", mute_speakers if not is_speaker_muted() else unmute_speakers, width=200, height=60)
button_widgets.insert(3, mute_button)

def arrange_buttons(event=None):
    for widget in button_frame.winfo_children():
        widget.grid_forget()
    
    # Fixed button dimensions
    button_width = 210  # Width of button + padding
    min_spacing = 1    # Minimum spacing between buttons
    
    # Get available width
    available_width = max(800, root.winfo_width()) - 40  # Use at least 800px width
    
    # Calculate how many buttons can fit in a row
    buttons_per_row = max(1, min(len(button_widgets), (available_width + min_spacing) // (button_width + min_spacing)))
    
    # Calculate rows needed
    total_buttons = len(button_widgets)
    rows = (total_buttons + buttons_per_row - 1) // buttons_per_row
    
    # Calculate spacing to center buttons
    total_width = buttons_per_row * button_width
    spacing = max(min_spacing, (available_width - total_width) // (buttons_per_row + 1))
    
    # Place buttons in grid
    for i, button in enumerate(button_widgets):
        row = i // buttons_per_row
        col = i % buttons_per_row
        button.grid(row=row, 
                   column=col, 
                   padx=spacing,
                   pady=1)
        
        # Configure column weight for even spacing
        button_frame.grid_columnconfigure(col, weight=1)
    
    # Configure row weight for vertical centering
    for row in range(rows):
        button_frame.grid_rowconfigure(row, weight=1)

    # Update frame size
    button_frame.update_idletasks()

def update_mute_button():
    if is_speaker_muted():
        mute_button.update_text("Unmute Speaker")
        mute_button.command = unmute_speakers
    else:
        mute_button.update_text("Mute Speaker")
        mute_button.command = mute_speakers
    root.after(1000, update_mute_button)  # Check every second

def check_mouse_position():
    global last_mouse_position, hide_timer
    
    x, y = root.winfo_pointerxy()
    last_mouse_position = (x, y)
    
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    center_left = (screen_width - 800) // 2  # Calculate left boundary of center 800px
    center_right = center_left + 800         # Calculate right boundary
    
    # Show window only if mouse is at top AND within center 800px
    if y < 5 and center_left <= x <= center_right:
        if not root.winfo_viewable():
            root.deiconify()
        # Cancel any pending hide operation
        if hide_timer:
            root.after_cancel(hide_timer)
            hide_timer = None
    else:
        # Only hide if the mouse stays outside the window for 500ms
        if root.winfo_viewable() and not hide_timer:
            hide_timer = root.after(500, hide_window)
    
    root.after(100, check_mouse_position)


def hide_window():
    global hide_timer
    # Only hide if mouse is still outside the window
    x, y = last_mouse_position
    if y >= 30 and not root.winfo_containing(x, y):
        root.withdraw()
    hide_timer = None

root.bind("<Configure>", arrange_buttons)
arrange_buttons()
update_mute_button()
check_mouse_position()  # Start checking mouse position


# root.mainloop()
if __name__ == "__main__":
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting gracefully.")
    except Exception as e:
        print(f"Error in main loop: {e}")
