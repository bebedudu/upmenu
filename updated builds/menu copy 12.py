# enhanced menu UI search and speaker control in single row

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
import webbrowser
from urllib.parse import quote
from pynput.keyboard import Key, Controller
import win32gui
import win32process
import psutil

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.command = command
        self.text = text
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.configure(bg="#222222", highlightthickness=0, highlightbackground="lightgray")
        
        # Adjust button dimensions based on canvas size
        canvas_width = kwargs.get('width', 200)
        canvas_height = kwargs.get('height', 60)
        
        # Calculate rectangle dimensions with padding
        rect_x1 = 10
        rect_y1 = 5
        rect_x2 = canvas_width - 10
        rect_y2 = canvas_height - 5
        
        # Store the rectangle id for later modification
        self.rect_id = self.create_rounded_rect(rect_x1, rect_y1, rect_x2, rect_y2, 20, 
                                              fill="lightgray", outline="#ffffff")
        # Center text
        text_x = canvas_width / 2
        text_y = canvas_height / 2
        self.text_id = self.create_text(text_x, text_y, text=self.text, 
                                      font=("Arial", 12), fill="black")
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

# Add these as global variables after other global declarations
speaker_mute_img = None
speaker_unmute_img = None

# Add global declarations at the top with other globals
search_entry = None
speaker_button = None
speaker_label_ref = None

# Move these functions up, after the global declarations and before create_media_controls
def get_active_media_player():
    """Check if any known media player is running"""
    media_players = [
        "spotify.exe", "musicbee.exe", "vlc.exe", "wmplayer.exe", 
        "groove music.exe", "chrome.exe", "msedge.exe", "firefox.exe"
    ]
    
    try:
        # Get active window process
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        
        if process.name().lower() in media_players:
            return True
    except:
        pass
    return False

def media_previous():
    keyboard = Controller()
    keyboard.press(Key.media_previous)
    keyboard.release(Key.media_previous)

def media_play_pause():
    keyboard = Controller()
    keyboard.press(Key.media_play_pause)
    keyboard.release(Key.media_play_pause)

def media_next():
    keyboard = Controller()
    keyboard.press(Key.media_next)
    keyboard.release(Key.media_next)

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
        # mute_button.update_text("Unmute Speaker")
        # mute_button.command = unmute_speakers
    except Exception as e:
        print(f"Error muting speakers: {e}")

def unmute_speakers():
    try:
        controller = AudioController()
        controller.volume.SetMute(0, None)
        print("Speakers unmuted.")
        # mute_button.update_text("Mute Speaker")
        # mute_button.command = mute_speakers
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

def search_google():
    query = search_entry.get().strip()
    if query:
        # Encode the search query for URL
        encoded_query = quote(query)
        url = f"https://www.bing.com/search?q={encoded_query}"
        webbrowser.open(url)
        search_entry.delete(0, tk.END)  # Clear the search box

def on_enter(event):
    search_google()

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
canvas = tk.Canvas(root, width=900, height=300, bg="white", highlightthickness=0, highlightbackground="lightgray")
canvas.pack()

# Draw rounded rectangle
radius = 20
canvas.create_rounded_rect(0, 0, 900, 300, radius, fill="#222222", outline="lightgray")

# Center the window on the screen
window_width = 900
window_height = 300  # Reduced height for single row
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
    # ("Shut Down", shut_down),
    # ("Restart", restart),
    # ("Show/Hide Desktop", show_desktop),
    # ("Task View", task_view),
    # ("Lock Screen", lock_screen),
    ("Restart Programs", restart_programs),
    ("Close Menu", close_menu)
]

button_widgets = []

for text, command in buttons:
    button = RoundedButton(button_frame, text, command, width=200, height=60)
    button_widgets.append(button)

# mute_button = RoundedButton(button_frame, "Mute Speaker" if not is_speaker_muted() else "Unmute Speaker", mute_speakers if not is_speaker_muted() else unmute_speakers, width=200, height=60)
# button_widgets.insert(3, mute_button)

# Move create_media_controls before create_top_controls
def create_media_controls(parent):
    media_frame = tk.Frame(parent, bg="#222222")
    
    # Create individual frames for each control (button + label)
    prev_control = tk.Frame(media_frame, bg="#222222")
    play_control = tk.Frame(media_frame, bg="#222222")
    next_control = tk.Frame(media_frame, bg="#222222")
    speaker_control = tk.Frame(media_frame, bg="#222222")
    
    # Load and resize media control images
    prev_img = tk.PhotoImage(file="assets/images/backward.png").subsample(15, 15)
    play_img = tk.PhotoImage(file="assets/images/playpause.png").subsample(15, 15)
    next_img = tk.PhotoImage(file="assets/images/forward.png").subsample(15, 15)
    
    # Load both speaker images and store them globally
    global speaker_mute_img, speaker_unmute_img
    speaker_mute_img = tk.PhotoImage(file="assets/images/volumemute.png").subsample(15, 15)
    speaker_unmute_img = tk.PhotoImage(file="assets/images/volumeup.png").subsample(15, 15)
    
    # Use the appropriate image based on current state
    current_speaker_img = speaker_mute_img if is_speaker_muted() else speaker_unmute_img
    
    # Create buttons with images and cursor style
    prev_btn = tk.Button(prev_control, image=prev_img, command=media_previous,
                        bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    play_btn = tk.Button(play_control, image=play_img, command=media_play_pause,
                        bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    next_btn = tk.Button(next_control, image=next_img, command=media_next,
                        bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    speaker_btn = tk.Button(speaker_control, image=current_speaker_img,
                        command=mute_speakers if not is_speaker_muted() else unmute_speakers,
                        bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    
    # Create labels with cursor style
    prev_label = tk.Label(prev_control, text="Previous", fg="lightgray",
                         bg="#222222", font=("Arial", 10), cursor="hand2")
    play_label = tk.Label(play_control, text="Play/Pause", fg="lightgray",
                         bg="#222222", font=("Arial", 10), cursor="hand2")
    next_label = tk.Label(next_control, text="Next", fg="lightgray",
                         bg="#222222", font=("Arial", 10), cursor="hand2")
    speaker_label = tk.Label(speaker_control,
                         text="Mute" if not is_speaker_muted() else "Unmute",
                         fg="lightgray", bg="#222222", font=("Arial", 10), cursor="hand2")
    
    # Bind labels to their respective commands
    prev_label.bind("<Button-1>", lambda e: media_previous())
    play_label.bind("<Button-1>", lambda e: media_play_pause())
    next_label.bind("<Button-1>", lambda e: media_next())
    speaker_label.bind("<Button-1>", lambda e: mute_speakers() if not is_speaker_muted() else unmute_speakers())
    
    # Keep references to prevent garbage collection
    prev_btn.image = prev_img
    play_btn.image = play_img
    next_btn.image = next_img
    speaker_btn.image = current_speaker_img
    
    # Store speaker controls for updating
    global speaker_button, speaker_label_ref
    speaker_button = speaker_btn
    speaker_label_ref = speaker_label
    
    # Pack buttons and labels in their frames
    prev_btn.pack(pady=(2, 0))
    prev_label.pack(pady=(0, 2))
    
    play_btn.pack(pady=(2, 0))
    play_label.pack(pady=(0, 2))
    
    next_btn.pack(pady=(2, 0))
    next_label.pack(pady=(0, 2))
    
    speaker_btn.pack(pady=(2, 0))
    speaker_label.pack(pady=(0, 2))
    
    # Pack control frames
    prev_control.pack(side=tk.LEFT, padx=10)
    play_control.pack(side=tk.LEFT, padx=10)
    next_control.pack(side=tk.LEFT, padx=10)
    speaker_control.pack(side=tk.LEFT, padx=10)
    
    return media_frame

# Modify create_top_controls to use global search_entry
def create_top_controls(parent):
    global search_entry  # Add this line
    
    top_frame = tk.Frame(parent, bg="#222222")
    
    # Create search controls (left side)
    search_frame = tk.Frame(top_frame, bg="#222222")
    search_frame.pack(side=tk.LEFT, padx=20)
    
    # Create and style the search entry
    search_entry = tk.Entry(search_frame, 
                          width=52,
                          font=("Arial", 12),
                          bg="lightgray",
                          fg="black",
                          insertbackground="black",
                          relief=tk.FLAT)
    search_entry.pack(side=tk.LEFT, padx=10, ipady=8)
    search_entry.bind("<Return>", on_enter)
    
    # Create search button with icon
    search_control = tk.Frame(search_frame, bg="#222222")
    search_control.pack(side=tk.LEFT, padx=5)
    
    search_img = tk.PhotoImage(file="assets/images/search.png").subsample(15, 15)
    search_btn = tk.Button(search_control, image=search_img, command=search_google,
                        bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    search_btn.image = search_img
    search_btn.pack(pady=(2, 0))
    
    search_label = tk.Label(search_control, text="Search", fg="lightgray",
                         bg="#222222", font=("Arial", 10), cursor="hand2")
    search_label.pack(pady=(0, 2))
    search_label.bind("<Button-1>", lambda e: search_google())
    
    # Create media controls (right side)
    media_frame = create_media_controls(top_frame)
    media_frame.pack(side=tk.LEFT, padx=20)
    
    return top_frame

# Create combined top controls (search + media)
top_controls = create_top_controls(button_frame)
top_controls.grid(row=0, column=0, columnspan=len(buttons)+1, pady=(5, 10))

# Create a frame for menu controls
def create_menu_controls(parent):
    menu_frame = tk.Frame(parent, bg="#222222")
    
    # Create individual frames for each control
    shutdown_control = tk.Frame(menu_frame, bg="#222222")
    restart_control = tk.Frame(menu_frame, bg="#222222")
    desktop_control = tk.Frame(menu_frame, bg="#222222")
    taskview_control = tk.Frame(menu_frame, bg="#222222")
    lock_control = tk.Frame(menu_frame, bg="#222222")
    
    # Load and resize menu control images
    shutdown_img = tk.PhotoImage(file="assets/images/shutdown.png").subsample(15, 15)
    restart_img = tk.PhotoImage(file="assets/images/restart.png").subsample(15, 15)
    desktop_img = tk.PhotoImage(file="assets/images/desktop.png").subsample(15, 15)
    taskview_img = tk.PhotoImage(file="assets/images/taskmenu3.png").subsample(15, 15)
    lock_img = tk.PhotoImage(file="assets/images/lockscreen.png").subsample(15, 15)
    
    # Create buttons with images
    shutdown_btn = tk.Button(shutdown_control, image=shutdown_img, command=shut_down,
                        bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    restart_btn = tk.Button(restart_control, image=restart_img, command=restart,
                        bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    desktop_btn = tk.Button(desktop_control, image=desktop_img, command=show_desktop,
                        bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    taskview_btn = tk.Button(taskview_control, image=taskview_img, command=task_view,
                        bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    lock_btn = tk.Button(lock_control, image=lock_img, command=lock_screen,
                        bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    
    # Create labels
    shutdown_label = tk.Label(shutdown_control, text="Shutdown", fg="lightgray",
                         bg="#222222", font=("Arial", 10), cursor="hand2")
    restart_label = tk.Label(restart_control, text="Restart", fg="lightgray",
                         bg="#222222", font=("Arial", 10), cursor="hand2")
    desktop_label = tk.Label(desktop_control, text="S/H Desktop", fg="lightgray",
                         bg="#222222", font=("Arial", 10), cursor="hand2")
    taskview_label = tk.Label(taskview_control, text="Task View", fg="lightgray",
                         bg="#222222", font=("Arial", 10), cursor="hand2")
    lock_label = tk.Label(lock_control, text="Lock Screen", fg="lightgray",
                         bg="#222222", font=("Arial", 10), cursor="hand2")
    
    # Bind labels to their respective commands
    shutdown_label.bind("<Button-1>", lambda e: shut_down())
    restart_label.bind("<Button-1>", lambda e: restart())
    desktop_label.bind("<Button-1>", lambda e: show_desktop())
    taskview_label.bind("<Button-1>", lambda e: task_view())
    lock_label.bind("<Button-1>", lambda e: lock_screen())
    
    # Keep references to prevent garbage collection
    shutdown_btn.image = shutdown_img
    restart_btn.image = restart_img
    desktop_btn.image = desktop_img
    taskview_btn.image = taskview_img
    lock_btn.image = lock_img
    
    # Pack buttons and labels in their frames
    shutdown_btn.pack(pady=(2, 0))
    shutdown_label.pack(pady=(0, 2))
    
    restart_btn.pack(pady=(2, 0))
    restart_label.pack(pady=(0, 2))
    
    desktop_btn.pack(pady=(2, 0))
    desktop_label.pack(pady=(0, 2))
    
    taskview_btn.pack(pady=(2, 0))
    taskview_label.pack(pady=(0, 2))
    
    lock_btn.pack(pady=(2, 0))
    lock_label.pack(pady=(0, 2))
    
    # Pack control frames
    shutdown_control.pack(side=tk.LEFT, padx=10)
    restart_control.pack(side=tk.LEFT, padx=10)
    lock_control.pack(side=tk.LEFT, padx=10)
    desktop_control.pack(side=tk.LEFT, padx=10)
    taskview_control.pack(side=tk.LEFT, padx=10)
    
    return menu_frame

# Create menu controls
menu_controls = create_menu_controls(button_frame)
menu_controls.grid(row=1, column=0, columnspan=len(buttons)+1, pady=5)

# Modify arrange_buttons function to handle menu controls
def arrange_buttons(event=None):
    # Handle all control frames
    top_controls.grid_forget()
    menu_controls.grid_forget()
    
    top_controls.grid(row=0, column=0, columnspan=len(button_widgets), pady=(5, 10))
    menu_controls.grid(row=1, column=0, columnspan=len(button_widgets), pady=5)
    
    # Then arrange other buttons starting from row 2
    for widget in button_frame.winfo_children():
        if widget not in (top_controls, menu_controls):
            widget.grid_forget()
    
    # Fixed button dimensions
    button_width = 210  # Width of button + padding
    min_spacing = 1    # Minimum spacing between buttons
    
    # Get available width
    available_width = max(800, root.winfo_width()) - 40
    
    # Calculate how many buttons can fit in a row
    buttons_per_row = max(1, min(len(button_widgets), (available_width + min_spacing) // (button_width + min_spacing)))
    
    # Calculate rows needed
    total_buttons = len(button_widgets)
    rows = (total_buttons + buttons_per_row - 1) // buttons_per_row
    
    # Calculate spacing to center buttons
    total_width = buttons_per_row * button_width
    spacing = max(min_spacing, (available_width - total_width) // (buttons_per_row + 1))
    
    # Place buttons in grid, starting from row 2 (after top and menu controls)
    for i, button in enumerate(button_widgets):
        row = (i // buttons_per_row) + 2  # Add 2 to start after top and menu controls
        col = i % buttons_per_row
        button.grid(row=row, 
                   column=col, 
                   padx=spacing,
                   pady=1)
        
        # Configure column weight for even spacing
        button_frame.grid_columnconfigure(col, weight=1)
    
    # Configure row weight for vertical centering
    for row in range(rows + 2):  # +2 for top and menu controls
        button_frame.grid_rowconfigure(row, weight=1)

    # Update frame size
    button_frame.update_idletasks()

def update_mute_button():
    is_muted = is_speaker_muted()
    if hasattr(speaker_button, 'image'):
        speaker_label_ref.config(text="Unmute" if is_muted else "Mute")
        speaker_button.config(
            command=unmute_speakers if is_muted else mute_speakers,
            image=speaker_mute_img if is_muted else speaker_unmute_img
        )
    root.after(1000, update_mute_button)

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
