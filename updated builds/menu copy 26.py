# enhanced the UI design

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
from PIL import Image, ImageGrab
import pystray
import threading
import winreg
import logging
import json
import time
from tkcalendar import Calendar
import wmi

# Image paths
APP_NAME = "UpMenu"
ICON_PATHH = "assets/images/upmenu.ico"  # Ensure this is an ICO file
is_startup_enabled = True # Track the "Run on Startup" state

# Add this with other global declarations at the top
user_apps = {}  # Dictionary to store user's applications

# Add this global variable at the top with other globals
app_launcher_ref = None  # Reference to the app launcher frame

# Add this global variable at the top with other globals
update_app_buttons_ref = None  # Store reference to update function

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


# Determine the application directory for log folder & config file
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
canvas = tk.Canvas(root, width=900, height=300, bg="white", highlightthickness=0, highlightbackground="lightgray")
canvas.pack(pady=0)

# Draw rounded rectangle - move it to top
radius = 20
canvas.create_rounded_rect(0, 0, 900, 300, radius, fill="#222222", outline="lightgray")

# Create main container frame
main_container = tk.Frame(canvas, bg="#222222")
main_container.place(relx=0.5, rely=0, anchor="n")  # Place at top

# Add this function to control brightness
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

# Now create the controls
def create_media_controls(parent):
    media_frame = tk.Frame(parent, bg="#222222")
    
    # Create individual frames for each control (button + label)
    prev_control = tk.Frame(media_frame, bg="#222222")
    play_control = tk.Frame(media_frame, bg="#222222")
    next_control = tk.Frame(media_frame, bg="#222222")
    speaker_control = tk.Frame(media_frame, bg="#222222")
    
    # Use preloaded images
    prev_btn = tk.Button(prev_control, image=images['backward'], command=media_previous,
                        bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    play_btn = tk.Button(play_control, image=images['playpause'], command=media_play_pause,
                        bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    next_btn = tk.Button(next_control, image=images['forward'], command=media_next,
                        bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    
    current_speaker_img = images['volumemute'] if is_speaker_muted() else images['volumeup']
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
    prev_btn.image = images['backward']
    play_btn.image = images['playpause']
    next_btn.image = images['forward']
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


def create_top_controls(parent):
    global search_entry
    
    top_frame = tk.Frame(parent, bg="#222222")
    
    # Create search controls (left side)
    search_frame = tk.Frame(top_frame, bg="#222222")
    search_frame.pack(side=tk.LEFT, padx=20)
    
    # Create and style the search entry
    search_entry = tk.Entry(search_frame, 
                          width=52,
                          font=("Arial", 12),
                          bg="#323232",
                          fg="#8aa7ff",
                          insertbackground="#8aa7ff",
                          relief=tk.FLAT)
    search_entry.pack(side=tk.LEFT, padx=10, ipady=8)
    search_entry.bind("<Return>", on_enter)
    
    # Create search button with icon
    search_control = tk.Frame(search_frame, bg="#222222")
    search_control.pack(side=tk.LEFT, padx=5)
    
    search_btn = tk.Button(search_control, image=images['search'], command=search_google,
                        bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    search_btn.image = images['search']
    search_btn.pack(pady=(2, 0))
    
    search_label = tk.Label(search_control, text="Search", fg="lightgray",
                         bg="#222222", font=("Arial", 10), cursor="hand2")
    search_label.pack(pady=(0, 2))
    search_label.bind("<Button-1>", lambda e: search_google())
    
    # Create media controls (right side)
    media_frame = create_media_controls(top_frame)
    media_frame.pack(side=tk.LEFT, padx=20)
    
    return top_frame

def create_menu_controls(parent):
    menu_frame = tk.Frame(parent, bg="#222222")
    
    # Create individual frames for each control
    shutdown_control = tk.Frame(menu_frame, bg="#222222")
    restart_control = tk.Frame(menu_frame, bg="#222222")
    desktop_control = tk.Frame(menu_frame, bg="#222222")
    taskview_control = tk.Frame(menu_frame, bg="#222222")
    lock_control = tk.Frame(menu_frame, bg="#222222")
    brightness_control = tk.Frame(menu_frame, bg="#222222")
    calculator_control = tk.Frame(menu_frame, bg="#222222")
    screenshot_control = tk.Frame(menu_frame, bg="#222222")
    homepage_control = tk.Frame(menu_frame, bg="#222222")
    
    # Function to get brightness icon and next level
    def get_brightness_info():
        current_brightness = get_brightness()
        if current_brightness == 0:
            return 'brightness0', "Brightness-25"
        elif current_brightness <= 25:
            return 'brightness25', "Brightness-50"
        elif current_brightness <= 50:
            return 'brightness50', "Brightness-75"
        elif current_brightness <= 75:
            return 'brightness75', "Brightness-100"
        else:
            return 'brightness100', "Brightness-0"
    
    # Function to cycle through brightness levels
    def cycle_brightness():
        current = get_brightness()
        if current == 0:
            set_brightness(25)
        elif current <= 25:
            set_brightness(50)
        elif current <= 50:
            set_brightness(75)
        elif current <= 75:
            set_brightness(100)
        else:
            set_brightness(0)
        
        # Update the label and icon after changing brightness
        icon_name, label_text = get_brightness_info()
        brightness_btn.config(image=images[icon_name])
        brightness_btn.image = images[icon_name]
        brightness_label.config(text=label_text)
    
    # Use preloaded images
    shutdown_btn = tk.Button(shutdown_control, image=images['shutdown'], command=shut_down,
                         bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    restart_btn = tk.Button(restart_control, image=images['restart'], command=restart,
                         bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    desktop_btn = tk.Button(desktop_control, image=images['desktop'], command=show_desktop,
                         bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    taskview_btn = tk.Button(taskview_control, image=images['taskmenu'], command=task_view,
                         bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    lock_btn = tk.Button(lock_control, image=images['lock'], command=lock_screen,
                         bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    calculator_btn = tk.Button(calculator_control, image=images['calculator'], command=open_calculator,
                         bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    screenshot_btn = tk.Button(screenshot_control, image=images['screenshot'], command=take_screenshot,
                         bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    homepage_btn = tk.Button(homepage_control, image=images['homepage'], command=open_homepage,
                         bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    

    # Get initial brightness icon and label
    icon_name, label_text = get_brightness_info()
    brightness_btn = tk.Button(brightness_control, image=images[icon_name], command=cycle_brightness,
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
    calculator_label = tk.Label(calculator_control, text="Calculator", fg="lightgray",
                          bg="#222222", font=("Arial", 10), cursor="hand2")
    brightness_label = tk.Label(brightness_control, text=label_text, fg="lightgray",
                          bg="#222222", font=("Arial", 10), cursor="hand2")
    screenshot_label = tk.Label(screenshot_control, text="Screenshot", fg="lightgray",
                          bg="#222222", font=("Arial", 10), cursor="hand2")
    homepage_label = tk.Label(homepage_control, text="Homepage", fg="lightgray",
                          bg="#222222", font=("Arial", 10), cursor="hand2")
    

    # Keep references to prevent garbage collection
    shutdown_btn.image = images['shutdown']
    restart_btn.image = images['restart']
    desktop_btn.image = images['desktop']
    taskview_btn.image = images['taskmenu']
    lock_btn.image = images['lock']
    brightness_btn.image = images[icon_name]
    calculator_btn.image = images['calculator']
    screenshot_btn.image = images['screenshot']
    homepage_btn.image = images['homepage']

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
    brightness_btn.pack(pady=(2, 0))
    brightness_label.pack(pady=(0, 2))
    calculator_btn.pack(pady=(2, 0))
    calculator_label.pack(pady=(0, 2))
    screenshot_btn.pack(pady=(2, 0))
    screenshot_label.pack(pady=(0, 2))
    homepage_btn.pack(pady=(2, 0))
    homepage_label.pack(pady=(0, 2))
    

    # Pack control frames
    shutdown_control.pack(side=tk.LEFT, padx=10)
    restart_control.pack(side=tk.LEFT, padx=10)
    lock_control.pack(side=tk.LEFT, padx=10)
    desktop_control.pack(side=tk.LEFT, padx=10)
    taskview_control.pack(side=tk.LEFT, padx=10)
    brightness_control.pack(side=tk.LEFT, padx=10)
    calculator_control.pack(side=tk.LEFT, padx=10)
    screenshot_control.pack(side=tk.LEFT, padx=10)
    homepage_control.pack(side=tk.LEFT, padx=10)
    
    # Function to update brightness icon and label
    def update_brightness_display():
        icon_name, label_text = get_brightness_info()
        brightness_btn.config(image=images[icon_name])
        brightness_btn.image = images[icon_name]
        brightness_label.config(text=label_text)
        menu_frame.after(1000, update_brightness_display)
    
    # Start updating brightness display
    update_brightness_display()
    
    return menu_frame


# Move these function definitions before create_bottom_controls
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
    
    return volume_frame

# Move these functions before create_app_launcher
def add_new_app():
    from tkinter import filedialog
    
    # Ask for the application executable
    file_path = filedialog.askopenfilename(
        title="Select Application",
        filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
    )
    
    if file_path:
        # Ask for a custom name
        app_name = simpledialog.askstring("App Name", 
            "Enter a name for this application:",
            initialvalue=os.path.splitext(os.path.basename(file_path))[0])
        
        if app_name:
            # Add to user_apps dictionary without erasing existing apps
            user_apps[app_name] = file_path
            save_config()
            if update_app_buttons_ref:
                update_app_buttons_ref()
            show_notification(APP_NAME, f"Added {app_name} to applications")

def remove_app():
    # Create a dialog to select app to remove
    if not user_apps:
        messagebox.showinfo("Remove App", "No applications to remove.")
        return
        
    app_to_remove = simpledialog.askstring("Remove App", 
        "Enter the name of the app to remove:",
        initialvalue=list(user_apps.keys())[0])
        
    if app_to_remove in user_apps:
        del user_apps[app_to_remove]
        save_config()
        if update_app_buttons_ref:
            update_app_buttons_ref()

def initialize_app_launcher():
    """Initialize the app launcher with stored applications"""
    if update_app_buttons_ref:
        update_app_buttons_ref()
    else:
        print("Warning: update_app_buttons_ref not initialized")

# Now create_app_launcher can use these functions
def create_app_launcher(parent):
    """Create a quick app launcher with add/remove functionality"""
    global app_launcher_ref, user_apps, update_app_buttons_ref
    launcher_frame = tk.Frame(parent, bg="#222222")
    app_launcher_ref = launcher_frame

    # Create scrollable frame
    container = tk.Frame(launcher_frame, bg="#222222")
    canvas = tk.Canvas(container, bg="#222222", highlightthickness=0, width=780, height=65)
    scrollbar = tk.Scrollbar(launcher_frame, orient="horizontal", command=canvas.xview)
    scrollable_frame = tk.Frame(canvas, bg="#222222")

    canvas.configure(xscrollcommand=scrollbar.set)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        
    # Add mouse wheel scrolling
    def on_mousewheel(event):
        # Scroll horizontally with the mouse wheel
        canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
    
    # Bind mouse wheel to canvas and scrollable frame
    canvas.bind("<MouseWheel>", on_mousewheel)
    scrollable_frame.bind("<MouseWheel>", on_mousewheel)
    
    # Bind mouse wheel to all child widgets
    def bind_mousewheel_to_children(widget):
        widget.bind("<MouseWheel>", on_mousewheel)
        for child in widget.winfo_children():
            bind_mousewheel_to_children(child)
    
    bind_mousewheel_to_children(scrollable_frame)
        
    scrollable_frame.bind("<Configure>", on_frame_configure)

    # Pack elements
    container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    # Control frame stays fixed on right
    control_frame = tk.Frame(launcher_frame, bg="#222222")
    control_frame.pack(side=tk.RIGHT, padx=(10, 0))

    def update_app_buttons():
        # Clear existing buttons
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        
        # Create buttons for each app with wrapping
        row_frame = None
        buttons_per_row = 8
        current_row = []
        
        print("Updating app buttons. Current apps:", user_apps)
        
        for name, path in user_apps.items():
            if len(current_row) >= buttons_per_row:
                current_row = []
                
            if not current_row:
                row_frame = tk.Frame(scrollable_frame, bg="#222222")
                row_frame.pack(fill=tk.X, pady=2)
                # Bind mousewheel to row frame
                row_frame.bind("<MouseWheel>", on_mousewheel)
                
            btn = tk.Button(row_frame, text=name,
                          command=lambda p=path: os.startfile(p),
                          bg="#333333", fg="#d2d2d2",
                          activebackground="#444444",
                          activeforeground="#d2d2d2",
                          font=("Arial", 10),
                          width=12,
                          height=1)
            btn.pack(side=tk.LEFT, padx=2)
            # Bind mousewheel to button
            btn.bind("<MouseWheel>", on_mousewheel)
            current_row.append(btn)

    # Store the update function reference globally BEFORE creating buttons
    update_app_buttons_ref = update_app_buttons

    # Add and Remove buttons
    add_btn = tk.Button(control_frame, text="+",
                       command=add_new_app,
                       bg="#333333", fg="#d2d2d2",
                       activebackground="#444444",
                       activeforeground="#d2d2d2",
                       font=("Arial", 10),
                       width=3)
    add_btn.pack(side=tk.LEFT, padx=2)
    
    remove_btn = tk.Button(control_frame, text="-",
                          command=remove_app,
                          bg="#333333", fg="white",
                          activebackground="#444444",
                          activeforeground="white",
                          font=("Arial", 10),
                          width=3)
    remove_btn.pack(side=tk.LEFT, padx=2)
    
    return launcher_frame

def create_brightness_slider(parent):
    """Create a brightness slider control"""
    brightness_frame = tk.Frame(parent, bg="#222222")
    
    # Add brightness label
    brightness_label = tk.Label(brightness_frame, text="Brightness", fg="lightgray",
                            bg="#222222", font=("Arial", 10))
    brightness_label.pack(side=tk.LEFT, padx=(20, 10))  # Added left padding
    
    def on_brightness_change(val):
        try:
            set_brightness(int(float(val)))
            # Update value label
            value_label.config(text=f"{int(float(val))}%")
        except Exception as e:
            print(f"Error setting brightness: {e}")
    
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
    
    return brightness_frame


# Create and pack controls in order
# 1. Search and Media Controls (in red area)
red_area_frame = tk.Frame(main_container, bg="#222222", height=40)
red_area_frame.pack(fill=tk.X, pady=(10, 5))  # Small padding between sections

# Create search and media controls in the red area
search_frame = create_top_controls(red_area_frame)
search_frame.pack(pady=0)

# 2. Icon Menu
menu_controls = create_menu_controls(main_container)
menu_controls.pack(pady=(5, 5))  # Small padding between sections

# Add this before creating the app_launcher
def initialize_ui():
    """Initialize UI elements after everything is created"""
    if update_app_buttons_ref:
        update_app_buttons_ref()
        print("Initializing UI with saved apps")
    else:
        print("Warning: update_app_buttons_ref not initialized")

# Then create and pack the app launcher
app_launcher = create_app_launcher(main_container)
app_launcher.pack(pady=(5, 10))  # Small bottom padding
root.after(100, initialize_ui)  # Now initialize_ui is defined before being used

# Update window geometry
window_width = 900
window_height = 300
position_top = 0
# Update window position calculation
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_right = int(screen_width / 2 - window_width / 2)
root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

# Initially hide the window
# root.withdraw()

# Add this before the volume frame creation
# Create a horizontal line
separator_canvas = tk.Canvas(canvas, height=2, bg="#222222", highlightthickness=0)
separator_canvas.place(relx=0, rely=0.80, relwidth=1.0)  # Place it above the controls
separator_canvas.create_line(0, 1, 900, 1, fill="#d2d2d2", width=1)  # Red line

# Then continue with the volume frame and other controls
volume_frame = tk.Frame(canvas, bg="#222222")
volume_frame.place(relx=0.02, rely=0.95, anchor="sw")  # Adjust position

volume_widget = create_volume_slider(volume_frame)
volume_widget.pack(side=tk.LEFT)

brightness_widget = create_brightness_slider(volume_frame)
brightness_widget.pack(side=tk.LEFT)

datetime_widget = create_datetime_widget(canvas)
datetime_widget.place(relx=0.98, rely=0.95, anchor="se")  # Adjust position

# Update the rounded rectangle size
canvas.create_rounded_rect(0, 0, 900, 300, radius, fill="#222222", outline="lightgray")

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
            hide_timer = root.after(300, hide_window)
    
    root.after(100, check_mouse_position)


def hide_window():
    global hide_timer
    # Only hide if mouse is still outside the window
    x, y = last_mouse_position
    if y >= 30 and not root.winfo_containing(x, y):
        root.withdraw()
    hide_timer = None

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

