# pages added in the menu main page & second page

import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
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
from datetime import datetime
from plyer import notification
from PIL import Image, ImageGrab, ImageTk
import pystray
import threading
import winreg
import logging
import json
import time
from tkcalendar import Calendar
import wmi
import requests
import io
import pyperclip
from pynput import keyboard

# Image paths
APP_NAME = "UpMenu"
ICON_PATHH = "assets/images/upmenu.ico"  # Ensure this is an ICO file
is_startup_enabled = True # Track the "Run on Startup" state
MENU_HEIGHT = 320
# Add this with other global declarations at the top
user_apps = {}  # Dictionary to store user's applications
# Add this global variable at the top with other globals
app_launcher_ref = None  # Reference to the app launcher frame
# Add this global variable at the top with other globals
update_app_buttons_ref = None  # Store reference to update function
# Add global variable for keyboard listener
keyboard_listener = None
default_shortcuts = {
    "Show/Hide Menu": "<ctrl>+<alt>+m",
    "Take Screenshot": "<ctrl>+<alt>+s",
    "Open Calculator": "<ctrl>+<alt>+c",
    "Open Homepage": "<ctrl>+<alt>+h"
}

# In global variables section, add:
current_page = 1  # Track current page
main_page_frame = None
second_page_frame = None

# Determine the application directory for logging error
# ----------------------------------------------------------------------------------
if getattr(sys, 'frozen', False):  # Check if the script is bundled
    app_dir = os.path.dirname(sys.executable)  # Directory of the .exe file
else:
    app_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the script
    
# Log file path in the application directory
LOG_FILE = os.path.join(app_dir, "upmenuerror.log")
# Ensure the log file exists or create it
if not os.path.exists(LOG_FILE):
    try:
        with open(LOG_FILE, 'w'):  # Create the file if it doesn't exist
            pass
    except Exception as e:
        print(f"Error creating log file: {e}")
        raise
# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
# Test logging
logging.info(f"\n\n\nApplication started successfully.")
print(f"Application started successfully.")
if(LOG_FILE):
    logging.info(f"Log file is at {LOG_FILE}")
    print(f"Log file is at {LOG_FILE}")
else:
    logging.info(f"Error creating log file")
    print(f"Error creating log file")


# Determine the application directory for images files
# ----------------------------------------------------------------------------------
if getattr(sys, 'frozen', False):  # Bundled as .exe
    app_dir = os.path.dirname(sys.executable)
else:  # Running as a script
    app_dir = os.path.dirname(os.path.abspath(__file__))

# Define the logs folder and log file path
# image_folders = os.path.join(app_dir, "image")
image_folders = os.path.join(app_dir, "assets\\image")
ICON_PATH = os.path.join(image_folders, "upmenu.ico")
# Ensure the logs folder exists
try:
    os.makedirs(image_folders, exist_ok=True)  # Create logs folder if it doesn't exist
    logging.info(f"icon is at {ICON_PATH}")
    print(f"icon is at {ICON_PATH}")
except Exception as e:
    logging.error(f"Error creating image folder: {e}")
    print(f"Error creating image folder: {e}")
    raise SystemExit(f"Error: Unable to create image folder. {e}")


# Determine the application directory for config file
# ----------------------------------------------------------------------------------
if getattr(sys, 'frozen', False):  # Bundled as .exe
    app_dir = os.path.dirname(sys.executable)
else:  # Running as a script
    app_dir = os.path.dirname(os.path.abspath(__file__))

# Define the logs folder and log file path
CONFIG_FILE = os.path.join(app_dir, "config.json")
# Ensure the logs folder exists
try:
    os.makedirs(app_dir, exist_ok=True)  # Create logs folder if it doesn't exist
    logging.info(f"configuration file is at {CONFIG_FILE}")
    print(f"configuration file is at {CONFIG_FILE}")
except Exception as e:
    logging.error(f"Error creating logs folder: {e}")
    print(f"Error creating logs folder: {e}")
    raise SystemExit(f"Error: Unable to create config file. {e}") 


# Notification function
# ----------------------------------------------------------------------------------
def show_notification(title, message):
    """
    Show a system notification.
    """
    try:
        notification.notify(
            title=title,
            message=message,
            app_name=APP_NAME,
            # app_icon=ICON_PATH,
            app_icon=ICON_PATHH if os.path.exists(ICON_PATHH) else None,
            timeout=3
        )
    except Exception as e:
        print.error(f"Notification Error: {e}")


# Default configuration
# ----------------------------------------------------------------------------------
DEFAULT_CONFIG = {
    "startup_enable": True,
    "apps": {
        "Notepad": "notepad.exe",
        "Explorer": "explorer.exe"
    }
}


# save configuration & restore 
# ----------------------------------------------------------------------------------
# Load configuration from JSON file
def load_config():
    global is_startup_enabled, user_apps
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                is_startup_enabled = config.get("startup_enable", DEFAULT_CONFIG["startup_enable"])
                user_apps = config.get("apps", {})
                if not user_apps:
                    user_apps = DEFAULT_CONFIG["apps"].copy()
            
            logging.info(f"Configuration loaded successfully. Apps: {user_apps}")
            # print(f"Configuration loaded successfully. Apps: {user_apps}")
            
            # Update app buttons if the update function exists
            if update_app_buttons_ref:
                update_app_buttons_ref()
        else:
            # If config file doesn't exist, use defaults
            is_startup_enabled = DEFAULT_CONFIG["startup_enable"]
            user_apps = DEFAULT_CONFIG["apps"].copy()
            save_config()
            logging.info("Created new config file with defaults")
            print("Created new config file with defaults")
            
    except Exception as e:
        logging.error(f"Error load_config: {e}")
        print(f"Error load_config: {e}")
        user_apps = DEFAULT_CONFIG["apps"].copy()

    try:
        # Only try to synchronize startup state if the function exists
        if 'synchronize_startup_state' in globals():
            synchronize_startup_state()
    except Exception as e:
        logging.error(f"Error synchronizing startup state: {e}")
        print(f"Error synchronizing startup state: {e}")


# Save configuration to JSON file
# ----------------------------------------------------------------------------------
def save_config():
    global is_startup_enabled, user_apps
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        config = {
            "startup_enable": is_startup_enabled,
            "apps": user_apps
        }
        
        with open(CONFIG_FILE, "w") as file:
            json.dump(config, file, indent=4)
        logging.info(f"Configuration saved successfully. Apps: {user_apps}")
        print(f"Configuration saved successfully. Apps: {user_apps}")
    except Exception as e:
        logging.error(f"Error save_config: {e}")
        print(f"Error saving config: {e}")
# Add this debug print after loading config
print(f"Current user_apps after loading: {user_apps}")


# Restore the default configuration
# ----------------------------------------------------------------------------------
def restore_defaults(icon, item=None):
    try:
        global is_startup_enabled
        is_startup_enabled = DEFAULT_CONFIG["startup_enable"]
        save_config()  # Save the restored defaults to the config file
            
        show_notification(APP_NAME, f"Default settings have been restored.")
        logging.info("Configuration restored to default.")
        print("Configuration restored to default.")
    except Exception as e:
        logging.error(f"Error restoring defaults: {e}")
        print(f"Error restoring defaults: {e}")
        show_notification(APP_NAME, "Failed to restore default configuration.")
    load_config()  # Load the interval from JSON file
        

# ----------------------------------------------------------------------------------
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

# Add these global variables at the top with other globals
images = {}  # Dictionary to store all images

# Add this function after global declarations and before any other functions
def load_all_images():
    """Preload all images used in the application"""
    global images
    
    # List of all images and their subsample factors
    image_configs = {
        'search': ('assets/images/search.png', 15),
        'backward': ('assets/images/backward.png', 15),
        'playpause': ('assets/images/playpause.png', 15),
        'forward': ('assets/images/forward.png', 15),
        'volumemute': ('assets/images/volumemute.png', 15),
        'volumeup': ('assets/images/volumeup.png', 15),
        'shutdown': ('assets/images/shutdown.png', 15),
        'restart': ('assets/images/restart.png', 15),
        'desktop': ('assets/images/desktop.png', 15),
        'taskmenu': ('assets/images/taskmenu3.png', 15),
        'lock': ('assets/images/lockscreen.png', 15),
        'screenshot': ('assets/images/screenshot1.png', 15),
        'brightness0': ('assets/images/brightness0.png', 15),
        'brightness25': ('assets/images/brightness25.png', 15),
        'brightness50': ('assets/images/brightness50.png', 15),
        'brightness75': ('assets/images/brightness75.png', 15),
        'brightness100': ('assets/images/brightness100.png', 15),
        'homepage': ('assets/images/homepage.png', 15),
        'calculator': ('assets/images/calculator.png', 15),
        'leftarrow': ('assets/images/leftarrow.png', 15),  # Add this line
        'rightarrow': ('assets/images/rightarrow.png', 15),  # Add this line
    }
    
    # Load each image
    for name, (path, subsample) in image_configs.items():
        try:
            images[name] = tk.PhotoImage(file=path).subsample(subsample, subsample)
        except Exception as e:
            print(f"Error loading image {path}: {e}")

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
    except Exception as e:
        print(f"Error muting speakers: {e}")

def unmute_speakers():
    try:
        controller = AudioController()
        controller.volume.SetMute(0, None)
        print("Speakers unmuted.")
    except Exception as e:
        print(f"Error unmuting speakers: {e}")

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
    show_notification(APP_NAME, "Keylogger is terminated...")
    logging.info(f"Script terminated\n\n")
    print("Stopping script...\n\n\n")
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
    
# take screenshot
def take_screenshot():
    import datetime
    try:
        time.sleep(1)
        # Capture screenshot
        screenshot = ImageGrab.grab()

        # Generate filename based on current time
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{current_time}_bibek.png"

        # Get the Downloads folder path
        downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')

        # Save screenshot to the Downloads folder
        file_path = os.path.join(downloads_folder, file_name)
        screenshot.save(file_path)
        # Screenshot saved successfully message
        # messagebox.showinfo("Success", f"Screenshot saved to {file_path}")
        # Prompt user to open screenshot folder
        if messagebox.askyesno("Success", f"Screenshot saved to {file_path}. Open folder?"):
            os.startfile(downloads_folder)
        # Open screenshot folder
        # os.startfile(downloads_folder)

    except Exception as e:
        messagebox.showerror("Error", f"Error while taking screenshot: {e}")
        logging.error(f"Error performing screenshot: {e}")

# homepage
def open_homepage():
    webbrowser.open("https://bibekchandsah.github.io/Homepage")

# open calculator
def open_calculator():
    os.system("calc.exe")



# Move this section up, right after creating the root window and before any controls
root = tk.Tk()
root.title("Rounded Rectangular Menu")
root.overrideredirect(True)  # Remove window decorations
root.attributes("-topmost", True)  # Keep window always on top
root.attributes("-transparentcolor", "white")
root.configure(bg="white", highlightthickness=0)

# Load configuration first
load_config()  # Add this line to load saved apps

# Load images 
load_all_images()



# Add this function before creating the canvas
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

# Now create the canvas and continue with the rest of the code
canvas = tk.Canvas(root, width=900, height=MENU_HEIGHT, bg="white", highlightthickness=0)
canvas.pack(pady=0)

radius = 25

# Draw shadow (slightly larger, offset, and semi-transparent dark color)
shadow_color = "#0a0a0a"  # Very dark color for shadow
shadow_offset = 5  # Increased offset for more visible shadow
canvas.create_rounded_rect(
    shadow_offset, shadow_offset,  # Offset x, y
    900, MENU_HEIGHT,  # Original width and height
    radius,
    fill=shadow_color,
    outline=""
)

# Draw the outer border (dark border)
canvas.create_rounded_rect(0, 0, 900, 300, radius, fill="#1a1a1a", outline="")

# Draw the inner background
canvas.create_rounded_rect(1, 1, 900, 300, radius, fill="#222222", outline="")

# Create main container frame
main_container = tk.Frame(canvas, bg="#222222")
main_container.place(relx=0.5, rely=0, anchor="n", width=900, height=MENU_HEIGHT-50)

# Create page frames
main_page_frame = tk.Frame(main_container, bg="#222222")
second_page_frame = tk.Frame(main_container, bg="#222222")

# Move existing main page content to main_page_frame
# Original code for creating controls should be nested under main_page_frame
# Example changes:

# Original:
# red_area_frame = tk.Frame(main_container, bg="#222222", height=40)
# red_area_frame.pack(fill=tk.X, pady=(10, 5))

# Change to:
red_area_frame = tk.Frame(main_page_frame, bg="#222222", height=40)
red_area_frame.pack(fill=tk.X, pady=(10, 5))

# Similarly for other components on main page

# Move this function BEFORE the create_second_page function
def create_system_monitor(parent):
    """Create a system resource monitor widget"""
    monitor_frame = tk.Frame(parent, bg="#222222")
    
    cpu_label = tk.Label(monitor_frame, text="CPU: 0%", fg="lightgray",
                        bg="#222222", font=("Arial", 10))
    cpu_label.pack(anchor="w")
    
    ram_label = tk.Label(monitor_frame, text="RAM: 0%", fg="lightgray",
                        bg="#222222", font=("Arial", 10))
    ram_label.pack(anchor="w")
    
    def update_system_stats():
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            cpu_label.config(text=f"CPU: {cpu_percent}%")
            
            # RAM usage
            ram = psutil.virtual_memory()
            ram_percent = ram.percent
            ram_label.config(text=f"RAM: {ram_percent}%")
            
            for label, value in [(cpu_label, cpu_percent), 
                                (ram_label, ram_percent)]:
                if value > 90:
                    label.config(fg="red")
                elif value > 70:
                    label.config(fg="orange")
                else:
                    label.config(fg="lightgray")
                    
        except Exception as e:
            logging.error(f"System monitor error: {e}")
        
        monitor_frame.after(2000, update_system_stats)
    
    update_system_stats()
    return monitor_frame

# Move this BEFORE create_second_page function
def create_shortcuts_manager(parent):
    """Create a keyboard shortcuts manager"""
    shortcuts_frame = tk.Frame(parent, bg="#222222")
    
    def open_shortcuts_manager():
        manager_window = tk.Toplevel(root)
        manager_window.title("Keyboard Shortcuts")
        manager_window.geometry("400x300")
        manager_window.configure(bg="#222222")
        
        # Create listbox for shortcuts
        listbox_frame = tk.Frame(manager_window, bg="#222222")
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create two columns: Action and Shortcut
        action_list = tk.Listbox(listbox_frame, bg="#333333", fg="white",
                               font=("Arial", 11), selectbackground="#555555",
                               width=25)
        action_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        shortcut_list = tk.Listbox(listbox_frame, bg="#333333", fg="white",
                                 font=("Arial", 11), selectbackground="#555555",
                                 width=15)
        shortcut_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Synchronize scrolling between lists
        def on_scroll(*args):
            action_list.yview_moveto(args[0])
            shortcut_list.yview_moveto(args[0])
        
        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL,
                               command=on_scroll)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        action_list.config(yscrollcommand=scrollbar.set)
        shortcut_list.config(yscrollcommand=scrollbar.set)
        
        # Add shortcuts to lists
        for action, shortcut in shortcuts.items():
            action_list.insert(tk.END, action)
            shortcut_list.insert(tk.END, shortcut)
        
        def edit_shortcut():
            selection = action_list.curselection()
            if not selection:
                return
                
            action = action_list.get(selection[0])
            old_shortcut = shortcuts[action]
            
            # Create edit dialog
            edit_window = tk.Toplevel(manager_window)
            edit_window.title("Edit Shortcut")
            edit_window.geometry("300x150")
            edit_window.configure(bg="#222222")
            
            tk.Label(edit_window, text=f"Action: {action}",
                    bg="#222222", fg="white").pack(pady=10)
            
            shortcut_var = tk.StringVar(value=old_shortcut)
            shortcut_entry = tk.Entry(edit_window, textvariable=shortcut_var,
                                    bg="#333333", fg="white", width=20)
            shortcut_entry.pack(pady=5)
            
            def on_key(event):
                key_name = event.keysym
                if key_name in ['Control_L', 'Control_R', 'Alt_L', 'Alt_R', 'Shift_L', 'Shift_R']:
                    return
                
                modifiers = []
                if event.state & 0x4:
                    modifiers.append("ctrl")
                if event.state & 0x8:
                    modifiers.append("alt")
                if event.state & 0x1:
                    modifiers.append("shift")
                
                shortcut = "+".join(modifiers + [key_name.lower()])
                shortcut_var.set(f"<{shortcut}>")
                return "break"
            
            shortcut_entry.bind("<Key>", on_key)
            
            def save_edit():
                new_shortcut = shortcut_var.set()
                shortcuts[action] = new_shortcut
                # save_shortcuts()
                shortcut_list.delete(selection[0])
                shortcut_list.insert(selection[0], new_shortcut)
                edit_window.destroy()
                setup_keyboard_shortcuts()  # Refresh keyboard listeners
            
            def cancel_edit():
                edit_window.destroy()
            
            btn_frame = tk.Frame(edit_window, bg="#222222")
            btn_frame.pack(pady=20)
            
            tk.Button(btn_frame, text="Save", command=save_edit,
                     bg="#444444", fg="white").pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Cancel", command=cancel_edit,
                     bg="#444444", fg="white").pack(side=tk.LEFT, padx=5)
        
        def reset_shortcuts():
            if messagebox.askyesno("Reset Shortcuts", 
                                 "Reset all shortcuts to default values?"):
                global shortcuts
                shortcuts = default_shortcuts.copy()
                # save_shortcuts()
                
                # Update lists
                action_list.delete(0, tk.END)
                shortcut_list.delete(0, tk.END)
                for action, shortcut in shortcuts.items():
                    action_list.insert(tk.END, action)
                    shortcut_list.insert(tk.END, shortcut)
                
                setup_keyboard_shortcuts()  # Refresh keyboard listeners
        
        # Control buttons
        control_frame = tk.Frame(manager_window, bg="#222222")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        edit_btn = tk.Button(control_frame, text="Edit", command=edit_shortcut,
                           bg="#444444", fg="white", width=8)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = tk.Button(control_frame, text="Reset", command=reset_shortcuts,
                            bg="#444444", fg="white", width=8)
        reset_btn.pack(side=tk.LEFT, padx=5)
    
    shortcuts_btn = tk.Button(shortcuts_frame, text="Shortcuts",
                            command=open_shortcuts_manager,
                            bg="#333333", fg="#d2d2d2",
                            activebackground="#444444")
    shortcuts_btn.pack()
    
    return shortcuts_frame

# Then keep create_timer_widget and create_bookmarks_widget definitions
def create_timer_widget(parent):
    """Create a timer and stopwatch widget"""
    timer_frame = tk.Frame(parent, bg="#222222")
    
    timer_btn = tk.Button(timer_frame, text="Timer", 
                        bg="#333333", fg="#d2d2d2", activebackground="#444444")
    timer_btn.pack(side=tk.LEFT, padx=5)
    
    stopwatch_btn = tk.Button(timer_frame, text="Stopwatch", 
                            bg="#333333", fg="#d2d2d2", activebackground="#444444")
    stopwatch_btn.pack(side=tk.LEFT, padx=5)
    
    # Timer functionality
    def open_timer():
        timer_window = tk.Toplevel(root)
        timer_window.title("Timer")
        timer_window.geometry("300x200")
        timer_window.configure(bg="#222222")
        
        # Time entry frame
        entry_frame = tk.Frame(timer_window, bg="#222222")
        entry_frame.pack(pady=10)
        
        # Minutes and seconds entries
        tk.Label(entry_frame, text="Min:", bg="#222222", fg="white").pack(side=tk.LEFT)
        min_entry = tk.Entry(entry_frame, width=3, bg="#333333", fg="white")
        min_entry.pack(side=tk.LEFT, padx=5)
        min_entry.insert(0, "5")  # Default 5 minutes
        
        tk.Label(entry_frame, text="Sec:", bg="#222222", fg="white").pack(side=tk.LEFT)
        sec_entry = tk.Entry(entry_frame, width=3, bg="#333333", fg="white")
        sec_entry.pack(side=tk.LEFT, padx=5)
        sec_entry.insert(0, "0")  # Default 0 seconds
        
        # Timer display
        time_display = tk.Label(timer_window, text="05:00", font=("Arial", 24),
                              bg="#222222", fg="white")
        time_display.pack(pady=10)
        
        # Timer variables
        timer_running = False
        timer_id = None
        remaining_seconds = 0
        
        def start_timer():
            nonlocal timer_running, timer_id, remaining_seconds
            
            if not timer_running:
                # Get time from entries
                try:
                    mins = int(min_entry.get())
                    secs = int(sec_entry.get())
                    remaining_seconds = mins * 60 + secs
                except ValueError:
                    show_notification(APP_NAME, "Please enter valid numbers")
                    return
                
                timer_running = True
                start_btn.config(text="Pause")
                
                update_timer()
        
        def update_timer():
            nonlocal timer_running, timer_id, remaining_seconds
            
            if timer_running and remaining_seconds > 0:
                # Update display
                mins, secs = divmod(remaining_seconds, 60)
                time_display.config(text=f"{mins:02d}:{secs:02d}")
                
                remaining_seconds -= 1
                timer_id = timer_window.after(1000, update_timer)
            elif timer_running and remaining_seconds <= 0:
                time_display.config(text="00:00")
                timer_running = False
                start_btn.config(text="Start")
                show_notification(APP_NAME, "Timer finished!")
        
        def pause_timer():
            nonlocal timer_running, timer_id
            
            if timer_running:
                timer_window.after_cancel(timer_id)
                timer_running = False
                start_btn.config(text="Resume")
            else:
                timer_running = True
                start_btn.config(text="Pause")
                update_timer()
        
        def reset_timer():
            nonlocal timer_running, timer_id, remaining_seconds
            
            if timer_running:
                timer_window.after_cancel(timer_id)
                timer_running = False
            
            # Reset to initial values
            try:
                mins = int(min_entry.get())
                secs = int(sec_entry.get())
                remaining_seconds = mins * 60 + secs
            except ValueError:
                remaining_seconds = 300  # Default 5 minutes
            
            time_display.config(text=f"{remaining_seconds//60:02d}:{remaining_seconds%60:02d}")
            start_btn.config(text="Start")
        
        # Control buttons
        control_frame = tk.Frame(timer_window, bg="#222222")
        control_frame.pack(pady=10)
        
        start_btn = tk.Button(control_frame, text="Start", 
                            command=lambda: start_timer() if not timer_running else pause_timer(),
                            bg="#444444", fg="white", width=8)
        start_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = tk.Button(control_frame, text="Reset", command=reset_timer,
                            bg="#444444", fg="white", width=8)
        reset_btn.pack(side=tk.LEFT, padx=5)
    
    # Stopwatch functionality
    def open_stopwatch():
        stopwatch_window = tk.Toplevel(root)
        stopwatch_window.title("Stopwatch")
        stopwatch_window.geometry("300x200")
        stopwatch_window.configure(bg="#222222")
        
        # Stopwatch display
        time_display = tk.Label(stopwatch_window, text="00:00.0", font=("Arial", 24),
                              bg="#222222", fg="white")
        time_display.pack(pady=20)
        
        # Stopwatch variables
        running = False
        start_time = 0
        elapsed = 0
        update_id = None
        
        def start_stopwatch():
            nonlocal running, start_time, update_id
            
            if not running:
                running = True
                start_time = time.time() - elapsed
                start_btn.config(text="Pause")
                update_stopwatch()
        
        def update_stopwatch():
            nonlocal running, update_id
            
            if running:
                current_time = time.time()
                elapsed_seconds = current_time - start_time
                
                # Format time as MM:SS.d
                minutes = int(elapsed_seconds // 60)
                seconds = int(elapsed_seconds % 60)
                deciseconds = int((elapsed_seconds * 10) % 10)
                
                time_display.config(text=f"{minutes:02d}:{seconds:02d}.{deciseconds}")
                
                update_id = stopwatch_window.after(100, update_stopwatch)
        
        def pause_stopwatch():
            nonlocal running, elapsed, update_id
            
            if running:
                stopwatch_window.after_cancel(update_id)
                running = False
                elapsed = time.time() - start_time
                start_btn.config(text="Resume")
        
        def reset_stopwatch():
            nonlocal running, elapsed, update_id
            
            if running:
                stopwatch_window.after_cancel(update_id)
                running = False
            
            elapsed = 0
            time_display.config(text="00:00.0")
            start_btn.config(text="Start")
        
        # Control buttons
        control_frame = tk.Frame(stopwatch_window, bg="#222222")
        control_frame.pack(pady=10)
        
        start_btn = tk.Button(control_frame, text="Start", 
                            command=lambda: start_stopwatch() if not running else pause_stopwatch(),
                            bg="#444444", fg="white", width=8)
        start_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = tk.Button(control_frame, text="Reset", command=reset_stopwatch,
                            bg="#444444", fg="white", width=8)
        reset_btn.pack(side=tk.LEFT, padx=5)
    
    # Connect buttons to their functions
    timer_btn.config(command=open_timer)
    stopwatch_btn.config(command=open_stopwatch)
    
    return timer_frame

def create_bookmarks_widget(parent):
    """Create a quick web bookmarks widget"""
    bookmarks_frame = tk.Frame(parent, bg="#222222")
    
    # Default bookmarks
    default_bookmarks = {
        "Google": "https://www.google.com",
        "YouTube": "https://www.youtube.com",
        "GitHub": "https://github.com",
        "Gmail": "https://mail.google.com"
    }
    
    # Load saved bookmarks
    bookmarks_file = os.path.join(app_dir, "bookmarks.json")
    bookmarks = default_bookmarks.copy()
    
    if os.path.exists(bookmarks_file):
        try:
            with open(bookmarks_file, "r") as f:
                saved_bookmarks = json.load(f)
                bookmarks.update(saved_bookmarks)
        except Exception as e:
            logging.error(f"Error loading bookmarks: {e}")
    
    def save_bookmarks():
        try:
            with open(bookmarks_file, "w") as f:
                json.dump(bookmarks, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving bookmarks: {e}")
    
    def open_bookmark_manager():
        manager_window = tk.Toplevel(root)
        manager_window.title("Bookmark Manager")
        manager_window.geometry("400x300")
        manager_window.configure(bg="#222222")
        
        # Create listbox for bookmarks
        listbox_frame = tk.Frame(manager_window, bg="#222222")
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        listbox = tk.Listbox(listbox_frame, bg="#333333", fg="white", 
                           font=("Arial", 11), selectbackground="#555555")
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)
        
        # Add bookmarks to listbox
        for name in bookmarks:
            listbox.insert(tk.END, name)
        
        # Control buttons frame
        control_frame = tk.Frame(manager_window, bg="#222222")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Function to add a new bookmark
        def add_bookmark():
            name = simpledialog.askstring("Add Bookmark", "Enter bookmark name:")
            if name and name not in bookmarks:
                url = simpledialog.askstring("Add Bookmark", "Enter URL:")
                if url:
                    bookmarks[name] = url
                    listbox.insert(tk.END, name)
                    save_bookmarks()
                    update_bookmark_buttons()
        
        # Function to edit selected bookmark
        def edit_bookmark():
            selected_idx = listbox.curselection()
            if selected_idx:
                old_name = listbox.get(selected_idx[0])
                new_name = simpledialog.askstring("Edit Bookmark", "Enter new name:", initialvalue=old_name)
                if new_name:
                    new_url = simpledialog.askstring("Edit Bookmark", "Enter new URL:", 
                                                  initialvalue=bookmarks[old_name])
                    if new_url:
                        # Remove old bookmark
                        del bookmarks[old_name]
                        # Add new bookmark
                        bookmarks[new_name] = new_url
                        # Update listbox
                        listbox.delete(selected_idx[0])
                        listbox.insert(selected_idx[0], new_name)
                        save_bookmarks()
                        update_bookmark_buttons()
        
        # Function to delete selected bookmark
        def delete_bookmark():
            selected_idx = listbox.curselection()
            if selected_idx:
                name = listbox.get(selected_idx[0])
                if messagebox.askyesno("Delete Bookmark", f"Delete '{name}'?"):
                    del bookmarks[name]
                    listbox.delete(selected_idx[0])
                    save_bookmarks()
                    update_bookmark_buttons()
        
        # Add control buttons
        add_btn = tk.Button(control_frame, text="Add", command=add_bookmark,
                          bg="#444444", fg="white", width=8)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        edit_btn = tk.Button(control_frame, text="Edit", command=edit_bookmark,
                           bg="#444444", fg="white", width=8)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(control_frame, text="Delete", command=delete_bookmark,
                             bg="#444444", fg="white", width=8)
        delete_btn.pack(side=tk.LEFT, padx=5)
    
    # Create bookmark buttons
    bookmark_buttons_frame = tk.Frame(bookmarks_frame, bg="#222222")
    bookmark_buttons_frame.pack()
    
    def update_bookmark_buttons():
        # Clear existing buttons
        for widget in bookmark_buttons_frame.winfo_children():
            widget.destroy()
        
        # Create buttons for first 4 bookmarks
        count = 0
        for name, url in bookmarks.items():
            if count < 4:  # Limit to 4 buttons
                btn = tk.Button(bookmark_buttons_frame, text=name,
                              command=lambda u=url: webbrowser.open(u),
                              bg="#333333", fg="#d2d2d2", 
                              activebackground="#444444",
                              width=8)
                btn.pack(side=tk.LEFT, padx=2)
                count += 1
            else:
                break
        
        # Add "More" button to open manager
        more_btn = tk.Button(bookmark_buttons_frame, text="More...",
                           command=open_bookmark_manager,
                           bg="#333333", fg="#d2d2d2", 
                           activebackground="#444444",
                           width=6)
        more_btn.pack(side=tk.LEFT, padx=2)
    
    # Initialize bookmark buttons
    update_bookmark_buttons()
    
    return bookmarks_frame

# Then keep create_second_page function
def create_second_page(parent):
    second_page = tk.Frame(parent, bg="#222222")
    
    # System Monitor
    system_monitor = create_system_monitor(second_page)
    system_monitor.pack(pady=10)
    
    # Shortcuts Manager
    shortcuts_widget = create_shortcuts_manager(second_page)
    shortcuts_widget.pack(pady=10)
    
    # Timer/Stopwatch
    timer_widget = create_timer_widget(second_page)
    timer_widget.pack(pady=10)
    
    # Bookmarks
    bookmarks_widget = create_bookmarks_widget(second_page)
    bookmarks_widget.pack(pady=10)
    
    return second_page

# Initialize pages
main_page_frame.pack()  # Show main page by default
second_page_frame = create_second_page(main_container)
second_page_frame.pack_forget()  # Hide second page initially

# Add this before the volume frame creation
# Create a horizontal line
separator_canvas = tk.Canvas(canvas, height=2, bg="#222222", highlightthickness=0)
separator_canvas.place(relx=0, rely=0.80, relwidth=1.0)  # Place it above the controls
separator_canvas.create_line(0, 1, 900, 1, fill="#d2d2d2", width=1)  # Red line


def create_volume_slider(parent):
    """Create a volume slider control"""
    volume_frame = tk.Frame(parent, bg="#222222")
    
    # Add volume label
    volume_label = tk.Label(volume_frame, text="Volume", fg="lightgray",
                          bg="#222222", font=("Arial", 10))
    volume_label.pack(side=tk.LEFT, padx=(0, 10))
    
    def on_volume_change(val):
        try:
            controller = AudioController()
            controller.volume.SetMasterVolumeLevelScalar(float(val)/100, None)
            # Update value label
            value_label.config(text=f"{int(float(val))}%")
        except Exception as e:
            print(f"Error setting volume: {e}")
    
    def on_mousewheel(event):
        # Change by 5% for each wheel tick
        delta = 5 if event.delta > 0 else -5
        new_value = min(100, max(0, volume_slider.get() + delta))
        volume_slider.set(new_value)
        on_volume_change(new_value)
    
    # Create slider with current volume
    try:
        controller = AudioController()
        current_volume = int(controller.volume.GetMasterVolumeLevelScalar() * 100)
    except:
        current_volume = 50
    
    volume_slider = tk.Scale(volume_frame, from_=0, to=100,
                           orient=tk.HORIZONTAL, length=150,
                           bg="#222222", fg="lightgray",
                           highlightthickness=0, troughcolor="#444444",
                           activebackground="#666666",
                           command=on_volume_change)
    volume_slider.set(current_volume)
    volume_slider.pack(side=tk.LEFT)
    
    # Bind mousewheel to slider and frame
    volume_slider.bind("<MouseWheel>", on_mousewheel)
    volume_frame.bind("<MouseWheel>", on_mousewheel)
    volume_label.bind("<MouseWheel>", on_mousewheel)
    
    # Add value label
    value_label = tk.Label(volume_frame, text=f"{current_volume}%",
                        fg="lightgray", bg="#222222", font=("Arial", 10))
    value_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def update_volume_display():
        try:
            controller = AudioController()
            current_vol = int(controller.volume.GetMasterVolumeLevelScalar() * 100)
            # Only update if value is different to avoid visual feedback loop
            if int(volume_slider.get()) != current_vol:
                volume_slider.set(current_vol)
                value_label.config(text=f"{current_vol}%")
        except Exception as e:
            print(f"Error updating volume display: {e}")
        volume_frame.after(100, update_volume_display)  # Check every 100ms
    
    # Start the update loop
    update_volume_display()
    value_label.bind("<MouseWheel>", on_mousewheel)
    
    return volume_frame

# Add these functions before the create_brightness_slider function
def get_brightness():
    try:
        c = wmi.WMI(namespace='wmi')
        monitors = c.WmiMonitorBrightness()
        return monitors[0].CurrentBrightness
    except Exception as e:
        print(f"Error getting brightness: {e}")
        return 50

def set_brightness(value):
    try:
        c = wmi.WMI(namespace='wmi')
        monitors = c.WmiMonitorBrightnessMethods()
        monitors[0].WmiSetBrightness(value, 0)
        return True
    except Exception as e:
        print(f"Error setting brightness: {e}")
        return False

def create_brightness_slider(parent):
    """Create a brightness slider control"""
    brightness_frame = tk.Frame(parent, bg="#222222")
    
    # Add brightness label
    brightness_label = tk.Label(brightness_frame, text="Brightness", fg="lightgray",
                            bg="#222222", font=("Arial", 10))
    brightness_label.pack(side=tk.LEFT, padx=(10, 0))  # Added left padding
    
    def on_brightness_change(val):
        try:
            set_brightness(int(float(val)))
            # Update value label
            value_label.config(text=f"{int(float(val))}%")
        except Exception as e:
            print(f"Error setting brightness: {e}")
    
    def on_mousewheel(event):
        # Change by 5% for each wheel tick
        delta = 5 if event.delta > 0 else -5
        new_value = min(100, max(0, brightness_slider.get() + delta))
        brightness_slider.set(new_value)
        on_brightness_change(new_value)
    
    # Create slider with current brightness
    try:
        current_brightness = get_brightness()
    except:
        current_brightness = 50
    
    brightness_slider = tk.Scale(brightness_frame, from_=0, to=100,
                             orient=tk.HORIZONTAL, length=150,
                             bg="#222222", fg="lightgray",
                             highlightthickness=0, troughcolor="#444444",
                             activebackground="#666666",
                             command=on_brightness_change)
    brightness_slider.set(current_brightness)
    brightness_slider.pack(side=tk.LEFT)
    
    # Bind mousewheel to slider and frame
    brightness_slider.bind("<MouseWheel>", on_mousewheel)
    brightness_frame.bind("<MouseWheel>", on_mousewheel)
    brightness_label.bind("<MouseWheel>", on_mousewheel)
    
    # Add value label
    value_label = tk.Label(brightness_frame, text=f"{current_brightness}%",
                        fg="lightgray", bg="#222222", font=("Arial", 10))
    value_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def update_brightness_display():
        try:
            current_bright = get_brightness()
            # Only update if value is different to avoid visual feedback loop
            if int(brightness_slider.get()) != current_bright:
                brightness_slider.set(current_bright)
                value_label.config(text=f"{current_bright}%")
        except Exception as e:
            print(f"Error updating brightness display: {e}")
        brightness_frame.after(100, update_brightness_display)
    
    # Start the update loop
    update_brightness_display()
    value_label.bind("<MouseWheel>", on_mousewheel)
    
    return brightness_frame

# Then continue with the volume frame and other controls
volume_frame = tk.Frame(canvas, bg="#222222")
volume_frame.place(relx=0.01, rely=0.95, anchor="sw")  # Adjust position

volume_widget = create_volume_slider(volume_frame)
volume_widget.pack(side=tk.LEFT)

brightness_widget = create_brightness_slider(volume_frame)
brightness_widget.pack(side=tk.LEFT)


# Add this function to calculate network speed
def get_network_speed():
    # Get initial bytes
    bytes_before = psutil.net_io_counters()
    time.sleep(1)  # Wait for 1 second
    # Get bytes after 1 second
    bytes_after = psutil.net_io_counters()
    
    # Calculate speeds
    download = bytes_after.bytes_recv - bytes_before.bytes_recv
    upload = bytes_after.bytes_sent - bytes_before.bytes_sent
    
    # Convert to appropriate units
    def format_speed(bytes_per_sec):
        if bytes_per_sec >= 1024*1024*1024:  # GB range
            return f"{bytes_per_sec/(1024*1024*1024):.2f} GB/s"
        elif bytes_per_sec >= 1024*1024:  # MB range
            return f"{bytes_per_sec/(1024*1024):.2f} MB/s"
        elif bytes_per_sec >= 1024:  # KB range
            return f"{bytes_per_sec/1024:.2f} KB/s"
        else:  # Bytes
            return f"{bytes_per_sec:.2f} B/s"
    
    return format_speed(download), format_speed(upload)

# Add this before creating the datetime widget
# Create network speed display
network_frame = tk.Frame(canvas, bg="#222222")
network_frame.place(relx=0.69, rely=0.98, anchor="se")  # Place before datetime

download_label = tk.Label(network_frame, text="D: 0 B/s", fg="#d2d2d2",
                         bg="#222222", font=("Arial", 10))
download_label.pack(anchor="e")

upload_label = tk.Label(network_frame, text="U: 0 B/s", fg="#d2d2d2",
                       bg="#222222", font=("Arial", 10))
upload_label.pack(anchor="e")

# Update network speed display
def update_network_speed():
    download_speed, upload_speed = get_network_speed()
    download_label.config(text=f"D: {download_speed}")
    upload_label.config(text=f"U: {upload_speed}")
    network_frame.after(1000, update_network_speed)  # Update every second

# Start updating network speed
update_network_speed()


def create_datetime_widget(parent):
    """Create a date and time display with clickable calendar"""
    datetime_frame = tk.Frame(parent, bg="#222222")
    
    # Create single label for both date and time
    datetime_label = tk.Label(datetime_frame, fg="lightgray",
                            bg="#222222", font=("Arial", 12),
                            cursor="hand2")
    datetime_label.pack()
    
    def update_time():
        now = datetime.now()
        datetime_str = now.strftime("%I:%M:%S %p  %Y-%m-%d")
        datetime_label.config(text=datetime_str)
        datetime_frame.after(1000, update_time)
    
    def show_calendar(event):
        # Create a new toplevel window
        cal_window = tk.Toplevel(root)
        cal_window.title("Calendar")
        cal_window.overrideredirect(True)  # Remove window decorations
        
        # Calculate position to show below the datetime label
        x = datetime_label.winfo_rootx() - 150  # Center horizontally with the date
        y = datetime_label.winfo_rooty() + datetime_label.winfo_height() + 5  # Position below with 5px gap
        
        # Ensure calendar stays within screen bounds
        screen_height = root.winfo_screenheight()
        if y + 250 > screen_height:  # If calendar would go off screen bottom
            y = datetime_label.winfo_rooty() - 250 - 5  # Show above instead
        
        cal_window.geometry(f"300x250+{x}+{y}")
        cal_window.configure(bg="#222222")
        
        # Keep calendar window on top
        cal_window.attributes('-topmost', True)
        
        # Create calendar widget with styling
        cal = Calendar(cal_window, 
                      selectmode='day',
                      year=datetime.now().year,
                      month=datetime.now().month,
                      day=datetime.now().day,
                      firstweekday='sunday',  # Set Sunday as first day
                      showweeknumbers=False,  # Remove week numbers
                      background="#222222",
                      foreground="white",
                      bordercolor="#222222",
                      headersbackground="#333333",
                      headersforeground="white",
                      selectbackground="#444444",
                      selectforeground="white",
                      normalbackground="#222222",
                      normalforeground="white",
                      weekendbackground="#222222",
                      weekendforeground="lightblue",
                      othermonthbackground="#1a1a1a",
                      othermonthforeground="gray")
        cal.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Add close button
        close_btn = tk.Button(cal_window, text="Close",
                            command=cal_window.destroy,
                            bg="#333333", fg="white",
                            activebackground="#444444",
                            activeforeground="white")
        close_btn.pack(pady=5)
        
        def keep_calendar_open():
            """Keep calendar open while mouse is over it or the datetime label"""
            if not cal_window.winfo_exists():
                return
            
            mouse_x = cal_window.winfo_pointerx()
            mouse_y = cal_window.winfo_pointery()
            
            # Check if mouse is over calendar window
            cal_x = cal_window.winfo_x()
            cal_y = cal_window.winfo_y()
            cal_width = cal_window.winfo_width()
            cal_height = cal_window.winfo_height()
            
            # Check if mouse is over datetime label
            dt_x = datetime_label.winfo_rootx()
            dt_y = datetime_label.winfo_rooty()
            dt_width = datetime_label.winfo_width()
            dt_height = datetime_label.winfo_height()
            
            # If mouse is over either calendar or datetime label, keep open
            if ((cal_x <= mouse_x <= cal_x + cal_width and 
                 cal_y <= mouse_y <= cal_y + cal_height) or
                (dt_x <= mouse_x <= dt_x + dt_width and 
                 dt_y <= mouse_y <= dt_y + dt_height)):
                cal_window.after(100, keep_calendar_open)
            else:
                cal_window.destroy()
        
        # Start checking mouse position
        cal_window.after(100, keep_calendar_open)
        
        # Prevent the calendar from being hidden by the auto-hide feature
        def on_calendar_enter(event):
            global hide_timer
            if hide_timer:
                root.after_cancel(hide_timer)
                hide_timer = None
        
        cal_window.bind("<Enter>", on_calendar_enter)
        cal.bind("<Enter>", on_calendar_enter)
    
    # Bind click event to show calendar
    datetime_label.bind("<Button-1>", show_calendar)
    
    update_time()
    return datetime_frame

# Update datetime widget position
datetime_widget = create_datetime_widget(canvas)
datetime_widget.place(relx=0.99, rely=0.95, anchor="se")  # Keep at far right




# Update the rounded rectangle size
canvas.create_rounded_rect(0, 0, 900, MENU_HEIGHT, radius, fill="#222222", outline="")

# Update window position calculation
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

def update_mute_button():
    is_muted = is_speaker_muted()
    if hasattr(speaker_button, 'image'):
        speaker_label_ref.config(text="Unmute" if is_muted else "Mute")
        speaker_button.config(
            command=unmute_speakers if is_muted else mute_speakers,
            image=images['volumemute'] if is_muted else images['volumeup']
        )
    root.after(1000, update_mute_button)

def check_mouse_position():
    global last_mouse_position, hide_timer
    
    x, y = root.winfo_pointerxy()
    last_mouse_position = (x, y)
    
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    center_left = (screen_width - 900) // 2  # Calculate left boundary of center 900px
    center_right = center_left + 900         # Calculate right boundary
    
    # Show window only if mouse is at top AND within center 900px
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
            hide_timer = root.after(300, hide_window)
    
    root.after(100, check_mouse_position)


def hide_window():
    global hide_timer
    # Only hide if mouse is still outside the window
    x, y = last_mouse_position
    if y >= 30 and not root.winfo_containing(x, y):
        root.withdraw()
    hide_timer = None




# Create arrow buttons
def create_arrow_buttons():
    def switch_page(direction):
        global current_page
        pages = [main_page_frame, second_page_frame]  # Add more pages if needed
        total_pages = len(pages)
        
        if direction == "right":
            current_page = (current_page + 1) % total_pages
        elif direction == "left":
            current_page = (current_page - 1) % total_pages
        
        # Hide all pages
        for page in pages:
            page.pack_forget()
        
        # Show current page
        pages[current_page].pack()
    
    # Left arrow button
    left_arrow_frame = tk.Frame(canvas, bg="#222222")
    left_arrow_frame.place(relx=0, rely=0.5, anchor="w")
    
    left_arrow_btn = tk.Button(left_arrow_frame, 
                              image=images['leftarrow'],
                              command=lambda: switch_page("left"),
                              bg="#222222",
                              activebackground="#333333",
                              bd=0,
                              cursor="hand2")
    left_arrow_btn.pack(padx=5)
    
    # Right arrow button
    right_arrow_frame = tk.Frame(canvas, bg="#222222")
    right_arrow_frame.place(relx=1.0, rely=0.5, anchor="e")
    
    right_arrow_btn = tk.Button(right_arrow_frame,
                               image=images['rightarrow'],
                               command=lambda: switch_page("right"),
                               bg="#222222",
                               activebackground="#333333",
                               bd=0,
                               cursor="hand2")
    right_arrow_btn.pack(padx=5)
    
    # Keep references to prevent garbage collection
    left_arrow_btn.image = images['leftarrow']
    right_arrow_btn.image = images['rightarrow']
    
    return left_arrow_frame, right_arrow_frame

# Add arrow buttons to the menu
left_arrow, right_arrow = create_arrow_buttons()



def setup_keyboard_shortcuts():
    """Setup keyboard shortcuts listeners"""
    global keyboard_listener
    
    if keyboard_listener:
        keyboard_listener.stop()
    
    def on_activate_show_hide():
        if root.winfo_viewable():
            root.withdraw()
        else:
            root.deiconify()
    
    def for_canonical(f):
        return lambda k: f(keyboard.canonical(k))
    
    # Create hotkey mapping
    # hotkeys = {
    #     shortcuts["Show/Hide Menu"]: on_activate_show_hide,
    #     shortcuts["Take Screenshot"]: take_screenshot,
    #     shortcuts["Open Calculator"]: open_calculator,
    #     shortcuts["Open Homepage"]: open_homepage
    # }
    
    # keyboard_listener = keyboard.GlobalHotKeys(hotkeys)
    # keyboard_listener.start()

# Add this to your UI layout
shortcuts_widget = create_shortcuts_manager(canvas)
shortcuts_widget.place(relx=0.08, rely=0.85, anchor="sw")

# Load shortcuts and setup listeners
# load_shortcuts()
# setup_keyboard_shortcuts()


# Toggle startup option
# ----------------------------------------------------------------------------------
def toggle_startup(enable):
    """
    Enable or disable running the application on startup.
    """
    global is_startup_enabled
    try:
        startup_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )

        # Get the correct path whether running as exe or script
        if getattr(sys, 'frozen', False):
            # Running as exe
            app_path = sys.executable
        else:
            # Running as script
            app_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'

        if enable:
            winreg.SetValueEx(startup_key, APP_NAME, 0, winreg.REG_SZ, app_path)
            show_notification(APP_NAME, "Enabled startup at boot.")
            logging.info(f"Startup Enabled. Path: {app_path}")
            print(f"Startup Enabled. Path: {app_path}")
        else:
            try:
                winreg.DeleteValue(startup_key, APP_NAME)
                show_notification(APP_NAME, "Disabled startup at boot.")
                logging.info(f"Startup Disabled")
                print(f"Startup Disabled")
            except FileNotFoundError:
                # Key doesn't exist, which is fine when disabling
                pass
        
        is_startup_enabled = enable
        save_config()  # Save the state to config file
        winreg.CloseKey(startup_key)
    except Exception as e:
        logging.error(f"Error toggling startup: {e}")
        show_notification(APP_NAME, f"Error: {e}")
        print(f"Error toggling startup: {e}")

def synchronize_startup_state():
    """
    Synchronize the startup state with the Windows Registry based on the is_startup_enabled variable.
    """
    global is_startup_enabled
    try:
        startup_key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name_key = APP_NAME

        # Get the correct path whether running as exe or script
        if getattr(sys, 'frozen', False):
            # Running as exe
            app_path = sys.executable
        else:
            # Running as script
            app_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'

        # Check if the app is already in the registry
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, startup_key_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, app_name_key)
                is_in_startup = True
        except FileNotFoundError:
            is_in_startup = False
        except WindowsError:
            is_in_startup = False

        # Add or remove the app from startup based on is_startup_enabled
        if is_startup_enabled and not is_in_startup:
            # Add to startup
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, startup_key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, app_name_key, 0, winreg.REG_SZ, app_path)
                logging.info(f"Added to startup. Path: {app_path}")
                print(f"Added to startup. Path: {app_path}")
        elif not is_startup_enabled and is_in_startup:
            # Remove from startup
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, startup_key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, app_name_key)
                logging.info("Removed from startup.")
                print("Removed from startup.")

    except Exception as e:
        logging.error(f"Error synchronizing startup state: {e}")
        print(f"Error synchronizing startup state: {e}")

def is_startup_checked(item):
    """
    Return whether the "Run on Startup" option is enabled.
    The `item` argument is required by pystray but not used here.
    """
    # logging.info(f"check startup")
    return is_startup_enabled

def on_toggle_startup(icon, item):
    """
    Toggle the startup status based on user selection.
    """
    # logging.info(f"on toggle startup")
    toggle_startup(not is_startup_enabled)



def create_system_tray():
    """Create system tray icon with menu"""
    def on_exit(icon, item):
        icon.stop()
        root.quit()
        
    # function to restart application 
    def on_restart(icon, item):
        icon.stop()
        show_notification(APP_NAME, "Restarting application...")
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    # function to show developer menu
    def on_developer(icon, item):
        webbrowser.open("https://bibekchandsah.com.np")
    
    # Load the icon
    icon_image = Image.open("assets/images/upmenu.ico")
    
    # Create the menu
    menu = (
        pystray.MenuItem("Run on Startup", (on_toggle_startup), checked=is_startup_checked),
        pystray.MenuItem("Take Screenshot", take_screenshot),
        pystray.MenuItem("Developer", on_developer),
        pystray.MenuItem("Restore Defaults", restore_defaults),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Restart", on_restart),
        pystray.MenuItem("Exit", on_exit)
    )
    
    # Create the icon
    icon = pystray.Icon("UpMenu", icon_image, "UpMenu", menu)
    
    return icon

# Add this code before root.mainloop()
def run_system_tray():
    icon = create_system_tray()
    icon.run()

# Start system tray in a separate thread
tray_thread = threading.Thread(target=run_system_tray, daemon=True)
tray_thread.start()

# Add this function before binding it
def arrange_buttons(event=None):
    """Update the frame size when window is configured"""
    main_container.update_idletasks()

# Keep these lines as they are
root.bind("<Configure>", arrange_buttons)
arrange_buttons()
update_mute_button()
check_mouse_position()  # Start checking mouse position

# Add this line after creating all UI elements but before the mainloop
def initialize_ui():
    """Initialize UI elements after everything is created"""
    if update_app_buttons_ref:
        update_app_buttons_ref()
        print("Initializing UI with saved apps")
    else:
        print("Warning: update_app_buttons_ref not initialized")

# root.mainloop()
if __name__ == "__main__":
    try:
        show_notification(APP_NAME, "Starting application...")
        root.mainloop()
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting gracefully.")
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        # Clean up system tray if it exists
        if 'tray_thread' in globals() and tray_thread.is_alive():
            root.quit()
