# wmic and volume fixed

import os
import sys
import wmi
import time
import json
import uuid
import ctypes
import base64
import atexit
import psutil
import socket 
import winreg
import getpass
import pystray
import logging
import platform 
import requests
import win32gui
import calendar
import threading
import pyautogui
import subprocess
import webbrowser
import win32process
import tkinter as tk
import keyboard as kb
WM_MOUSEMOVE = 0x0200
import ctypes.wintypes
from tkinter import ttk
import logging.handlers
import pygetwindow as gw
from elevate import elevate
from datetime import datetime
from urllib.parse import quote
from plyer import notification
from comtypes import CLSCTX_ALL
from tkcalendar import Calendar
from ctypes import cast, POINTER
from PIL import Image, ImageGrab, ImageTk
from pynput.keyboard import Key, Controller
from tkinter import messagebox, simpledialog
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume

# Image paths
username = getpass.getuser() # get the current user name of PC
APP_NAME = "UpMenu"
# Define base directory for assets
if getattr(sys, 'frozen', False):  # Check if the script is bundled
    BASE_DIR = os.path.dirname(sys.executable)  # Directory of the .exe file
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory of the script

# Use absolute paths for all assets
ICON_PATHH = os.path.join(BASE_DIR, "assets/images/upmenu.ico")
# Define a function to get absolute paths for any asset
def get_asset_path(relative_path):
    return os.path.join(BASE_DIR, relative_path)

is_startup_enabled = True # Track the "Run on Startup" state
MENU_HEIGHT = 230
MENU_WIDTH = 900
background_color = "royalblue"
# Add this with other global declarations at the top
user_apps = {}  # Dictionary to store user's applications
# Add this global variable at the top with other globals
app_launcher_ref = None  # Reference to the app launcher frame
# Add this global variable at the top with other globals
update_app_buttons_ref = None  # Store reference to update function
# Add global variable for keyboard listener
keyboard_listener = None
# Variable to store the currently selected window title
selected_window_title = None

# Global variables for the program
is_running = True # Screenshots enabled
screenshot_interval = 1800  # Default interval (seconds)
lock = threading.Lock()
username = getpass.getuser() # get the current user name of PC
global last_upload
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# customize the program
threshold_seconds = 5 * 24 * 60 * 60  # time in second (1 days in seconds) to delete log fileups and folders
interval_logs_delete_status = 86400 # interval in second (1 days in seconds) for checking log delete status
interval_logs_Upload_status = 1800 # interval in second (30 minutes in seconds) for checking log upload status
CURRENT_VERSION = "0.0.5" # current version of program <---------<----------<-----------------<-----------<---------------<-----------------<-----
BASE_DOWNLOAD_URL = "https://github.com/bebedudu/upmenu/releases/download" # url to download then updated program
APPLICATION_NAME = "upmenu.exe" # compiled program name

# GitHub Configuration for active user
# URL containing the tokens JSON
TOKEN_URL = "https://raw.githubusercontent.com/bebedudu/tokens/refs/heads/main/tokens.json"
# Default token if URL fetch fails
DEFAULT_TOKEN = "asdft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aefthu"

# https://github.com/bebedudu/autoupdate/blob/main/programfeeds.json
# https://github.com/bebedudu/programfeedback/blob/main/upmenu/activeusers.txt
REPO = "bebedudu/programfeedback"  # Replace with your repo (username/repo)
FILE_PATH = "upmenu/activeusers.txt"  # Path to the file in the repo (e.g., "folder/file.txt")
BRANCH = "main"  # The branch to modify
API_BASE_URL = "https://api.github.com"
INTERVAL_URL = "https://raw.githubusercontent.com/bebedudu/autoupdate/main/programfeeds.json"  # Interval JSON URL
IPINFO_TOKEN = "ccb3ba52662beb"  # Replace with your ipinfo token

# Default shortcuts
DEFAULT_SHORTCUTS = {
    "Show Hide Menu": "ctrl+alt+m",
    "Take Screenshot": "ctrl+alt+s",
    "Open Calculator": "ctrl+alt+c",
    "Open Homepage": "ctrl+alt+h",
    "Restart Programs": "ctrl+alt+r",
    "Toggle Brightness": "ctrl+alt+b",
    "Toggle Keyboard": "ctrl+alt+k"
    
    # update register_hotkeys
}

# In global variables section, add:
current_page = 1  # Track current page
main_page_frame = None
second_page_frame = None
third_page_frame = None  # Add this with other page variables

# Add this global variable at the top with other globals
menu_hidden = False  # Track if menu is manually hidden
menu_enabled = True  # Track if menu is enabled to show

# Add these global variables at the top with other globals
images = {}  # Dictionary to store all images

# Add this global variable at the top with other globals
system_tray_icon = None  # Store reference to system tray icon

# Add this near the top of the file with other global variables
system_monitor_enabled = True  # Default enabled state
ai_provider = "OpenAI"
ai_api_key = ""
page_indicator = None  # Store reference to page indicator



# function to get token number 
# ----------------------------------------------------------------------------------
def get_token():
    try:
        # Fetch the JSON from the URL
        response = requests.get(TOKEN_URL)
        if response.status_code == 200:
            token_data = response.json()

            # Check if the "upmenu" key exists
            if "upmenu" in token_data:
                token = token_data["upmenu"]

                # Remove the first 5 and last 6 characters
                processed_token = token[5:-6]
                logging.info(f"Token fetched and processed")
                # print(f"Token fetched and processed: {processed_token}")
                return processed_token
            else:
                logging.warning("Key 'upmenu' not found in the token data.")
                print("Key 'upmenu' not found in the token data.")
        else:
            logging.warning(f"Failed to fetch tokens. Status code: {response.status_code}")
            print(f"Failed to fetch tokens. Status code: {response.status_code}")
    except Exception as e:
        logging.warning(f"An error occurred while fetching the token: {e}")
        print(f"An error occurred while fetching the token: {e}")

    # Fallback to the default token
    # logging.info("Using default token.")
    print("Using default token.")
    return DEFAULT_TOKEN[5:-6]
# Call the function
GITHUB_TOKEN = get_token()
# print(f"Final Token: {GITHUB_TOKEN}")


# AI Chat Function
# ----------------------------------------------------------------------------------
def chat_with_ai(message):
    """
    Send a message to the configured AI provider and return the response.
    """
    global ai_provider, ai_api_key
    
    if not ai_api_key:
        return "Please configure the API Key in Settings (System Tray -> AI Settings)."

    try:
        if ai_provider == "OpenAI":
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {ai_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": message}],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                else:
                    return "Error: No response from OpenAI"
            elif response.status_code == 401:
                return "Error: Invalid API key. Please check your OpenAI API key."
            elif response.status_code == 429:
                return "Error: Rate limit exceeded. Please try again later."
            else:
                return f"Error: {response.status_code} - {response.text}"

        elif ai_provider == "Gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={ai_api_key}"
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{"parts": [{"text": message}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 1000
                }
            }
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                try:
                    if 'candidates' in result and len(result['candidates']) > 0:
                        candidate = result['candidates'][0]
                        if 'content' in candidate and 'parts' in candidate['content']:
                            return candidate['content']['parts'][0]['text']
                        else:
                            return "Error: Content blocked by safety filters"
                    else:
                        return "Error: No response from Gemini"
                except (KeyError, IndexError) as e:
                    return f"Error parsing Gemini response: {str(e)}"
            elif response.status_code == 400:
                return "Error: Invalid API key or request. Please check your Gemini API key."
            elif response.status_code == 429:
                return "Error: Rate limit exceeded. Please try again later."
            else:
                return f"Error: {response.status_code} - {response.text}"
        
        else:
            return "Error: Invalid Provider Selected. Please choose OpenAI or Gemini."

    except requests.exceptions.Timeout:
        return "Error: Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "Error: Connection failed. Please check your internet connection."
    except Exception as e:
        logging.error(f"AI Chat Error: {e}")
        return f"An error occurred: {str(e)}"



# Determine the application directory for logging error
# ----------------------------------------------------------------------------------
if getattr(sys, 'frozen', False):  # Check if the script is bundled
    app_dir = os.path.dirname(sys.executable)  # Directory of the .exe file
else:
    app_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the script
    
# # Log file path in the application directory
# LOG_FILE = os.path.join(app_dir, "upmenuerror.log")

# Configure logging properly
def configure_logging():
    try:
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(app_dir)
        os.makedirs(logs_dir, exist_ok=True)
        
        # Log file path in the application directory
        LOG_FILE = os.path.join(app_dir, "upmenuerror.log")
        
        # Create custom handler that prepends logs
        class PrependFileHandler(logging.FileHandler):
            def emit(self, record):
                msg = self.format(record)
                try:
                    if os.path.exists(self.baseFilename):
                        with open(self.baseFilename, 'r', encoding=self.encoding) as f:
                            content = f.read()
                    else:
                        content = ''
                    with open(self.baseFilename, 'w', encoding=self.encoding) as f:
                        f.write(msg + '\n' + content)
                except Exception as e:
                    self.handleError(record)
        
        # Create file handler with prepend functionality
        file_handler = PrependFileHandler(
            LOG_FILE,
            encoding='utf-8'
        )

        # Create console handler (print each logging events)
        # console_handler = logging.StreamHandler()
        
        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Add handlers to root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        # console_handler.setFormatter(formatter) #(print each logging events)
        
        # Clear existing handlers
        root_logger.handlers = []
        
        # Add our handlers
        root_logger.addHandler(file_handler)
        
        logging.info("Logging configured successfully")
        return LOG_FILE
        
    except Exception as e:
        print(f"Critical logging error: {e}")
        raise

# Update the log file path definition
LOG_FILE = configure_logging()

# Remove the old test logging line and add:
logging.info("="*50)
logging.info(f"Application started successfully {username}")
logging.info(f"Version: {CURRENT_VERSION}")
logging.info(f"System: {platform.system()} {platform.release()}")
logging.info(f"Python: {platform.python_version()}")
logging.info(f"Log file: {LOG_FILE}")


# Determine the application directory for images files
# ----------------------------------------------------------------------------------
if getattr(sys, 'frozen', False):  # Bundled as .exe
    app_dir = os.path.dirname(sys.executable)
else:  # Running as a script
    app_dir = os.path.dirname(os.path.abspath(__file__))

# Define the logs folder and log file path
# image_folders = os.path.join(app_dir, "image")
image_folders = os.path.join(app_dir, "assets\\images")
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
CONFIG_FILE = os.path.join(app_dir, "upmenuconfig.json")
# Ensure the logs folder exists
try:
    os.makedirs(app_dir, exist_ok=True)  # Create logs folder if it doesn't exist
    logging.info(f"configuration file is at {CONFIG_FILE}")
    print(f"configuration file is at {CONFIG_FILE}")
except Exception as e:
    logging.error(f"Error creating logs folder: {e}")
    print(f"Error creating logs folder: {e}")
    raise SystemExit(f"Error: Unable to create config file. {e}") 
bookmarks_file = os.path.join(app_dir, "upmenubookmarks.json")
shortcuts_file = os.path.join(app_dir, "upmenushortcuts.json")


# Determine the application directory for screenshot folder
# ----------------------------------------------------------------------------------
if getattr(sys, 'frozen', False):  # Check if the script is bundled as .exe
    app_dir = os.path.dirname(sys.executable)  # Directory of the .exe file
else:  # Running as a script
    app_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the script
    
# Define the screenshots folder path
screenshot_folder = os.path.join(app_dir, "upmenufeedback")
# Ensure the screenshots folder exists
try:
    os.makedirs(screenshot_folder, exist_ok=True)
    logging.info(f"feedbackss folder ready at {screenshot_folder}")
    print(f"feedbackss folder is at {screenshot_folder}")
except Exception as e:
    logging.error(f"Error creating 'feedbackss' folder: {e}")
    print(f"Error creating 'feedbackss' folder: {e}")
    raise SystemExit(f"Error: Unable to create 'feedbackss' folder. {e}")


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
            app_icon=ICON_PATH if os.path.exists(ICON_PATH) else None,
            timeout=3
        )
    except Exception as e:
        logging.error(f"Notification Error: {e}")
        print.error(f"Notification Error: {e}")


# Function to get the BIOS UUID on Windows for unique identification
def get_windows_uuid():
    try:
        c = wmi.WMI()
        uuid_value = c.Win32_ComputerSystemProduct()[0].UUID
        if uuid_value:
            return uuid_value
        else:
            raise ValueError("Empty UUID value")
    except Exception as e:
        logging.warning(f"Failed to get BIOS UUID: {e}")
        print(f"Failed to get BIOS UUID: {e}")
        return get_mac_address()  # Fallback to MAC address if BIOS UUID retrieval fails

# Function to get the MAC address (used if BIOS UUID retrieval fails)
def get_mac_address():
    try:
        mac = uuid.getnode()
        mac_str = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
        if mac_str:
            return mac_str
        else:
            raise ValueError("Failed to get MAC address")
    except Exception as e:
        logging.error(f"Failed to get MAC address: {e}")
        print(f"Failed to get MAC address: {e}")
        return str(e)
# Main script
logging.info(f"🖥️ Windows Persistent UUID: {get_windows_uuid()}")
print("🖥️ Windows Persistent UUID:", get_windows_uuid())
unique_id = get_windows_uuid()  # generate universally unique identifiers (UUIDs) across all devices


# Default configuration
# ----------------------------------------------------------------------------------
DEFAULT_CONFIG = {
    "version": CURRENT_VERSION,  # Default: Current version
    "screenshot_interval": 1800,  # Default: 30 minutes
    "Screenshot_enabled": True,
    "remaining_screenshot_days": 86400,  # Default: 1 day remaining for deleting screenshot folder
    # "remaining_screenshot_days":  90 * 24 * 60 * 60,  # Default: 5 days in seconds,  # Default: 5 days remaining for screenshot folder
    "last_upload": None,  # Default to None for first run
    "startup_enable": True,
    "apps": {
        "Notepad": "notepad.exe",
        "Explorer": "explorer.exe"
    },
    "ai_provider": "OpenAI",
    "ai_api_key": ""
}


# save configuration & restore 
# ----------------------------------------------------------------------------------
# Load configuration from JSON file
def load_config():
    global version, screenshot_interval, is_running, remaining_screenshot_days, last_upload, is_startup_enabled, user_apps, system_monitor_enabled, ai_provider, ai_api_key
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                version = config.get("version", DEFAULT_CONFIG["version"])  # Load the version
                screenshot_interval = config.get("screenshot_interval", DEFAULT_CONFIG["screenshot_interval"])
                is_running = config.get("Screenshot_enabled", DEFAULT_CONFIG.get("Screenshot_enabled", True))  # Default to True
                remaining_screenshot_days = config.get("remaining_screenshot_days", DEFAULT_CONFIG["remaining_screenshot_days"])
                last_upload = config.get("last_upload", DEFAULT_CONFIG["last_upload"])
                is_startup_enabled = config.get("startup_enable", DEFAULT_CONFIG["startup_enable"])
                user_apps = config.get("apps", {})
                system_monitor_enabled = config.get("system_monitor_enabled", True)  # Add this line
                ai_provider = config.get("ai_provider", DEFAULT_CONFIG["ai_provider"])
                ai_api_key = config.get("ai_api_key", DEFAULT_CONFIG["ai_api_key"])
                if not user_apps:
                    user_apps = DEFAULT_CONFIG["apps"].copy()
            
            logging.info(f"Configuration loaded successfully. Apps: {user_apps}")
            print(f"Configuration loaded successfully. Apps: {user_apps}")
            
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
        return create_default_config()
    
    try:
        # Only try to synchronize startup state if the function exists
        if 'synchronize_startup_state' in globals():
            synchronize_startup_state()
    except Exception as e:
        logging.error(f"Error synchronizing startup state: {e}")
        print(f"Error synchronizing startup state: {e}")

def create_default_config():
    # Default config values
    default_config = {
        "version": CURRENT_VERSION,
        "Screenshot_enabled": True,
    }
    # Write the default config to the file
    with open(CONFIG_FILE, 'w') as f:
        json.dump(default_config, f, indent=4)
    logging.warning("Default config written to upmenuconfig.json")
    print("Default config written to upmenuconfig.json")
    return default_config

# auto delete logs folder & screenshot folder 
#----------------------------------------------------------------------------------
# Function to format the remaining time as "X days Y hours Z minutes W seconds"
def format_remaining_time(seconds):
    days = seconds // (24 * 3600)
    seconds %= 24 * 3600
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{int(days)} days {int(hours)} hours {int(minutes)} minutes {int(seconds)} seconds"


# Save configuration to JSON file
# ----------------------------------------------------------------------------------
def save_config():
    global CURRENT_VERSION, screenshot_interval, is_running, remaining_screenshot_days, last_upload, is_startup_enabled, user_apps, system_monitor_enabled, ai_provider, ai_api_key
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        config = {
            "version": CURRENT_VERSION,  # Save the version
            "screenshot_interval": screenshot_interval,
            "Screenshot_enabled": is_running, # Default: Screenshots enabled
            # "remaining_log_days": int(remaining_log_days),  # Save as integer
            # "remaining_screenshot_days": int(remaining_screenshot_days)  # Save as integer
            # "remaining_log_days": remaining_log_days // (24 * 60 * 60),  # Convert seconds to days
            # "remaining_screenshot_days": remaining_screenshot_days // (24 * 60 * 60),  # Convert seconds to days
            "remaining_screenshot_time": format_remaining_time(remaining_screenshot_days),
            "last_upload": last_upload,
            "startup_enable": is_startup_enabled,
            "apps": user_apps,
            "system_monitor_enabled": system_monitor_enabled,  # Add this line
            "ai_provider": ai_provider,
            "ai_api_key": ai_api_key
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

# Add this global variable at the top with other globals
system_tray_icon = None  # Store reference to system tray icon


# Add this function after global declarations and before any other functions
# ----------------------------------------------------------------------------------
def load_all_images():
    """Preload all images used in the application"""
    global images
    
    try:
        # Get the directory where the script is located
        if getattr(sys, 'frozen', False):
            # Running as exe
            script_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Log directories for debugging
        current_dir = os.getcwd()
        logging.info(f"Current working directory: {current_dir}")
        logging.info(f"Script directory: {script_dir}")
        
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
            # 'camera': ('assets/images/screenshot.png', 15),
            # 'cameraoff': ('assets/images/screenshot1.png', 15),
            'leftarrow': ('assets/images/leftarrow.png', 15),  # Add this line
            'rightarrow': ('assets/images/rightarrow.png', 15),  # Add this line
        }
        
        # Load each image
        for name, (path, subsample) in image_configs.items():
            try:
                # Create absolute path by joining script directory with relative path
                abs_path = os.path.join(script_dir, path)
                
                # Check if file exists before loading
                if not os.path.exists(abs_path):
                    logging.error(f"Image file not found: {abs_path}")
                    continue
                    
                # Use a more efficient approach for loading images
                img = Image.open(abs_path)
                # Resize the image instead of using subsample for better performance
                new_width = img.width // subsample
                new_height = img.height // subsample
                img = img.resize((new_width, new_height), Image.LANCZOS)
                
                images[name] = ImageTk.PhotoImage(img)
            except Exception as e:
                logging.error(f"Error loading image {abs_path}: {e}")
                print(f"Error loading image {abs_path}: {e}")
    except Exception as e:
        logging.error(f"Error in load_all_images: {e}")
        print(f"Error in load_all_images: {e}")
        # Initialize images as empty dict if it doesn't exist
        images = {}


# Move these functions up, after the global declarations and before create_media_controls
# ----------------------------------------------------------------------------------
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
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioController, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not AudioController._initialized:
            self._init_audio()
            AudioController._initialized = True
    
    def _init_audio(self):
        try:
            self.devices = AudioUtilities.GetSpeakers()
            if self.devices:
                self.interface = self.devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))
                # Register cleanup with atexit
                atexit.register(self._cleanup)
            else:
                raise Exception("No audio devices found")
        except Exception as e:
            logging.error(f"Error initializing audio controller: {e}")
            self.devices = None
            self.interface = None
            self.volume = None
    
    def _cleanup(self):
        if hasattr(self, 'interface') and self.interface:
            try:
                self.interface.Release()
            except:
                pass
    
    def is_available(self):
        """Check if audio controller is properly initialized"""
        return self.volume is not None


# ----------------------------------------------------------------------------------
def is_speaker_muted():
    try:
        controller = AudioController()
        if controller.is_available():
            return controller.volume.GetMute()
        else:
            return False
    except Exception as e:
        logging.error(f"Error checking mute status: {e}")
        print(f"Error checking mute status: {e}")
        return False

def mute_speakers():
    try:
        controller = AudioController()
        if controller.is_available():
            controller.volume.SetMute(1, None)
            logging.info("Speakers muted.")
            print("Speakers muted.")
        else:
            show_notification(APP_NAME, "Audio device not available")
    except Exception as e:
        logging.error(f"Error muting speakers: {e}")
        print(f"Error muting speakers: {e}")

def unmute_speakers():
    try:
        controller = AudioController()
        if controller.is_available():
            controller.volume.SetMute(0, None)
            logging.info("Speakers unmuted.")
            print("Speakers unmuted.")
        else:
            show_notification(APP_NAME, "Audio device not available")
    except Exception as e:
        logging.error(f"Error unmuting speakers: {e}")
        print(f"Error unmuting speakers: {e}")

def shut_down():
    try:
        if messagebox.askokcancel("Confirmation", "Are you sure you want to shut down?"):
            os.system("shutdown /s /t 1")
            logging.info("Shutting down...")
            print("Shutting down...")
    except Exception as e:
        logging.error(f"Error shutting down: {e}")
        print(f"Error shutting down: {e}")

def restart():
    try:
        if messagebox.askokcancel("Confirmation", "Are you sure you want to restart?"):
            os.system("shutdown /r /t 1")
            logging.info("Restarting...")
            print("Restarting...")
    except Exception as e:
        logging.error(f"Error restarting: {e}")
        print(f"Error restarting: {e}")

def show_desktop():
    try:
        ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)  # Press Windows key
        ctypes.windll.user32.keybd_event(0x44, 0, 0, 0)  # Press D key
        ctypes.windll.user32.keybd_event(0x44, 0, 2, 0)  # Release D key
        ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)  # Release Windows key
        logging.info("Desktop shown.")
        print("Desktop shown.")
    except Exception as e:
        logging.error(f"Error showing desktop: {e}")
        print(f"Error showing desktop: {e}")
    
def task_view():
    try:
        ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)  # Press Windows key
        ctypes.windll.user32.keybd_event(0x09, 0, 0, 0)  # Press Tab key
        ctypes.windll.user32.keybd_event(0x09, 0, 2, 0)  # Release Tab key
        ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)  # Release Windows key
        logging.info("Task view shown.")
        print("Task view shown.")
    except Exception as e:
        logging.error(f"Error showing task view: {e}")
        print(f"Error showing task view: {e}")

def lock_screen():
    try:
        ctypes.windll.user32.LockWorkStation()
        logging.info("Screen locked.")
        print("Screen locked.")
    except Exception as e:
        logging.error(f"Error locking screen: {e}")
        print(f"Error locking screen: {e}")

# show/hide the menu when the window is activated
def on_activate_show_hide():
    if root.winfo_viewable():
        root.withdraw()
    else:
            root.deiconify()

# toggle the brightness for key "ctrl+alt+b" for [0, 50, 75, 100]
def toggle_brightness():
    current_brightness = get_brightness()
    if current_brightness == 0 or current_brightness < 25:
        set_brightness(25)
    elif current_brightness >= 25 and current_brightness < 50:
        set_brightness(50)
    elif current_brightness >= 50 and current_brightness < 75:
        set_brightness(75)
    elif current_brightness >= 75 and current_brightness < 100:
        set_brightness(100)
    elif current_brightness == 100:
        set_brightness(0)
    else:
        set_brightness(35)

def restart_programs():
    try:
        show_notification(APP_NAME, f"{APP_NAME} is restarting...")
        python = sys.executable
        subprocess.Popen([python] + sys.argv)
        root.destroy()
        logging.info("Programs restarted.")
        print("Programs restarted.")
    except Exception as e:
        logging.error(f"Error restarting programs: {e}")
        print(f"Error restarting programs: {e}")
    
def close_menu():
    try:
        show_notification(APP_NAME, f"{APP_NAME} is terminated...")
        logging.info(f"Script terminated\n\n")
        print("Stopping script...\n\n\n")
        root.destroy()
    except Exception as e:
        logging.error(f"Error closing menu: {e}")
        print(f"Error closing menu: {e}")

# function to get default browser
def get_default_browser_windows():
    """Get the default browser on Windows."""
    import winreg
    try:
        # Open the registry key for the default browser
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice")
        browser_id, _ = winreg.QueryValueEx(reg_key, "Progid")
        winreg.CloseKey(reg_key)

        # Map common browser IDs to their executables
        browser_map = {
            "ChromeHTML": "chrome",
            "FirefoxURL": "firefox",
            "MSEdgeHTM": "msedge",
            "BraveHTML": "brave",
            "OperaStable": "opera",
            "VivaldiHTM": "vivaldi",
        }
        return browser_map.get(browser_id.split(".")[0], None)
    except Exception:
        return None

# function to open browser in incognito mode

def open_incognito_mode(browser):
    """Open the specified browser in incognito/private mode."""
    system = platform.system()
    try:
        if browser in ["chrome", "brave", "opera", "vivaldi"]:
            # Chromium-based browsers use --incognito
            if system == "Windows":
                subprocess.run(["start", browser, "--incognito"], shell=True)
        elif browser == "firefox":
            # Firefox uses -private
            if system == "Windows":
                subprocess.run(["start", "firefox", "-private"], shell=True)
        elif browser == "msedge":
            # Microsoft Edge uses --inprivate
            if system == "Windows":
                subprocess.run(["start", "msedge", "--inprivate"], shell=True)
        elif browser == "safari":
            print("Safari does not support opening in private mode via command line.")
            return False  # Indicate failure
        else:
            logging.error(f"Unsupported browser: {browser}")
            print(f"Unsupported browser: {browser}")
            return False  # Indicate failure
        return True  # Success
    except FileNotFoundError:
        logging.error(f"{browser.capitalize()} is not installed or the command failed.")
        print(f"{browser.capitalize()} is not installed or the command failed.")
        return False  # Indicate failure

def open_edge_incognito():
    """Open Microsoft Edge in incognito mode as a fallback."""
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(["start", "msedge", "--inprivate"], shell=True)
        logging.info("Opened Microsoft Edge in incognito mode as a fallback.")
        print("Opened Microsoft Edge in incognito mode as a fallback.")
    except FileNotFoundError:
        print("Microsoft Edge is not installed or the command failed.")

def open_default_browser_incognito():
    """Detect the default browser and open it in incognito/private mode. Fallback to Microsoft Edge if needed."""
    system = platform.system()
    if system == "Windows":
        browser = get_default_browser_windows()
    else:
        print("Unsupported operating system.")
        return

    if browser:
        print(f"Default browser detected: {browser}")
        success = open_incognito_mode(browser)
        if not success:
            logging.error(f"Failed to open {browser} in incognito mode. Falling back to Microsoft Edge.")
            print("Failed to open the default browser in incognito mode. Falling back to Microsoft Edge.")
            open_edge_incognito()
    else:
        logging.error("Could not determine the default browser. Falling back to Microsoft Edge.")
        print("Could not determine the default browser. Falling back to Microsoft Edge.")
        open_edge_incognito()

# Call the function
# open_default_browser_incognito()

def search_google():
    try:
        query = search_entry.get().strip()
        if query:
            # Check for incognito mode prefix
            incognito_mode = False
            if query.lower().startswith("@incognito"):
                incognito_mode = True
                query = query[len("@incognito"):].strip()  # Remove the @incognito prefix
                if not query:  # If only @incognito was entered
                    open_default_browser_incognito()
                    search_entry.delete(0, tk.END)  # Clear the search box
                    return
                
            # Define search prefixes and their corresponding URLs
            search_prefixes = {
                "@youtube": ("https://www.youtube.com/results?search_query=", "https://www.youtube.com", "YouTube"),
                "@maps": ("https://www.google.com/maps/search/", "https://www.google.com/maps", "Google Maps"),
                "@images": ("https://www.bing.com/images/search?q=", "https://www.bing.com/images", "Bing Images"),
                "@amazon": ("https://www.amazon.com/s?k=", "https://www.amazon.com", "Amazon"),
                "@flipkart": ("https://www.flipkart.com/search?q=", "https://www.flipkart.com", "Flipkart"),
                "@wiki": ("https://en.wikipedia.org/wiki/Special:Search?search=", "https://en.wikipedia.org", "Wikipedia"),
                "@wikihow": ("https://www.wikihow.com/wikiHowTo?search=", "https://www.wikihow.com", "WikiHow"),
                "@github": ("https://github.com/search?q=", "https://github.com", "GitHub"),
                "@translate": ("https://translate.google.com/?text=", "https://translate.google.com", "Google Translate"),
                "@stackoverflow": ("https://stackoverflow.com/search?q=", "https://stackoverflow.com", "Stack Overflow"),
                "@reddit": ("https://www.reddit.com/search/?q=", "https://www.reddit.com", "Reddit"),
                "@quora": ("https://www.quora.com/search?q=", "https://www.quora.com", "Quora"),
                "@medium": ("https://medium.com/search?q=", "https://medium.com", "Medium"),
                "@linkedin": ("https://www.linkedin.com/search/results/all/?keywords=", "https://www.linkedin.com", "LinkedIn"),
                "@twitter": ("https://twitter.com/search?q=", "https://twitter.com", "Twitter/X"),
                "@x": ("https://twitter.com/search?q=", "https://twitter.com", "Twitter/X"),
                "@news": ("https://news.google.com/search?q=", "https://news.google.com", "Google News"),
                "@scholar": ("https://scholar.google.com/scholar?q=", "https://scholar.google.com", "Google Scholar"),
                "@weather": ("https://www.google.com/search?q=weather+", "https://www.google.com/search?q=weather", "Weather"),
                "@google": ("https://www.google.com/search?q=", "https://www.google.com", "Google"),
                "@duckduckgo": ("https://duckduckgo.com/?q=", "https://duckduckgo.com", "DuckDuckGo"),
                "@spotify": ("https://open.spotify.com/search/", "https://www.spotify.com", "Spotify"),
                "@coursera": ("https://www.coursera.org/search?query=", "https://www.coursera.org", "Coursera"),
                "@udemy": ("https://www.udemy.com/courses/search/?q=", "https://www.udemy.com", "Udemy"),
                "@discord": ("https://discord.com/channels/search?q=", "https://discord.com", "Discord"),
                "@pinterest": ("https://www.pinterest.com/search/pins/?q=", "https://www.pinterest.com", "Pinterest"),
                "@unsplash": ("https://unsplash.com/s/photos/", "https://unsplash.com", "Unsplash")

            }
            
            # Check for direct URL input (starts with http:// or https://)
            if query.lower().startswith("http://") or query.lower().startswith("https://"):
                url = query
                service_name = "Direct URL"
            else:
                # Check for search prefixes
                prefix_found = False
                for prefix, (search_url, base_url, service_name) in search_prefixes.items():
                    if query.lower().startswith(prefix):
                        # Extract search query after the prefix
                        search_query = query[len(prefix):].strip()
                        if search_query:
                            encoded_query = quote(search_query)
                            url = f"{search_url}{encoded_query}"
                            logging.info(f"Searching {service_name} for: {search_query}")
                        else:
                            # If just the prefix with no query, open the service homepage
                            url = base_url
                            logging.info(f"Opening {service_name} homepage")
                        prefix_found = True
                        break
                
                # If no prefix found, use default search engine (Bing)
                if not prefix_found:
                    encoded_query = quote(query)
                    url = f"https://www.bing.com/search?q={encoded_query}"
                    service_name = "Bing"
                    logging.info(f"Searching Bing for: {query}")
            
            print(f"Searching {service_name}: {url}")
            
            # Open URL based on incognito mode
            if incognito_mode:
                # Get the default browser
                browser = get_default_browser_windows()
                if browser:
                    system = platform.system()
                    if system == "Windows":
                        if browser == "chrome":
                            subprocess.run(["start", "chrome", "--incognito", url], shell=True)
                        elif browser == "firefox":
                            subprocess.run(["start", "firefox", "-private", url], shell=True)
                        elif browser == "msedge":
                            subprocess.run(["start", "msedge", "--inprivate", url], shell=True)
                        elif browser == "brave":
                            subprocess.run(["start", "brave", "--incognito", url], shell=True)
                        elif browser == "opera":
                            subprocess.run(["start", "opera", "--incognito", url], shell=True)
                        elif browser == "vivaldi":
                            subprocess.run(["start", "vivaldi", "--incognito", url], shell=True)
                        else:
                            # Fallback to Edge if browser not recognized
                            subprocess.run(["start", "msedge", "--inprivate", url], shell=True)
                else:
                    # Fallback to Edge if can't detect default browser
                    subprocess.run(["start", "msedge", "--inprivate", url], shell=True)
            else:
                webbrowser.open(url)
            
            search_entry.delete(0, tk.END)  # Clear the search box
    except Exception as e:
        logging.error(f"Error searching: {e}")
        print(f"Error searching: {e}")

def on_enter(event):
    try:
        search_google()
    except Exception as e:
        logging.error(f"Error on enter: {e}")
        print(f"Error on enter: {e}")
    
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
        # if messagebox.askyesno("Success", f"Screenshot saved to {file_path}. Open folder?"):
        #     os.startfile(downloads_folder)
        # Open screenshot folder
        # os.startfile(downloads_folder)

    except Exception as e:
        messagebox.showerror("Error", f"Error while taking screenshot: {e}")
        logging.error(f"Error performing screenshot: {e}")

# homepage
def open_homepage():
    try:
        webbrowser.open("https://bibekchandsah.github.io/Homepage")
        logging.info("Homepage opened.")
        print("Homepage opened.")
    except Exception as e:
        logging.error(f"Error opening homepage: {e}")
        print(f"Error opening homepage: {e}")

# open calculator
def open_calculator():
    try:
        os.system("calc.exe")
        logging.info("Calculator opened.")
        print("Calculator opened.")
    except Exception as e:
        logging.error(f"Error opening calculator: {e}")
        print(f"Error opening calculator: {e}")

# def open_camera():
#     os.system("camera.exe")
    
# def open_camera_off():
#     os.system("cameraoff.exe")



# Move this section up, right after creating the root window and before any controls
root = tk.Tk()
root.title("Rounded Rectangular Menu")
root.overrideredirect(True)  # Remove window decorations
root.attributes("-topmost", True)  # Keep window always on top
root.attributes("-transparentcolor", background_color)
root.configure(bg=background_color, highlightthickness=0)

# Load configuration first
load_config()  # Add this line to load saved apps

# Load images 
load_all_images()

# Load each image with subsample for arrows
images['leftarrow'] = tk.PhotoImage(file=get_asset_path("assets/images/leftarrow.png")).subsample(25, 25)
images['rightarrow'] = tk.PhotoImage(file=get_asset_path("assets/images/rightarrow.png")).subsample(25, 25)



# Add this function before creating the canvas
# create rounded rectangle
# ----------------------------------------------------------------------------------
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
canvas = tk.Canvas(root, width=MENU_WIDTH, height=MENU_HEIGHT, bg=background_color, highlightthickness=0)
canvas.pack(pady=0)

radius = 25  # Adjust the radius for the desired roundness


# Draw shadow (slightly larger, offset, and semi-transparent dark color)
# ----------------------------------------------------------------------------------
shadow_color = "#0a0a0a"  # Very dark color for shadow
shadow_offset = 5  # Increased offset for more visible shadow
canvas.create_rounded_rect(
    shadow_offset, shadow_offset,  # Offset x, y
    MENU_WIDTH, MENU_HEIGHT,  # Original width and height
    radius,
    fill=shadow_color,
    outline=""
)

# Draw the outer border (dark border)
canvas.create_rounded_rect(0, 0, MENU_WIDTH, MENU_HEIGHT, radius, fill="#1a1a1a", outline="")

# Draw the inner background
canvas.create_rounded_rect(1, 1, MENU_WIDTH, MENU_HEIGHT, radius, fill="#222222", outline="")

# Create main container frame
main_container = tk.Frame(canvas, bg="#222222")
main_container.place(relx=0.5, rely=0, anchor="n", width=MENU_WIDTH, height=MENU_HEIGHT-50)


# Now create the controls
# ----------------------------------------------------------------------------------
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


# create top controls
# ----------------------------------------------------------------------------------
# Tooltip class
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.attributes("-topmost", True)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, background="#424242", foreground="lightgray", relief="solid", borderwidth=1,
            font=("tahoma", "10", "normal")
        )
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


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
                          fg="#ffffff",
                          insertbackground="#ffffff",
                          relief=tk.FLAT)
    search_entry.pack(side=tk.LEFT, padx=10, ipady=8)
    
    # Add placeholder text
    placeholder_text = "  Developed by Bibek___Search anything here (@youtube for YouTube)..."
    search_entry.insert(0, placeholder_text)
    search_entry.config(fg="grey")
    ToolTip(search_entry, f"@incognito, @youtube, @maps, @images, @amazon, @flipkart, @wiki, @wikihow, \n @github, @translate, @stackoverflow, @reddit, @quora, @medium, @linkedin, @twitter/@x, \n @news, @scholar, @weather, @duckduckgo, @spotify, @coursera, @udemy, @discord, \n @pinterest, @unsplash, @google")

    def on_focus_in(event):
        if search_entry.get() == placeholder_text:
            search_entry.delete(0, tk.END)
            search_entry.config(fg="#ffffff")

    def on_focus_out(event):
        if not search_entry.get():
            search_entry.insert(0, placeholder_text)
            search_entry.config(fg="grey")

    search_entry.bind("<FocusIn>", on_focus_in)
    search_entry.bind("<FocusOut>", on_focus_out)
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
    media_frame.pack(side=tk.LEFT, padx=10)
    
    return top_frame


# Add this function to control brightness
# ----------------------------------------------------------------------------------
def get_brightness():
    try:
        c = wmi.WMI(namespace='wmi')
        monitors = c.WmiMonitorBrightness()
        if monitors and len(monitors) > 0:
            return monitors[0].CurrentBrightness
        else:
            # No monitors found that support WMI brightness control
            return 50
    except wmi.x_wmi as e:
        # Handle specific WMI COM errors silently
        if "0x80041032" in str(e):
            # This is a common error when WMI can't access brightness
            # Just log at debug level to avoid filling logs
            logging.debug(f"WMI brightness access not available: {e}")
        else:
            logging.error(f"WMI error getting brightness: {e}")
        return 50
    except Exception as e:
        logging.error(f"Error getting brightness: {e}")
        print(f"Error getting brightness: {e}")
        return 50


# def set_brightness(value):
#     try:
#         c = wmi.WMI(namespace='wmi')
#         monitors = c.WmiMonitorBrightnessMethods()
#         monitors[0].WmiSetBrightness(value, 0)
#         return True
#     except Exception as e:
#         logging.error(f"Error setting brightness: {e}")
#         print(f"Error setting brightness: {e}")
#         return False

def set_brightness(value):
    try:
        c = wmi.WMI(namespace='wmi')
        monitors = c.WmiMonitorBrightnessMethods()
        if monitors and len(monitors) > 0:
            monitors[0].WmiSetBrightness(value, 0)
            return True
        else:
            # No monitors found that support WMI brightness control
            return False
    except wmi.x_wmi as e:
        # Handle specific WMI COM errors silently
        if "0x80041032" in str(e):
            # This is a common error when WMI can't access brightness
            logging.debug(f"WMI brightness control not available: {e}")
        else:
            logging.error(f"WMI error setting brightness: {e}")
        return False
    except Exception as e:
        logging.error(f"Error setting brightness: {e}")
        print(f"Error setting brightness: {e}")
        return False


# listen for shortcuts for brightness
# ----------------------------------------------------------------------------------
# def listen_for_shortcuts():
#     """
#     Listen for global keyboard shortcuts to adjust brightness.
#     """
#     shortcuts = load_shortcuts()
#     register_hotkeys(shortcuts)

#     # Add a watchdog timer to periodically refresh shortcuts
#     def refresh_shortcuts():
#         try:
#             kb.clear_all_hotkeys()
#             register_hotkeys(shortcuts)
#             logging.info("Shortcuts refreshed successfully.")
#             print("Shortcuts refreshed successfully.")
#         except Exception as e:
#             logging.error(f"Error refreshing shortcuts: {e}")
#             show_notification(APP_NAME, f"Error refreshing shortcuts: {e}")
#             print(f"Error refreshing shortcuts: {e}")

#         # Schedule the next refresh after 1 hour (3600000 ms)
#         root.after(3600000, refresh_shortcuts)

#     # Start the watchdog timer
#     root.after(3600000, refresh_shortcuts)

#     kb.wait()


# create menu controls
# ----------------------------------------------------------------------------------
def create_menu_controls(parent):
    menu_frame = tk.Frame(parent, bg="#222222")
    
    # Create a canvas with scrollbar for icons
    canvas = tk.Canvas(menu_frame, bg="#222222", height=120, highlightthickness=0)
    canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # Create scrollbar but don't pack it yet
    scrollbar = tk.Scrollbar(menu_frame, orient="horizontal", command=canvas.xview)
    
    canvas.configure(xscrollcommand=scrollbar.set)
    
    # Create a frame inside the canvas to hold all the controls
    icons_frame = tk.Frame(canvas, bg="#222222")
    canvas_window = canvas.create_window((0, 0), window=icons_frame, anchor="nw")
    
    # Create a container frame for the icons to allow centering
    icons_container = tk.Frame(icons_frame, bg="#222222")
    icons_container.pack(expand=True)
    
    # Create individual frames for each control
    shutdown_control = tk.Frame(icons_container, bg="#222222")
    restart_control = tk.Frame(icons_container, bg="#222222")
    desktop_control = tk.Frame(icons_container, bg="#222222")
    taskview_control = tk.Frame(icons_container, bg="#222222")
    lock_control = tk.Frame(icons_container, bg="#222222")
    brightness_control = tk.Frame(icons_container, bg="#222222")
    calculator_control = tk.Frame(icons_container, bg="#222222")
    screenshot_control = tk.Frame(icons_container, bg="#222222")
    homepage_control = tk.Frame(icons_container, bg="#222222")
    
    # Function to get brightness icon and next level
    def get_brightness_info():
        current_brightness = get_brightness()
        if current_brightness == 0 or current_brightness < 25:
            return 'brightness0', "Brightness-25"
        elif current_brightness >= 25 and current_brightness < 50:
            return 'brightness25', "Brightness-50"
        elif current_brightness >= 50 and current_brightness < 75:
            return 'brightness50', "Brightness-75"
        elif current_brightness >= 75 and current_brightness < 100:
            return 'brightness75', "Brightness-100"
        elif current_brightness == 100:
            return 'brightness100', "Brightness-0"
        else:
            return 'brightness35', "Brightness-35"
    
    # Function to cycle through brightness levels
    def cycle_brightness():
        current = get_brightness()
        if current == 0 or current < 25:
            set_brightness(25)
        elif current >= 25 and current < 50:
            set_brightness(50)
        elif current >= 50 and current < 75:
            set_brightness(75)
        elif current >= 75 and current < 100:
            set_brightness(100)
        elif current == 100:
            set_brightness(0)
        else:
            set_brightness(35)
        
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
    # camera_btn = tk.Button(camera_control, image=images['camera'], command=open_camera,
    #                      bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    # cameraoff_btn = tk.Button(cameraoff_control, image=images['cameraoff'], command=open_camera_off,
    #                      bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    
    # Get initial brightness icon and label
    icon_name, label_text = get_brightness_info()
    brightness_btn = tk.Button(brightness_control, image=images[icon_name], command=cycle_brightness,
                         bg="#222222", activebackground="#333333", bd=0, cursor="hand2")
    
    # Create labels with click functionality
    shutdown_label = tk.Label(shutdown_control, text="Shutdown", fg="lightgray",
                          bg="#222222", font=("Arial", 10), cursor="hand2")
    shutdown_label.bind("<Button-1>", lambda e: shut_down())
    
    restart_label = tk.Label(restart_control, text="Restart", fg="lightgray",
                          bg="#222222", font=("Arial", 10), cursor="hand2")
    restart_label.bind("<Button-1>", lambda e: restart())
    
    desktop_label = tk.Label(desktop_control, text="S/H Desktop", fg="lightgray",
                          bg="#222222", font=("Arial", 10), cursor="hand2")
    desktop_label.bind("<Button-1>", lambda e: show_desktop())
    
    taskview_label = tk.Label(taskview_control, text="Task View", fg="lightgray",
                          bg="#222222", font=("Arial", 10), cursor="hand2")
    taskview_label.bind("<Button-1>", lambda e: task_view())
    
    lock_label = tk.Label(lock_control, text="Lock Screen", fg="lightgray",
                          bg="#222222", font=("Arial", 10), cursor="hand2")
    lock_label.bind("<Button-1>", lambda e: lock_screen())
    
    calculator_label = tk.Label(calculator_control, text="Calculator", fg="lightgray",
                          bg="#222222", font=("Arial", 10), cursor="hand2")
    calculator_label.bind("<Button-1>", lambda e: open_calculator())
    
    brightness_label = tk.Label(brightness_control, text=label_text, fg="lightgray",
                          bg="#222222", font=("Arial", 10), cursor="hand2")
    brightness_label.bind("<Button-1>", lambda e: cycle_brightness())
    
    screenshot_label = tk.Label(screenshot_control, text="Screenshot", fg="lightgray",
                          bg="#222222", font=("Arial", 10), cursor="hand2")
    screenshot_label.bind("<Button-1>", lambda e: take_screenshot())
    
    homepage_label = tk.Label(homepage_control, text="Homepage", fg="lightgray",
                          bg="#222222", font=("Arial", 10), cursor="hand2")
    homepage_label.bind("<Button-1>", lambda e: open_homepage())
    
    # camera_label = tk.Label(camera_control, text="Camera", fg="lightgray",
    #                       bg="#222222", font=("Arial", 10), cursor="hand2")
    # cameraoff_label = tk.Label(cameraoff_control, text="Camera Off", fg="lightgray",
    #                       bg="#222222", font=("Arial", 10), cursor="hand2")
    
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
    # camera_btn.image = images['camera']
    # cameraoff_btn.image = images['cameraoff']

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
    # camera_btn.pack(pady=(2, 0))
    # camera_label.pack(pady=(0, 2))
    # cameraoff_btn.pack(pady=(2, 0))
    # cameraoff_label.pack(pady=(0, 2))

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
    # camera_control.pack(side=tk.LEFT, padx=10)
    # cameraoff_control.pack(side=tk.LEFT, padx=10)
    
    # Update canvas scrollregion after all controls are added
    def update_scrollregion(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Get the width of all icons
        icons_width = icons_container.winfo_reqwidth()
        canvas_width = canvas.winfo_width()
        
        # Center the icons if they don't fill the canvas
        if icons_width < canvas_width:
            # Calculate the x position to center the icons
            x_position = (canvas_width - icons_width) / 2
            canvas.coords(canvas_window, x_position, 0)
            
            # Hide scrollbar if not needed
            scrollbar.pack_forget()
        else:
            # If icons are wider than canvas, align to left
            canvas.coords(canvas_window, 0, 0)
            
            # Show scrollbar if needed
            # scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            scrollbar.pack_forget()
            
        # Set canvas width to match parent frame
        canvas.config(width=parent.winfo_width() - 20)  # Subtract some padding
    
    # Bind to configure event to update scrollregion when size changes
    icons_frame.bind("<Configure>", update_scrollregion)
    canvas.bind("<Configure>", update_scrollregion)
    
    # Add mousewheel scrolling
    def on_mousewheel(event):
        canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
    
    # Bind mousewheel to canvas and all child widgets
    canvas.bind("<MouseWheel>", on_mousewheel)
    
    # Recursive function to bind mousewheel to all children
    def bind_mousewheel_recursive(widget):
        widget.bind("<MouseWheel>", on_mousewheel)
        for child in widget.winfo_children():
            bind_mousewheel_recursive(child)
    
    bind_mousewheel_recursive(icons_frame)
    
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


# Create page frames
main_page_frame = tk.Frame(main_container, bg="#222222")
second_page_frame = tk.Frame(main_container, bg="#222222")
third_page_frame = tk.Frame(main_container, bg="#222222")  # Add this with other page variables

# create first page
# ----------------------------------------------------------------------------------
# Update the create_first_page function
def create_first_page(parent):
    first_page = tk.Frame(parent, bg="#222222")
    
    # Create a context menu for the page
    context_menu = create_context_menu(first_page)
    # Bind right-click to show the context menu
    first_page.bind("<Button-3>", lambda event: show_context_menu(event, context_menu))
    
    # Create and pack top controls (search + media)
    top_controls = create_top_controls(first_page)
    top_controls.pack(pady=10, fill=tk.X)
    
    # Create and pack main menu controls (shutdown, restart, etc)
    menu_controls = create_menu_controls(first_page)
    menu_controls.pack(pady=10)
    
    return first_page



# Update window geometry
# ----------------------------------------------------------------------------------
window_width = MENU_WIDTH
window_height = MENU_HEIGHT
position_top = 0
# Update window position calculation
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_right = int(screen_width / 2 - window_width / 2)
root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
# Update the initial setup to hide the window
root.withdraw()  # Hide the window initially


# Add this after creating the root window and before any UI elements
# ----------------------------------------------------------------------------------
# Create and configure ttk style for scrollbars
style = ttk.Style()
style.theme_create('custom_style', parent='alt', settings={
    'Horizontal.TScrollbar': {
        'configure': {
            'background': '#222222',          # Scrollbar background
            'troughcolor': '#333333',         # Trough/track color
            'borderwidth': 0,                 # Remove border
            'relief': 'flat',                 # Flat appearance
            'arrowsize': 0,                   # Remove arrows
        },
        'map': {
            'background': [('active', '#444444'),     # Hover color
                         ('pressed', '#444444')],     # Pressed color
            'darkcolor': [('pressed', '#444444')],    # Corner color when pressed
            'lightcolor': [('pressed', '#444444')],   # Corner color when pressed
        }
    },
    'Vertical.TScrollbar': {                 # Add vertical scrollbar styling
        'configure': {
            'background': '#222222',          # Scrollbar background
            'troughcolor': '#333333',         # Trough/track color
            'borderwidth': 0,                 # Remove border
            'relief': 'flat',                 # Flat appearance
            'arrowsize': 0,                   # Remove arrows
        },
        'map': {
            'background': [('active', '#444444'),     # Hover color
                         ('pressed', '#444444')],     # Pressed color
            'darkcolor': [('pressed', '#444444')],    # Corner color when pressed
            'lightcolor': [('pressed', '#444444')],   # Corner color when pressed
        }
    }
})
style.theme_use('custom_style')

# Configure specific scrollbar style elements
style.configure('Horizontal.TScrollbar', 
    gripcount=0,               # Remove the grip/ridges
    background='#222222',      # Match frame background
    darkcolor='#222222',       # Corner color
    lightcolor='#222222',      # Corner color
    troughcolor='#333333',     # Track color
    bordercolor='#222222',     # Border color
    arrowcolor='#222222'       # Arrow color
)

# Add vertical scrollbar configuration
style.configure('Vertical.TScrollbar', 
    gripcount=0,               # Remove the grip/ridges
    background='#222222',      # Match frame background
    darkcolor='#222222',       # Corner color
    lightcolor='#222222',      # Corner color
    troughcolor='#333333',     # Track color
    bordercolor='#222222',     # Border color
    arrowcolor='#222222'       # Arrow color
)






# Add this before creating the app_launcher
# initialize_ui is used to initialize the UI elements after everything is created
# ----------------------------------------------------------------------------------
def initialize_ui():
    """Initialize UI elements after everything is created"""
    if update_app_buttons_ref:
        update_app_buttons_ref()
        logging.info("Initializing UI with saved apps")
        print("Initializing UI with saved apps")
    else:
        logging.warning("Warning: update_app_buttons_ref not initialized")
        print("Warning: update_app_buttons_ref not initialized")

# second page content starts here 👇
# ----------------------------------------------------------------------------------
# Move this function AFTER the create_first_page function and BEFORE the create_second_page function

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
        else:
            show_notification(APP_NAME, "App name not provided")
            logging.warning("Warning: App name not provided")
            print("Warning: App name not provided")

def remove_app():
    # Create a dialog to select app to remove
    if not user_apps:
        messagebox.showinfo("Remove App", "No applications to remove.")
        show_notification(APP_NAME, "No applications to remove")
        logging.info("No applications to remove")
        print("No applications to remove")
        return
        
    app_to_remove = simpledialog.askstring("Remove App", 
        "Enter the name of the app to remove:",
        initialvalue=list(user_apps.keys())[0])
        
    if app_to_remove in user_apps:
        del user_apps[app_to_remove]
        save_config()
        if update_app_buttons_ref:
            update_app_buttons_ref()
        show_notification(APP_NAME, f"Removed {app_to_remove}")
        logging.info(f"Removed {app_to_remove}")
        print(f"Removed {app_to_remove}")
    else:
        show_notification(APP_NAME, "App not found")
        logging.warning("Warning: App not found")
        print("Warning: App not found")

def initialize_app_launcher():
    """Initialize the app launcher with stored applications"""
    if update_app_buttons_ref:
        update_app_buttons_ref()
    else:
        logging.warning("update_app_buttons_ref not initialized")
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
    scrollbar = ttk.Scrollbar(launcher_frame, orient="horizontal", command=canvas.xview)
    scrollable_frame = tk.Frame(canvas, bg="#222222")

    canvas.configure(xscrollcommand=scrollbar.set)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        
    # Add mouse wheel scrolling
    def on_mousewheel(event):
        # Scroll horizontally with the mouse wheel
        canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"  # Prevent event propagation
    
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
    # hide scrollbar
    # scrollbar.pack_forget()

    # Control frame stays fixed on right
    control_frame = tk.Frame(launcher_frame, bg="#222222")
    control_frame.pack(side=tk.RIGHT, padx=(5, 0))

    def update_app_buttons():
        # Clear existing buttons
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        
        # Create buttons for each app with wrapping
        row_frame = None
        buttons_per_row = 8
        current_row = []
        
        # Create a copy of user_apps to avoid potential modification during iteration
        apps_to_display = user_apps.copy()
        
        for name, path in apps_to_display.items():
            if len(current_row) >= buttons_per_row:
                current_row = []
                
            if not current_row:
                row_frame = tk.Frame(scrollable_frame, bg="#222222")
                row_frame.pack(fill=tk.X, pady=2)
                # Bind mousewheel to row frame
                row_frame.bind("<MouseWheel>", on_mousewheel)
                
            # Use a lambda with default argument to avoid late binding issues
            btn = tk.Button(row_frame, text=name,
                          command=lambda p=path: launch_app(p),
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

    # Add this function to launch apps in a separate thread
    def launch_app(path):
        def _launch():
            try:
                # Get the directory of the application
                app_dir = os.path.dirname(path)
                
                # Use subprocess.Popen instead of os.startfile to set the working directory
                if app_dir:
                    subprocess.Popen(path, cwd=app_dir)
                else:
                    # If there's no directory (just a filename), use os.startfile
                    os.startfile(path)
                    
                logging.info(f"Launched application: {path}")
                print(f"Launched application: {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to launch application: {e}")
                logging.error(f"Error launching app {path}: {e}")
                print(f"Error launching app {path}: {e}")

        # Launch in a separate thread to prevent UI freezing
        threading.Thread(target=_launch, daemon=True).start()

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


# swithch window
# ----------------------------------------------------------------------------------
def close_window():
    global selected_window_title
    if selected_window_title:
        window = gw.getWindowsWithTitle(selected_window_title)
        if window:
            window[0].close()
        selected_window_title = None  # Clear the selection after closing

def minimize_window():
    global selected_window_title
    if selected_window_title:
        window = gw.getWindowsWithTitle(selected_window_title)
        if window:
            window[0].minimize()

def maximize_window():
    global selected_window_title
    if selected_window_title:
        window = gw.getWindowsWithTitle(selected_window_title)
        if window:
            window[0].maximize()

def restart_window():
    global selected_window_title
    if selected_window_title:
        window = gw.getWindowsWithTitle(selected_window_title)
        if window:
            try:
                # Use psutil to find the process with the matching window title
                import psutil
                for proc in psutil.process_iter(['pid', 'name', 'exe']):
                    try:
                        if selected_window_title.lower() in proc.info['name'].lower():
                            executable_path = proc.info['exe']
                            # Close the window
                            window[0].close()
                            # Restart the application
                            subprocess.Popen(executable_path)
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue
            except Exception as e:
                print(f"Error restarting window: {e}")


def list_open_windows_window():
    global selected_window_title
    
    # Check if window list is already open
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and hasattr(widget, 'windows_list_window'):
            return  # Window list already open
    
    def refresh_window_list():
        global selected_window_title
        windows = gw.getAllTitles()
        
        # Save current scroll position and selection
        current_scroll_pos = window_list.yview()[0]
        current_selection = None
        if window_list.curselection():
            current_selection = window_list.get(window_list.curselection())
        
        window_list.delete(0, tk.END)  # Clear the listbox
        
        # Get search term and handle placeholder text
        search_text = search_var.get()
        if search_text == 'Search window name here...':
            search_term = ''  # Ignore the placeholder text
        else:
            search_term = search_text.lower().strip()
            
        # Filter and sort the window titles
        filtered_windows = []
        for window in windows:
            if window.strip() and window not in ["Windows Input Experience", "Realtek Audio Console", "Program Manager", "Widgets", "PopupHost"]:
                if search_term == '' or search_term in window.lower():
                    filtered_windows.append(window)
        
        # Sort the filtered windows
        filtered_windows.sort()
        
        # Add filtered windows to listbox
        selection_index = None
        for i, window in enumerate(filtered_windows):
            window_list.insert(tk.END, window)
            # Track index of previously selected window or current selection
            if window == selected_window_title or window == current_selection:
                selection_index = i
                
        # Restore selection if found
        if selection_index is not None:
            window_list.selection_clear(0, tk.END)
            window_list.selection_set(selection_index)
            
            # Only scroll to make selection visible if it's not already in view
            visible_range = window_list.yview()
            item_position = selection_index / window_list.size()
            
            # Check if the selected item is already visible in the current view
            if item_position < visible_range[0] or item_position > visible_range[1]:
                # Only then make it visible, but don't center it
                window_list.see(selection_index)
            else:
                # If already visible, maintain the current scroll position
                window_list.yview_moveto(current_scroll_pos)
        else:
            # Restore scroll position if no selection to focus on
            window_list.yview_moveto(current_scroll_pos)
                
        # Schedule the function to run again after 1000 milliseconds (1 second)
        windows_dialog.after(1000, refresh_window_list)

    def activate_window(event):
        global selected_window_title
        try:
            # Only proceed if there's a selection
            if window_list.curselection():
                selected_window_title = window_list.get(window_list.curselection())
                window = gw.getWindowsWithTitle(selected_window_title)
                if window:
                    # Restore the window if it's minimized
                    if window[0].isMinimized:
                        window[0].restore()
                    # Activate the window
                    window[0].activate()
        except Exception as e:
            print(f"Error activating window: {e}")
    
    def show_context_menu(event):
        global selected_window_title
        try:
            # Prevent the main menu from disappearing by grabbing and releasing focus
            root.grab_set()
            root.grab_release()

            
            # Select the item under the cursor
            window_list.selection_clear(0, tk.END)
            index = window_list.nearest(event.y)
            window_list.selection_set(index)
            selected_window_title = window_list.get(index)
            context_menu.post(event.x_root, event.y_root)
        except tk.TclError:
            pass  # Handle the case where no item is under the cursor

    def on_entry_click(event):
        """Function that gets called whenever entry is clicked"""
        if search_var.get() == 'Search window name here...':
            search_entry.delete(0, "end")  # delete all the text in the entry
            search_entry.insert(0, '')  # Insert blank for user input
            search_entry.config(fg='white')

    def on_focusout(event):
        """Function that gets called whenever entry loses focus"""
        if search_var.get() == '':
            search_entry.delete(0, "end")
            search_entry.insert(0, 'Search window name here...')
            search_entry.config(fg='grey')
    
    def on_search_change(*args):
        refresh_window_list()
    
    # Find the list_open_windows_widget button to position the window below it
    list_open_windows_widget = None
    
    def find_button(parent):
        """Recursively search for the List Open Windows button"""
        nonlocal list_open_windows_widget
        if list_open_windows_widget:
            return
            
        for widget in parent.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget('text') == "List Open Windows":
                list_open_windows_widget = widget
                return
            if hasattr(widget, 'winfo_children'):
                find_button(widget)
    
    # Start the recursive search from root
    find_button(root)
    
    if not list_open_windows_widget:
        # Fallback to creating a regular window if button not found
        windows_dialog = tk.Tk()
        windows_dialog.title("Open Windows")
        windows_dialog.geometry("500x300")
    else:
        # Create a new toplevel window
        windows_dialog = tk.Toplevel(root)
        windows_dialog.windows_list_window = True  # Mark as windows list window
        windows_dialog.title("Open Windows")
        windows_dialog.overrideredirect(True)  # Remove window decorations
        
        # Calculate position to show below the button
        x = list_open_windows_widget.winfo_rootx() - 150  # Center horizontally with the button
        y = list_open_windows_widget.winfo_rooty() + list_open_windows_widget.winfo_height() + 5  # Position below with 5px gap
        
        # Ensure window stays within screen bounds
        screen_height = root.winfo_screenheight()
        if y + 300 > screen_height:  # If window would go off screen bottom
            y = list_open_windows_widget.winfo_rooty() - 300 - 5  # Show above instead
        
        windows_dialog.geometry(f"500x300+{x}+{y}")
    
    windows_dialog.configure(bg="#222222")  # Set dark background color
    windows_dialog.attributes('-topmost', True)

    # Create a frame to hold the search bar, refresh button, listbox, and scrollbar
    frame = tk.Frame(windows_dialog, bg="#222222")
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Create a search bar
    search_var = tk.StringVar()
    search_entry = tk.Entry(frame, textvariable=search_var, fg='grey', bg="#333333", insertbackground='white')
    search_entry.insert(0, 'Search window name here...')  # Set initial placeholder text
    search_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    search_entry.bind('<FocusIn>', on_entry_click)
    search_entry.bind('<FocusOut>', on_focusout)
    
    # Make the search variable trigger refresh when it changes
    search_var.trace_add("write", on_search_change)

    # Create a button to refresh the list of open windows
    refresh_button = tk.Button(frame, text="Refresh", command=refresh_window_list, bg="#333333", fg="#ffffff", activebackground="#4e4e4e")
    refresh_button.grid(row=0, column=1, padx=5, pady=5)
    
    # Create a listbox to display the open windows
    window_list = tk.Listbox(frame, bg="#333333", fg="#ffffff", selectbackground="#4e4e4e", selectforeground="#ffffff", font=("Arial", 10))
    window_list.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
    window_list.bind('<Double-Button-1>', activate_window)  # double click to activate window
    window_list.bind('<<ListboxSelect>>', activate_window)  # click to activate window
    window_list.bind('<Button-3>', show_context_menu)  # Right-click
    
    # Add mousewheel binding to prevent event propagation
    def on_mousewheel(event):
        # Scroll the listbox
        if event.delta > 0:
            window_list.yview_scroll(-2, "units")
        else:
            window_list.yview_scroll(2, "units")
        # Stop event propagation
        return "break"
    
    # Bind mousewheel events for Windows
    window_list.bind("<MouseWheel>", on_mousewheel)
    # Bind mousewheel events for Linux
    window_list.bind("<Button-4>", on_mousewheel)
    window_list.bind("<Button-5>", on_mousewheel)
    
    # Prevent event propagation for the entire dialog
    windows_dialog.bind("<MouseWheel>", lambda e: "break")
    windows_dialog.bind("<Button-4>", lambda e: "break")
    windows_dialog.bind("<Button-5>", lambda e: "break")
    
    # Create a ttk scrollbar and attach it to the listbox
    style = ttk.Style()
    style.theme_use('clam')  # Use 'clam' theme for better customization
    style.configure("Vertical.TScrollbar", background="#333333", troughcolor="#222222", bordercolor="#222222", arrowcolor="#ffffff")
    
    # Create a scrollbar for the listbox
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=window_list.yview)
    scrollbar.grid(row=1, column=2, sticky="ns", pady=5)
    window_list.config(yscrollcommand=scrollbar.set)
    
    # Create a context menu for the listbox
    context_menu = tk.Menu(window_list, tearoff=0, bg="#333333", fg="#ffffff")
    context_menu.add_command(label="Minimize", command=minimize_window)
    context_menu.add_command(label="Maximize", command=maximize_window)
    context_menu.add_command(label="Close", command=close_window)
    context_menu.add_command(label="Restart", command=restart_window)
    
    # Bind right-click to show the context menu
    window_list.bind("<Button-3>", show_context_menu)
    
    # Configure grid weights for resizing
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=0)
    
    # Add close button
    close_btn = tk.Button(frame, text="Close",
                        command=windows_dialog.destroy,
                        bg="#333333", fg="white",
                        activebackground="#444444",
                        activeforeground="white")
    close_btn.grid(row=2, column=0, columnspan=2, pady=5)
    
    # Use a more efficient approach for tracking mouse position
    def check_mouse_position():
        if not windows_dialog.winfo_exists():
            return
        
        mouse_x = windows_dialog.winfo_pointerx()
        mouse_y = windows_dialog.winfo_pointery()
        
        # Check if mouse is over windows dialog
        win_x = windows_dialog.winfo_x()
        win_y = windows_dialog.winfo_y()
        win_width = windows_dialog.winfo_width()
        win_height = windows_dialog.winfo_height()
        
        # Check if mouse is over the button
        if list_open_windows_widget:
            btn_x = list_open_windows_widget.winfo_rootx()
            btn_y = list_open_windows_widget.winfo_rooty()
            btn_width = list_open_windows_widget.winfo_width()
            btn_height = list_open_windows_widget.winfo_height()
            
            # If mouse is over either windows dialog or button, keep open
            if ((win_x <= mouse_x <= win_x + win_width and 
                win_y <= mouse_y <= win_y + win_height) or
                (btn_x <= mouse_x <= btn_x + btn_width and 
                btn_y <= mouse_y <= btn_y + btn_height)):
                windows_dialog.after(200, check_mouse_position)  # Check less frequently
            else:
                windows_dialog.destroy()
        else:
            # If button not found, just check if mouse is over dialog
            if (win_x <= mouse_x <= win_x + win_width and 
                win_y <= mouse_y <= win_y + win_height):
                windows_dialog.after(200, check_mouse_position)
            else:
                windows_dialog.destroy()
    
    # Start checking mouse position
    windows_dialog.after(200, check_mouse_position)
    
    # Populate the listbox with open windows initially and set up auto-refresh
    refresh_window_list()



# volume mixer
# ----------------------------------------------------------------------------------
def update_volume_sliders():
    global sliders

    # Get all active audio sessions
    sessions = AudioUtilities.GetAllSessions()
    
    # Track active process IDs in this update cycle
    active_pids = set()

    # Loop through each session to update or add sliders
    for session in sessions:
        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        process = session.Process

        if process:
            app_name = process.name()
            if app_name == "ShellExperienceHost.exe":
                app_name = "Volume Mixer"
            pid = process.pid  # Unique ID for each process to track sliders

            # Mark this PID as active
            active_pids.add(pid)

            # If this application does not have a slider yet, create one
            if pid not in sliders:
                row = len(sliders) + 1  # Offset by 1 to leave space for system volume

                # Create a label with the application name
                label = ttk.Label(scrollable_frame, text=app_name, font=("Helvetica", 10), style="TLabel")
                label.grid(row=row, column=0, padx=5, pady=5)

                # Create a label to show the volume percentage
                volume_value_label = ttk.Label(scrollable_frame, text=f"{int(volume.GetMasterVolume() * 100)}%", style="TLabel")
                volume_value_label.grid(row=row, column=2, padx=5, pady=5)

                # Create a modern volume slider for the application
                volume_slider = ttk.Scale(scrollable_frame, from_=0, to=100, orient='horizontal',
                                          style="TScale",
                                          command=lambda v, vol=volume, lbl=volume_value_label: set_volume(vol, v, lbl))
                volume_slider.set(volume.GetMasterVolume() * 100)  # Set current volume level
                volume_slider.grid(row=row, column=1, padx=10, pady=10, sticky="ew")

                # Bind mouse scroll to adjust volume on scroll
                volume_slider.bind("<MouseWheel>", lambda e, vol_slider=volume_slider: scroll_volume(e, vol_slider))

                # Store the slider, label, volume value label, and volume control by PID
                sliders[pid] = (label, volume_slider, volume_value_label, volume)

            else:
                # If the application slider already exists, update the slider position and value label
                _, volume_slider, volume_value_label, _ = sliders[pid]
                current_volume = volume.GetMasterVolume() * 100
                if volume_slider.get() != current_volume:
                    volume_slider.set(current_volume)
                    volume_value_label.config(text=f"{int(current_volume)}%")

    # Remove sliders and labels for applications that have stopped
    for pid in list(sliders.keys()):
        if pid not in active_pids:
            # Application is no longer active, so destroy its label and slider
            label, volume_slider, volume_value_label, _ = sliders.pop(pid)
            label.destroy()          # Completely removes the label
            volume_slider.destroy()   # Completely removes the slider
            volume_value_label.destroy()  # Completely removes the volume value label

    # Schedule the next update after a delay (e.g., 1000 ms or 1 second)
    volume_mixer_window.after(1000, update_volume_sliders)

def set_volume(volume_control, volume_level, volume_value_label):
    # Convert the volume level to a float, then set it to the volume control
    volume_level = float(volume_level)  # Ensure volume_level is a float
    volume_control.SetMasterVolume(volume_level / 100.0, None)
    
    # Update the volume value label with an integer percentage
    volume_value_label.config(text=f"{int(volume_level)}%")

def scroll_volume(event, volume_slider):
    """Adjust the slider's value based on mouse scroll direction."""
    current_value = volume_slider.get()
    step = 2  # Amount to increase/decrease the volume per scroll

    if event.delta > 0:  # Scroll up
        new_value = min(100, current_value + step)
    else:  # Scroll down
        new_value = max(0, current_value - step)

    # Update the slider position and trigger the set_volume method to apply the volume change
    volume_slider.set(new_value)

def show_volume_mixer(event=None):
    global volume_mixer_window, scrollable_frame, canvas, volume_mixer_visible
    
    # Toggle the volume mixer window if it's already visible
    if volume_mixer_visible:
        volume_mixer_window.destroy()
        volume_mixer_visible = False
        return
    
    volume_mixer_visible = True
    
    # Find the volume mixer button to position the window below it
    volume_mixer_button = None
    
    def find_button(parent):
        """Recursively search for the Volume Mixer button"""
        nonlocal volume_mixer_button
        if volume_mixer_button:
            return
            
        for widget in parent.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget('text') == "Volume Mixer":
                volume_mixer_button = widget
                return
            if hasattr(widget, 'winfo_children'):
                find_button(widget)
    
    # Start the recursive search from root
    find_button(root)
    
    # Create the window
    volume_mixer_window = tk.Toplevel(root)
    volume_mixer_window.title("Application Volume Adjuster")
    volume_mixer_window.configure(background="#222222", highlightthickness=0, bd=0)
    volume_mixer_window.overrideredirect(True)  # Remove window decorations
    volume_mixer_window.attributes('-topmost', True)
    
    # Calculate position based on the button
    if volume_mixer_button:
        x = volume_mixer_button.winfo_rootx() - 150  # Center horizontally with the button
        y = volume_mixer_button.winfo_rooty() + volume_mixer_button.winfo_height() + 5  # Position below with 5px gap
        
        # Ensure window stays within screen bounds
        screen_height = root.winfo_screenheight()
        if y + 400 > screen_height:  # If window would go off screen bottom
            y = volume_mixer_button.winfo_rooty() - 400 - 5  # Show above instead
    else:
        # Fallback positioning if button not found
        x = root.winfo_rootx() + (root.winfo_width() // 2) - 150
        y = root.winfo_rooty() + (root.winfo_height() // 2)
    
    # Position the window
    volume_mixer_window.geometry(f"350x300+{x}+{y}")
    
    # Initialize the style for a modern slider with a light transparent background
    style = ttk.Style()
    style.configure("TScale",
                    troughcolor="#444444",   # Light background for track
                    sliderthickness=12)      # Thickness of the slider button
    style.map("TScale",
              sliderrelief=[("active", "groove")],  # Hover effect
              background=[("active", "#0078D4")])   # Color of slider when active

    # Configure style for labels
    style.configure("TLabel", background="#222222", foreground="#d2d2d2")

    # Create a canvas and scrollbar to make the window scrollable
    canvas = tk.Canvas(volume_mixer_window, background="#222222", highlightthickness=0, bd=0)
    scrollbar = ttk.Scrollbar(volume_mixer_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas, style="TFrame")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    
    # Configure button style
    style = ttk.Style()
    style.configure("TButton",
                    background="#222222",
                    foreground="#d2d2d2",
                    font=("Helvetica", 12))
    
    # Configure style for the main application window
    style.configure("TFrame", background="#222222")

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Add system volume control at the top
    add_system_volume_control(scrollable_frame)

    # Dictionary to hold the labels and sliders for each application by process ID
    global sliders
    sliders = {}

    # Start the UI update loop
    update_volume_sliders()
    
    # Bind mouse scroll to the canvas to enable scrolling when outside of volume_value_label and volume_slider
    # canvas.bind_all("<MouseWheel>", on_mouse_wheel)
    
    # Add event to close the window when clicking outside
    def on_focus_out(event):
        if event.widget == volume_mixer_window:
            volume_mixer_window.destroy()
            global volume_mixer_visible
            volume_mixer_visible = False
    
    volume_mixer_window.bind("<FocusOut>", on_focus_out)
    
    # Add event to close the window when Escape key is pressed
    volume_mixer_window.bind("<Escape>", lambda e: volume_mixer_window.destroy())
    
    # Bind to window close event
    volume_mixer_window.protocol("WM_DELETE_WINDOW", lambda: setattr(sys.modules[__name__], 'volume_mixer_visible', False))

    # Function to check if mouse is over the button or the mixer window
    def check_mouse_position():
        global volume_mixer_visible
        if not volume_mixer_visible:
            return
            
        # Get current mouse position
        mouse_x, mouse_y = root.winfo_pointerxy()
        
        # Check if mouse is over the volume mixer window
        win_x = volume_mixer_window.winfo_rootx()
        win_y = volume_mixer_window.winfo_rooty()
        win_width = volume_mixer_window.winfo_width()
        win_height = volume_mixer_window.winfo_height()
        
        in_window = (win_x <= mouse_x <= win_x + win_width and 
                     win_y <= mouse_y <= win_y + win_height)
        
        # Check if mouse is over the button
        btn_x = volume_mixer_button.winfo_rootx()
        btn_y = volume_mixer_button.winfo_rooty()
        btn_width = volume_mixer_button.winfo_width()
        btn_height = volume_mixer_button.winfo_height()
        
        in_button = (btn_x <= mouse_x <= btn_x + btn_width and 
                     btn_y <= mouse_y <= btn_y + btn_height)
        
        # Close if mouse is outside both
        if not in_window and not in_button:
            volume_mixer_window.destroy()
            volume_mixer_visible = False
            return
            
        # Continue checking if still visible
        if volume_mixer_visible:
            volume_mixer_window.after(200, check_mouse_position)
    
    # Start checking mouse position
    volume_mixer_window.after(500, check_mouse_position)  # Start after a short delay

# Add this at the beginning of your file or in the initialization section
volume_mixer_visible = False

def add_system_volume_control(frame):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    # Create a label for system volume
    label = ttk.Label(frame, text="System Volume", font=("Helvetica", 10), style="TLabel")
    label.grid(row=0, column=0, padx=5, pady=5)

    # Create a label to show the volume percentage
    volume_value_label = ttk.Label(frame, text=f"{int(volume.GetMasterVolumeLevelScalar() * 100)}%", style="TLabel")
    volume_value_label.grid(row=0, column=2, padx=5, pady=5)

    # Create a modern volume slider for system volume
    volume_slider = ttk.Scale(frame, from_=0, to=100, orient='horizontal',
                              style="TScale",
                              command=lambda v, vol=volume, lbl=volume_value_label: set_system_volume(vol, v, lbl))
    volume_slider.set(volume.GetMasterVolumeLevelScalar() * 100)  # Set current volume level
    volume_slider.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    # Bind mouse scroll to adjust volume on scroll
    volume_slider.bind("<MouseWheel>", lambda e, vol_slider=volume_slider: scroll_volume(e, vol_slider))

def set_system_volume(volume_control, volume_level, volume_value_label):
    # Convert the volume level to a float, then set it to the volume control
    volume_level = float(volume_level)  # Ensure volume_level is a float
    volume_control.SetMasterVolumeLevelScalar(volume_level / 100.0, None)
    
    # Update the volume value label with an integer percentage
    volume_value_label.config(text=f"{int(volume_level)}%")

# def on_mouse_wheel(event):
#     widget = event.widget
#     if not isinstance(widget, ttk.Scale) and not isinstance(widget, ttk.Label):
#         canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    

# keyboard shortcuts
# ----------------------------------------------------------------------------------
# Load saved shortcuts from config
# shortcuts_file = os.path.join(app_dir, "upmenushortcuts.json")

def load_shortcuts():
    """
    Load shortcuts from the JSON file.
    """
    try:
        with open(shortcuts_file, 'r') as file:
            shortcuts = json.load(file)
            # Ensure all keys are present
            for key, value in DEFAULT_SHORTCUTS.items():
                shortcuts.setdefault(key, value)
            return shortcuts
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        # Return default shortcuts if file not found or JSON is invalid
        logging.error(f"Error loading shortcuts: {e}")
        print(f"Error loading shortcuts: {e}")
        return DEFAULT_SHORTCUTS.copy()

def save_shortcuts(shortcuts):
    """
    Save shortcuts to the JSON file.
    """
    try:
        with open(shortcuts_file, 'w') as file:
            json.dump(shortcuts, file, indent=4)
    except Exception as e:
        logging.error(f"Error saving shortcuts: {e}")
        print(f"Error saving shortcuts: {e}")

def register_hotkeys(shortcuts):
    """
    Register global keyboard shortcuts.
    """
    actions = {
        "Show Hide Menu": on_activate_show_hide,
        "Take Screenshot": take_screenshot,
        "Open Calculator": open_calculator,
        "Open Homepage": open_homepage,
        "Restart Programs": restart_programs,
        "Toggle Brightness": toggle_brightness,
        "Toggle Keyboard": toggle_keyboard,
        
        # update the open_shortcut_editor function -> events and event_keys to use the new shortcuts
    }
    try:
        for key, action in actions.items():
            kb.add_hotkey(shortcuts[key], action)
        return True
    except Exception as e:
        logging.error(f"Error registering hotkey: {e}")
        show_notification(APP_NAME, f"Error registering hotkey: {e}")
        print(f"Error registering hotkey: {e}")
        return False

def listen_for_shortcuts():
    """
    Listen for global keyboard shortcuts to adjust brightness.
    """
    shortcuts = load_shortcuts()
    register_hotkeys(shortcuts)

    # Add a watchdog timer to periodically refresh shortcuts
    def refresh_shortcuts():
        try:
            kb.clear_all_hotkeys()
            register_hotkeys(shortcuts)
            logging.info("Shortcuts refreshed successfully.")
            # show_notification(APP_NAME, "Shortcuts refreshed successfully.")
            print("Shortcuts refreshed successfully.")
        except Exception as e:
            logging.error(f"Error refreshing shortcuts: {e}")
            show_notification(APP_NAME, f"Error refreshing shortcuts: {e}")
            print(f"Error refreshing shortcuts: {e}")

        # Schedule the next refresh after 1 hour (3600000 ms)
        root.after(3600000, refresh_shortcuts)

    # Start the watchdog timer
    root.after(3600000, refresh_shortcuts)  # First refresh after 1 hour

    kb.wait()


def open_shortcut_editor():
    """
    Open a dialog to edit keyboard shortcuts.
    """
    
    def edit_shortcut():
        # Get the selected action
        selected_index = event_listbox.curselection()
        if not selected_index:
            return

        action_name = events[selected_index[0]]
        current_key = keys[selected_index[0]]

        def save_shortcut():
            # Save the updated shortcut
            new_key = shortcut_entry.get()
            keys[selected_index[0]] = new_key
            shortcut_listbox.delete(selected_index[0])
            shortcut_listbox.insert(selected_index[0], new_key)
            save_shortcuts(dict(zip(event_keys, keys)))
            edit_window.destroy()
            logging.info("Shortcut updated.")
            show_notification(APP_NAME, "Shortcut updated.")
            print("Shortcut updated.")
            reload_shortcuts()

        # Create a new window for editing the selected shortcut
        edit_window = tk.Toplevel(editor_window)
        edit_window.title("Edit Shortcut")
        edit_window.geometry("300x150")
        edit_window.minsize(300, 150)
        edit_window.configure(bg="#333333")
        edit_window.iconbitmap(ICON_PATHH)
        # Get screen dimensions and position the window at the center
        screen_width = edit_window.winfo_screenwidth()
        screen_height = edit_window.winfo_screenheight()
        window_width, window_height = 300, 150  # Same as geometry
        position_x = (screen_width // 2) - (window_width // 2)
        position_y = (screen_height // 2) - (window_height // 2)
        edit_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

        tk.Label(edit_window, text=f"Action: {action_name}", bg="#333333", fg="white").pack(pady=5)
        shortcut_entry = tk.Entry(edit_window, bg="#222222", fg="white")
        # change the text cursor color to white
        shortcut_entry.config(insertbackground="white")
        shortcut_entry.insert(0, current_key)
        shortcut_entry.pack(pady=5)

        tk.Button(edit_window, text="Save", command=save_shortcut, bg="#222222", fg="white").pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(edit_window, text="Cancel", command=edit_window.destroy, bg="#222222", fg="white").pack(side=tk.RIGHT, padx=10, pady=10)

    def reset_to_defaults():
        """
        Reset shortcuts to default values
        """
        save_shortcuts(DEFAULT_SHORTCUTS)
        for i, key in enumerate(DEFAULT_SHORTCUTS.values()):
            shortcut_listbox.delete(i)
            shortcut_listbox.insert(i, key)
        reload_shortcuts()
        logging.info("Shortcuts reset to default. Restart the app to apply changes.")
        show_notification(APP_NAME, "Shortcuts reset to default. Restart the app to apply changes.")
        print("Shortcuts reset to default. Restart the app to apply changes.")

    def reload_shortcuts():
        """
        Reload shortcuts and re-register hotkeys.
        """
        shortcuts = load_shortcuts()
        kb.clear_all_hotkeys()
        register_hotkeys(shortcuts)

    # Create a new window for editing shortcuts
    editor_window = tk.Toplevel(root)
    editor_window.title("Keyboard Shortcuts")
    editor_window.geometry("400x300")
    editor_window.minsize(400, 300)
    editor_window.configure(bg="#333333")
    editor_window.iconbitmap(ICON_PATHH)
    # Get screen dimensions and position the window at the center
    screen_width = editor_window.winfo_screenwidth()
    screen_height = editor_window.winfo_screenheight()
    window_width, window_height = 400, 300  # Same as geometry
    position_x = (screen_width // 2) - (window_width // 2)
    position_y = (screen_height // 2) - (window_height // 2)
    editor_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    # Load current shortcuts
    shortcuts = load_shortcuts()

    # Create a frame for the listboxes
    frame = tk.Frame(editor_window, bg="#333333")
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Configure grid weights for responsiveness
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)

    # Create listboxes for event names and shortcuts
    event_listbox = tk.Listbox(frame, width=20, height=5, bg="#222222", fg="white")
    shortcut_listbox = tk.Listbox(frame, width=20, height=5, bg="#222222", fg="white")

    # Insert event names and shortcuts into listboxes
    events = ["Show Hide Menu", "Take Screenshot", "Open Calculator", "Open Homepage", "Restart Programs", "Toggle Brightness", "Toggle Keyboard"]
    event_keys = ["Show Hide Menu", "Take Screenshot", "Open Calculator", "Open Homepage", "Restart Programs", "Toggle Brightness", "Toggle Keyboard"]
    # ["on_activate_show_hide", "take_screenshot", "open_calculator", "open_homepage", "restart_programs", "toggle_brightness"]
    keys = [shortcuts[key] for key in event_keys]

    for event, key in zip(events, keys):
        event_listbox.insert(tk.END, event)
        shortcut_listbox.insert(tk.END, key)

    event_listbox.grid(row=0, column=0, sticky="nsew")
    shortcut_listbox.grid(row=0, column=1, sticky="nsew")

    # Add edit and reset buttons
    button_frame = tk.Frame(editor_window, bg="#333333")
    button_frame.pack(fill=tk.X, padx=10, pady=5)
    tk.Button(button_frame, text="Edit", command=edit_shortcut, bg="#222222", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Reset to Default", command=reset_to_defaults, bg="#222222", fg="white").pack(side=tk.RIGHT, padx=5)



# enable/disable keyboard
# ----------------------------------------------------------------------------------
# State trackers
keyboard_disabled = False

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Windows 8.1 or later
except:
    pass

# Functions to disable/enable keyboard
def disable_keyboard():
    global keyboard_disabled
    if not keyboard_disabled:
        try:
            ctypes.windll.user32.BlockInput(True)
            keyboard_disabled = True
            logging.info("Keyboard has been disabled!")
            show_notification(APP_NAME, "Keyboard has been disabled!")
            print("Keyboard has been disabled!")
            update_keyboard_button_text()  # Update button text
        except Exception as e:
            logging.error(f"Failed to disable keyboard: {e}")
            show_notification(APP_NAME, f"Failed to disable keyboard: {e}")
            print(f"Failed to disable keyboard: {e}")

def enable_keyboard():
    global keyboard_disabled
    if keyboard_disabled:
        ctypes.windll.user32.BlockInput(False)
        keyboard_disabled = False
        logging.info("Keyboard has been enabled!")
        show_notification(APP_NAME, "Keyboard has been enabled!")
        print("Keyboard has been enabled!")
        update_keyboard_button_text()  # Update button text

# Function to toggle the keyboard state
def toggle_keyboard(): # ctrl+alt+k
    global keyboard_disabled
    if not is_admin():
        elevate()
        return
    if keyboard_disabled:
        enable_keyboard()
    else:
        disable_keyboard()
    # Update button text after toggling
    update_keyboard_button_text()

# Function to update the keyboard button text
def update_keyboard_button_text():
    global toggle_keyboard_button
    if 'toggle_keyboard_button' in globals():
        toggle_keyboard_button.config(text="Enable Keyboard" if keyboard_disabled else "Disable Keyboard")



# Then keep create_timer_widget and create_bookmarks_widget definitions
# ----------------------------------------------------------------------------------
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
        timer_window.attributes("-topmost", True)
        timer_window.geometry("300x200")
        timer_window.minsize(190, 195)
        timer_window.maxsize(500, 300)
        timer_window.configure(bg="#222222")
        timer_window.iconbitmap(ICON_PATHH)
        # Get screen dimensions and position the window at the center
        screen_width = timer_window.winfo_screenwidth()
        screen_height = timer_window.winfo_screenheight()
        window_width, window_height = 300, 200  # Same as geometry
        position_x = (screen_width // 2) - (window_width // 2)
        position_y = (screen_height // 2) - (window_height // 2)
        timer_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
        
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
        stopwatch_window.minsize(235, 175)
        stopwatch_window.maxsize(400, 250)
        stopwatch_window.configure(bg="#222222")
        stopwatch_window.attributes("-topmost", True)
        stopwatch_window.iconbitmap(ICON_PATHH)
        # Get screen dimensions and position the window at the center
        screen_width = stopwatch_window.winfo_screenwidth()
        screen_height = stopwatch_window.winfo_screenheight()
        window_width, window_height = 300, 200  # Same as geometry
        position_x = (screen_width // 2) - (window_width // 2)
        position_y = (screen_height // 2) - (window_height // 2)
        stopwatch_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
        
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


# bookmarks
# ----------------------------------------------------------------------------------
def create_bookmarks_widget(parent):
    """Create a quick web bookmarks widget"""
    bookmarks_frame = tk.Frame(parent, bg="#222222")
    
    # Default bookmarks
    default_bookmarks = {
        "Bibek": "https://www.bibekchandsah.com.np",
        "Google": "https://www.google.com",
        "YouTube": "https://www.youtube.com",
        "GitHub": "https://github.com",
        "Gmail": "https://mail.google.com"
    }
    
    # Load saved bookmarks
    bookmarks_file = os.path.join(app_dir, "upmenubookmarks.json")
    bookmarks = default_bookmarks.copy()
    
    if os.path.exists(bookmarks_file):
        try:
            with open(bookmarks_file, "r") as f:
                saved_bookmarks = json.load(f)
                bookmarks.update(saved_bookmarks)
        except Exception as e:
            logging.error(f"Error loading bookmarks: {e}")
            print(f"Error loading bookmarks: {e}")
    
    def save_bookmarks():
        try:
            with open(bookmarks_file, "w") as f:
                json.dump(bookmarks, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving bookmarks: {e}")
            print(f"Error saving bookmarks: {e}")

    def open_bookmark_manager():
        manager_window = tk.Toplevel(root)
        manager_window.title("Bookmark Manager")
        manager_window.geometry("400x300")
        manager_window.minsize(300, 250)
        manager_window.configure(bg="#222222")
        manager_window.iconbitmap(ICON_PATHH)
        # Get screen dimensions and position the window at the center
        screen_width = manager_window.winfo_screenwidth()
        screen_height = manager_window.winfo_screenheight()
        window_width, window_height = 400, 300  # Same as geometry
        position_x = (screen_width // 2) - (window_width // 2)
        position_y = (screen_height // 2) - (window_height // 2)
        manager_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
        
        # Create listbox for bookmarks
        listbox_frame = tk.Frame(manager_window, bg="#222222")
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        listbox = tk.Listbox(listbox_frame, bg="#333333", fg="white", 
                           font=("Arial", 11), selectbackground="#555555")
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Replace tk.Scrollbar with ttk.Scrollbar
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
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
                    logging.info(f"Added bookmark: {name} -> {url}")
                    show_notification(APP_NAME, f"Added bookmark: {name} -> {url}")
                    print(f"Added bookmark: {name} -> {url}")
                else:
                    logging.warning("URL not provided")
                    show_notification(APP_NAME, "URL not provided")
                    print("URL not provided")

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
                        logging.info(f"Edited bookmark: {old_name} -> {new_name}")
                        show_notification(APP_NAME, f"Edited bookmark: {old_name} -> {new_name}")
                        print(f"Edited bookmark: {old_name} -> {new_name}")
        

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
                    logging.info(f"Deleted bookmark: {name}")
                    show_notification(APP_NAME, f"Deleted bookmark: {name}")
                    print(f"Deleted bookmark: {name}")
        

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
    bookmark_buttons_frame = tk.Frame(bookmarks_frame, bg="#222222", width=850)  # Increased width
    bookmark_buttons_frame.pack(fill=tk.X, expand=True)  # Use fill and expand to use available width
    
    def update_bookmark_buttons():
        # Clear existing buttons
        for widget in bookmark_buttons_frame.winfo_children():
            widget.destroy()
        
        # Create buttons for bookmarks (show as many as will fit)
        count = 0
        max_buttons = 10  # Increased from 8 to show more bookmarks
        
        # Create a scrollable frame for bookmarks if there are many
        if len(bookmarks) > max_buttons:
            # Create a canvas with scrollbar for many bookmarks
            canvas = tk.Canvas(bookmark_buttons_frame, bg="#222222", height=70, 
                             highlightthickness=0, width=800)  # Increased width
            canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            scrollbar = tk.Scrollbar(bookmark_buttons_frame, orient="horizontal", 
                                   command=canvas.xview)
            scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            
            canvas.configure(xscrollcommand=scrollbar.set)
            
            buttons_frame = tk.Frame(canvas, bg="#222222")
            canvas.create_window((0, 0), window=buttons_frame, anchor="nw")
            
            # Add all bookmarks as buttons
            for name, url in bookmarks.items():
                btn = tk.Button(buttons_frame, text=name,
                              command=lambda u=url: webbrowser.open(u),
                              bg="#333333", fg="#d2d2d2", 
                              activebackground="#444444",
                              width=10)
                btn.pack(side=tk.LEFT, padx=2, pady=2)
                count += 1
            
            # Update canvas scrollregion after buttons are added
            buttons_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
            
            # Add mousewheel handler to prevent event propagation
            def on_mousewheel(event):
                # Scroll the canvas
                if event.delta > 0:
                    canvas.xview_scroll(-2, "units")
                else:
                    canvas.xview_scroll(2, "units")
                # Stop event propagation
                return "break"
            
            # Bind mousewheel events for Windows
            canvas.bind("<MouseWheel>", on_mousewheel)
            buttons_frame.bind("<MouseWheel>", on_mousewheel)
            # Bind mousewheel events for Linux
            canvas.bind("<Button-4>", on_mousewheel)
            canvas.bind("<Button-5>", on_mousewheel)
            buttons_frame.bind("<Button-4>", on_mousewheel)
            buttons_frame.bind("<Button-5>", on_mousewheel)
            
            # For each button, also bind the mousewheel event
            for child in buttons_frame.winfo_children():
                child.bind("<MouseWheel>", on_mousewheel)
                child.bind("<Button-4>", on_mousewheel)
                child.bind("<Button-5>", on_mousewheel)
        else:
            # For fewer bookmarks, just add them directly
            for name, url in bookmarks.items():
                if count < max_buttons:
                    btn = tk.Button(bookmark_buttons_frame, text=name,
                                  command=lambda u=url: webbrowser.open(u),
                                  bg="#333333", fg="#d2d2d2", 
                                  activebackground="#444444",
                                  width=10)
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


# context menu
# ----------------------------------------------------------------------------------
def show_context_menu(event, context_menu):
    try:
        # Prevent the main menu from disappearing by grabbing and releasing focus
        root.grab_set()
        root.grab_release()
        root.deiconify()
        check_mouse_position()
        
        # Post the context menu at the cursor position
        context_menu.post(event.x_root, event.y_root)
    except tk.TclError:
        pass  # Handle any errors

def create_context_menu(parent):
    """Create a context menu with common actions"""
    context_menu = tk.Menu(parent, tearoff=0, bg="#333333", fg="#ffffff")
    context_menu.add_command(label="Toggle Brightness", command=toggle_brightness)
    context_menu.add_command(label="Hide Menu", command=on_activate_show_hide)
    
    # Add system monitor toggle
    def toggle_system_monitor():
        global system_monitor_enabled
        system_monitor_enabled = not system_monitor_enabled
        save_config()  # Save the state
        
        if system_monitor_enabled:
            # Resume updates
            if system_monitor_ref and system_monitor_ref.winfo_exists():
                update_system_stats()
            show_notification(APP_NAME, "System Monitor enabled")
        else:
            # Clear labels when disabled
            if system_monitor_ref and system_monitor_ref.winfo_exists():
                for widget in system_monitor_ref.winfo_children():
                    if isinstance(widget, tk.Label):
                        widget.config(text="Monitor disabled", fg="gray")
            show_notification(APP_NAME, "System Monitor disabled")
    
    context_menu.add_command(
        label="Toggle System Monitor",
        command=toggle_system_monitor
    )
    
    context_menu.add_command(label="Restart", command=restart_programs)
    context_menu.add_command(label="Terminate", command=close_menu)
    
    # Add a handler for when the menu is unposted (closed)
    context_menu.bind("<Unmap>", lambda e: root.after(10, root.deiconify))
    
    return context_menu


# Admin elevation functions
# ----------------------------------------------------------------------------------
def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate():
    """Restart the script with administrative privileges."""
    try:
        if not is_admin():
            show_notification(APP_NAME, "Requesting admin privileges...")
            # Re-run the program with admin rights
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)
    except Exception as e:
        logging.error(f"Failed to elevate privileges: {e}")
        show_notification(APP_NAME, f"Failed to elevate privileges: {e}")
        print(f"Failed to elevate privileges: {e}")


# Then keep create_second_page function
# ----------------------------------------------------------------------------------
def create_second_page(parent):
    second_page = tk.Frame(parent, bg="#222222")
    
    # Create a context menu for the page
    context_menu = create_context_menu(second_page)
    # Bind right-click to show the context menu
    second_page.bind("<Button-3>", lambda event: show_context_menu(event, context_menu))
    
    # app launcher
    app_launcher_widget = create_app_launcher(second_page)
    app_launcher_widget.pack(pady=(15, 5))
    root.after(100, initialize_ui)  # Now initialize_ui is defined before being used
    
    # Create a frame for shortcuts, timer, and stopwatch
    tools_frame = tk.Frame(second_page, bg="#222222")
    tools_frame.pack(pady=10)
    
    # list open windows
    list_open_windows_widget = tk.Button(tools_frame, text="List Open Windows", command=list_open_windows_window, 
                        bg="#333333", 
                        fg="#d2d2d2",
                        activebackground="#444444",
                        activeforeground="white")
    list_open_windows_widget.pack(side=tk.LEFT, padx=5)
    
    # Volume Mixer
    # Create a button to show the volume mixer window
    # show_mixer_button = ttk.Button(root, text="Volume Mixer", command=show_volume_mixer)
    # show_mixer_button.pack(pady=20)
    
    volume_mixer_widget = tk.Button(tools_frame, text="Volume Mixer", command=show_volume_mixer, 
                        bg="#333333", 
                        fg="#d2d2d2",
                        activebackground="#444444",
                        activeforeground="white")
    volume_mixer_widget.pack(side=tk.LEFT, padx=5)
    
    # Shortcuts Manager
    # shortcuts_widget = create_shortcuts_manager(tools_frame)
    # shortcuts_widget.pack(side=tk.LEFT, padx=5)
    
    # Edit Shortcuts
    edit_shortcuts_button = tk.Button(tools_frame, text="Edit Shortcuts", command=open_shortcut_editor, 
                        bg="#333333", 
                        fg="#d2d2d2",
                        activebackground="#444444",
                        activeforeground="white")
    edit_shortcuts_button.pack(side=tk.LEFT, padx=5)

    # toggle keyboard
    global toggle_keyboard_button
    toggle_keyboard_button = tk.Button(tools_frame, text="Disable Keyboard", command=toggle_keyboard, 
                        bg="#333333", 
                        fg="#d2d2d2",
                        activebackground="#444444",
                        activeforeground="white")
    toggle_keyboard_button.pack(side=tk.LEFT, padx=5)
    
    
    
    
    # Timer/Stopwatch
    timer_widget = create_timer_widget(tools_frame)
    timer_widget.pack(side=tk.LEFT, padx=5)
    
    # Bookmarks
    bookmarks_widget = create_bookmarks_widget(second_page)
    bookmarks_widget.pack(pady=5)
    
    return second_page



# ----------------------------------------------------------------------------------
# third page content starts here 👇

# Add this function to create the third page
# ----------------------------------------------------------------------------------
def create_third_page(parent):
    """Create the third page with 'Coming Soon' message"""
    third_page = tk.Frame(parent, bg="#222222")
    
    # Create a context menu for the page
    context_menu = create_context_menu(third_page)
    # Bind right-click to show the context menu
    third_page.bind("<Button-3>", lambda event: show_context_menu(event, context_menu))
    
    # Create a container for the message
    message_frame = tk.Frame(third_page, bg="#222222")
    message_frame.pack(expand=True, fill=tk.BOTH)
    
    # Add the "Coming Soon" text
    coming_soon_label = tk.Label(
        message_frame, 
        text="Coming Soon", 
        font=("Arial", 24, "bold"),
        fg="#d2d2d2",
        bg="#222222"
    )
    coming_soon_label.pack(expand=True, pady=50)
    
    # Add a subtitle with more information
    subtitle_label = tk.Label(
        message_frame,
        text="New features are under development",
        font=("Arial", 12),
        fg="#a0a0a0",
        bg="#222222"
    )
    subtitle_label.pack(pady=10)
    
    return third_page

def create_fourth_page(parent):
    """Create the AI Chat page"""
    fourth_page = tk.Frame(parent, bg="#222222")
    
    # Create a context menu for the page
    context_menu = create_context_menu(fourth_page)
    # Bind right-click to show the context menu
    fourth_page.bind("<Button-3>", lambda event: show_context_menu(event, context_menu))
    
    # Header with AI provider info
    header_frame = tk.Frame(fourth_page, bg="#222222")
    header_frame.pack(fill=tk.X, padx=10, pady=5)
    
    lbl_title = tk.Label(header_frame, text="AI Conversation", bg="#222222", fg="white", font=("Arial", 12, "bold"))
    lbl_title.pack(side=tk.LEFT)
    
    # Show current AI provider
    provider_label = tk.Label(header_frame, text=f"Provider: {ai_provider}", bg="#222222", fg="lightgray", font=("Arial", 9))
    provider_label.pack(side=tk.RIGHT)

    # Chat History
    history_frame = tk.Frame(fourth_page, bg="#222222")
    history_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=(5, 0))
    
    chat_history = tk.Text(history_frame, bg="#333333", fg="#d2d2d2", font=("Arial", 10), 
                          wrap=tk.WORD, state=tk.DISABLED, bd=0, insertbackground="white")
    scrollbar = ttk.Scrollbar(history_frame, command=chat_history.yview)
    chat_history.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    chat_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Tags for styling
    chat_history.tag_config("user", foreground="#87CEEB", justify="left")  # Sky blue
    chat_history.tag_config("ai", foreground="#90EE90", justify="left")    # Light green
    chat_history.tag_config("error", foreground="#FF6B6B", justify="center")  # Light red
    chat_history.tag_config("system", foreground="#FFD700", justify="center")  # Gold

    # Input Area - Pack at bottom with explicit positioning
    input_frame = tk.Frame(fourth_page, bg="#444444", relief=tk.RAISED, bd=1)
    input_frame.pack(fill=tk.X, padx=10, pady=5, side=tk.BOTTOM)
    
    # Add placeholder text functionality
    placeholder_text = "Ask me anything..."
    input_entry = tk.Entry(input_frame, bg="#333333", fg="gray", font=("Arial", 12), 
                          bd=0, insertbackground="white")
    input_entry.insert(0, placeholder_text)
    input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5, ipady=8)
    
    def on_entry_click(event):
        if input_entry.get() == placeholder_text:
            input_entry.delete(0, tk.END)
            input_entry.config(fg="white")

    def on_focusout(event):
        if input_entry.get() == '':
            input_entry.insert(0, placeholder_text)
            input_entry.config(fg="gray")
    
    input_entry.bind('<FocusIn>', on_entry_click)
    input_entry.bind('<FocusOut>', on_focusout)
    
    send_btn = tk.Button(input_frame, text="Send", bg="#4CAF50", fg="white", 
                        font=("Arial", 10), bd=0, cursor="hand2", padx=15, pady=5)
    send_btn.pack(side=tk.RIGHT, padx=5, pady=5)
    
    # Clear chat button
    clear_btn = tk.Button(input_frame, text="Clear", bg="#f44336", fg="white", 
                         font=("Arial", 10), bd=0, cursor="hand2", padx=10, pady=5)
    clear_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    def append_message(sender, message, tag):
        chat_history.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M")
        if sender:
            chat_history.insert(tk.END, f"[{timestamp}] {sender}:\n", tag)
        chat_history.insert(tk.END, f"{message}\n\n", tag)
        chat_history.config(state=tk.DISABLED)
        chat_history.see(tk.END)

    def handle_send(event=None):
        msg = input_entry.get().strip()
        if not msg or msg == placeholder_text:
            return
            
        input_entry.delete(0, tk.END)
        input_entry.config(fg="white")
        append_message("You", msg, "user")
        
        # Check if API key is configured
        if not ai_api_key:
            append_message("System", "Please configure your API key in Settings (System Tray -> AI Settings)", "error")
            return
        
        # Disable input while processing
        input_entry.config(state=tk.DISABLED)
        send_btn.config(state=tk.DISABLED, text="Thinking...")
        
        def run_ai():
            try:
                response = chat_with_ai(msg)
                # Schedule UI update on main thread
                fourth_page.after(0, lambda: process_response(response))
            except Exception as e:
                fourth_page.after(0, lambda: process_response(f"Error: {str(e)}"))
            
        threading.Thread(target=run_ai, daemon=True).start()

    def process_response(response):
        if response.startswith("Error:"):
            append_message("System", response, "error")
        else:
            append_message("AI", response, "ai")
        
        input_entry.config(state=tk.NORMAL)
        send_btn.config(state=tk.NORMAL, text="Send")
        input_entry.focus()
    
    def clear_chat():
        chat_history.config(state=tk.NORMAL)
        chat_history.delete(1.0, tk.END)
        chat_history.config(state=tk.DISABLED)
        append_message("System", "Chat cleared", "system")

    send_btn.config(command=handle_send)
    clear_btn.config(command=clear_chat)
    input_entry.bind("<Return>", handle_send)
    
    # Add welcome message
    def show_welcome():
        welcome_msg = f"Welcome to AI Chat! Current provider: {ai_provider}\n"
        if not ai_api_key:
            welcome_msg += "Please configure your API key in System Tray -> AI Settings to start chatting."
        else:
            welcome_msg += "You can start asking questions now!"
        append_message("System", welcome_msg, "system")
    
    # Show welcome message after a short delay
    fourth_page.after(100, show_welcome)
    
    return fourth_page


# Initialize pages
# ----------------------------------------------------------------------------------
main_page_frame = create_first_page(main_container)
second_page_frame = create_second_page(main_container)
third_page_frame = create_third_page(main_container)
fourth_page_frame = create_fourth_page(main_container)

# Set the initial page to be visible
current_page = 0  # Ensure this is set to the index of the first page
main_page_frame.pack(fill=tk.BOTH, expand=True)  # Ensure the main page is packed initially
second_page_frame.pack_forget()  # Hide second page initially
third_page_frame.pack_forget()  # Hide third page
fourth_page_frame.pack_forget()  # Hide fourth page


# Add this before the volume frame creation
# Create a horizontal line
# ----------------------------------------------------------------------------------
separator_canvas = tk.Canvas(canvas, height=2, bg="#222222", highlightthickness=0)
separator_canvas.place(relx=0, rely=0.78, relwidth=1.0)  # Place it above the controls
separator_canvas.create_line(0, 1, MENU_WIDTH, 1, fill="#d2d2d2", width=1)  # Red line


# volume and brightness
# ----------------------------------------------------------------------------------
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
            if controller.is_available():
                controller.volume.SetMasterVolumeLevelScalar(float(val)/100, None)
                # Update value label
                value_label.config(text=f"{int(float(val))}%")
        except Exception as e:
            logging.error(f"Error setting volume: {e}")
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
        if controller.is_available():
            current_volume = int(controller.volume.GetMasterVolumeLevelScalar() * 100)
        else:
            current_volume = 50
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
            if controller.is_available():
                current_vol = int(controller.volume.GetMasterVolumeLevelScalar() * 100)
                # Only update if value is different to avoid visual feedback loop
                if int(volume_slider.get()) != current_vol:
                    volume_slider.set(current_vol)
                    value_label.config(text=f"{current_vol}%")
        except Exception as e:
            logging.error(f"Error updating volume display: {e}")
            print(f"Error updating volume display: {e}")
        volume_frame.after(1000, update_volume_display)  # Check every 1000ms to reduce load
    
    # Start the update loop
    update_volume_display()
    value_label.bind("<MouseWheel>", on_mousewheel)
    
    return volume_frame


# Add these functions before the create_brightness_slider function
# ----------------------------------------------------------------------------------
# def get_brightness():
#     try:
#         c = wmi.WMI(namespace='wmi')
#         monitors = c.WmiMonitorBrightness()
#         return monitors[0].CurrentBrightness
#     except Exception as e:
#         logging.error(f"Error getting brightness: {e}")
#         print(f"Error getting brightness: {e}")
#         return 50

def get_brightness():
    try:
        c = wmi.WMI(namespace='wmi')
        monitors = c.WmiMonitorBrightness()
        if monitors and len(monitors) > 0:
            return monitors[0].CurrentBrightness
        else:
            # No monitors found that support WMI brightness control
            return 50
    except wmi.x_wmi as e:
        # Handle specific WMI COM errors silently
        if "0x80041032" in str(e):
            # This is a common error when WMI can't access brightness
            # Just log at debug level to avoid filling logs
            logging.debug(f"WMI brightness access not available: {e}")
        else:
            logging.error(f"WMI error getting brightness: {e}")
        return 50
    except Exception as e:
        logging.error(f"Error getting brightness: {e}")
        print(f"Error getting brightness: {e}")
        return 50


# def set_brightness(value):
#     try:
#         c = wmi.WMI(namespace='wmi')
#         monitors = c.WmiMonitorBrightnessMethods()
#         monitors[0].WmiSetBrightness(value, 0)
#         return True
#     except Exception as e:
#         logging.error(f"Error setting brightness: {e}")
#         print(f"Error setting brightness: {e}")
#         return False

def set_brightness(value):
    try:
        c = wmi.WMI(namespace='wmi')
        monitors = c.WmiMonitorBrightnessMethods()
        if monitors and len(monitors) > 0:
            monitors[0].WmiSetBrightness(value, 0)
            return True
        else:
            # No monitors found that support WMI brightness control
            return False
    except wmi.x_wmi as e:
        # Handle specific WMI COM errors silently
        if "0x80041032" in str(e):
            # This is a common error when WMI can't access brightness
            logging.debug(f"WMI brightness control not available: {e}")
            print(f"WMI brightness control not available: {e}")
        else:
            logging.error(f"WMI error setting brightness: {e}")
            print(f"WMI error setting brightness: {e}")
        return False
    except Exception as e:
        logging.error(f"Error setting brightness: {e}")
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
            logging.error(f"Error setting brightness: {e}")
            show_notification("Error", f"Error setting brightness: {e}")
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
    except Exception as e:
        logging.error(f"Error getting brightness: {e}")
        print(f"Error getting brightness: {e}")
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
# ----------------------------------------------------------------------------------
def get_network_speed():
    global last_bytes_recv, last_bytes_sent, last_check_time
    
    current_time = time.time()
    current_bytes = psutil.net_io_counters()
    
    # Initialize on first call
    if last_check_time == 0:
        last_bytes_recv = current_bytes.bytes_recv
        last_bytes_sent = current_bytes.bytes_sent
        last_check_time = current_time
        return "0 B/s", "0 B/s"
    
    # Calculate time difference
    time_diff = current_time - last_check_time
    if time_diff < 0.1:  # Avoid division by very small numbers
        return "Calculating...", "Calculating..."
    
    # Calculate speeds
    download = (current_bytes.bytes_recv - last_bytes_recv) / time_diff
    upload = (current_bytes.bytes_sent - last_bytes_sent) / time_diff
    
    # Update last values
    last_bytes_recv = current_bytes.bytes_recv
    last_bytes_sent = current_bytes.bytes_sent
    last_check_time = current_time
    
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

# Optimize update intervals - reduce frequency of updates
UPDATE_INTERVAL_FAST = 500    # For critical UI elements (ms)
UPDATE_INTERVAL_MEDIUM = 1000  # For normal UI elements (ms)
UPDATE_INTERVAL_SLOW = 2000   # For non-critical elements (ms)

# Add throttling for resource-intensive operations
last_update_times = {
    'network': 0,
    'system_stats': 0,
    'brightness': 0,
    'volume': 0,
    'mute': 0
}

def throttle(operation, min_interval=500):
    """Throttle function to prevent too frequent updates"""
    current_time = time.time() * 1000  # Convert to ms
    if current_time - last_update_times.get(operation, 0) >= min_interval:
        last_update_times[operation] = current_time
        return True
    return False

# Optimize network speed display update
def update_network_speed():
    if not throttle('network', UPDATE_INTERVAL_MEDIUM):
        network_frame.after(100, update_network_speed)
        return
        
    try:
        download_speed, upload_speed = get_network_speed()
        download_label.config(text=f"D: {download_speed}")
        upload_label.config(text=f"U: {upload_speed}")
    except Exception as e:
        logging.error(f"Error updating network speed: {e}")
    
    network_frame.after(UPDATE_INTERVAL_MEDIUM, update_network_speed)

# Add these global variables at the top with other globals
last_bytes_recv = 0
last_bytes_sent = 0
last_check_time = 0
system_monitor_ref = None  # Reference to the system monitor frame


# Modify the create_system_monitor function to fix the global declaration
# ----------------------------------------------------------------------------------
def create_system_monitor(parent):
    """Create a system resource monitor widget"""
    global system_monitor_ref, update_system_stats
    
    monitor_frame = tk.Frame(parent, bg="#222222")
    system_monitor_ref = monitor_frame
    
    cpu_label = tk.Label(monitor_frame, text="CPU: 0%", fg="lightgray",
                        bg="#222222", font=("Arial", 10))
    cpu_label.pack(anchor="w")
    
    ram_label = tk.Label(monitor_frame, text="RAM: 0%", fg="lightgray",
                        bg="#222222", font=("Arial", 10))
    ram_label.pack(anchor="w")
    
    # open task manager
    def open_task_manager(event=None):
        try:
            subprocess.run(["taskmgr"], shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Task Manager: {e}")
            logging.error(f"Error opening task manager: {e}")
    
    # when the user clicks on the cpu label, open task manager
    cpu_label.bind("<Button-1>", lambda event: open_task_manager())
    ram_label.bind("<Button-1>", lambda event: open_task_manager())
    
    # show the mouse pointer
    monitor_frame.bind("<Enter>", lambda event: monitor_frame.config(cursor="hand2"))   
    monitor_frame.bind("<Leave>", lambda event: monitor_frame.config(cursor=""))
    
    # Define the update function
    def update_system_stats_func():
        # Don't update if disabled
        if not system_monitor_enabled:
            return
            
        if not throttle('system_stats', UPDATE_INTERVAL_MEDIUM):
            if system_monitor_ref and system_monitor_ref.winfo_exists():
                system_monitor_ref.after(100, update_system_stats)
            return
        
        try:
            # CPU usage - use interval parameter to avoid blocking
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_label.config(text=f"CPU: {cpu_percent}%")
            
            # RAM usage
            ram = psutil.virtual_memory()
            ram_percent = ram.percent
            ram_label.config(text=f"RAM: {ram_percent}%")
            
            # Update color based on usage
            for label, value in [(cpu_label, cpu_percent), (ram_label, ram_percent)]:
                if value > 90:
                    label.config(fg="red")
                elif value > 70:
                    label.config(fg="orange")
                else:
                    label.config(fg="lightgray")
                
        except Exception as e:
            logging.error(f"System monitor error: {e}")
        
        # Schedule next update if widget still exists and monitoring is enabled
        if system_monitor_ref and system_monitor_ref.winfo_exists() and system_monitor_enabled:
            system_monitor_ref.after(UPDATE_INTERVAL_MEDIUM, update_system_stats)
    
    # Assign the function to the global variable
    update_system_stats = update_system_stats_func
    
    return monitor_frame

# Add this to your UI layout
system_monitor = create_system_monitor(canvas)
system_monitor.place(relx=0.69, rely=0.98, anchor="sw")  # Adjust position as needed



# Move these function definitions before create_bottom_controls
# ----------------------------------------------------------------------------------
def create_simple_calendar(parent):
    """Create a simple calendar widget as fallback"""
    cal_frame = tk.Frame(parent, bg="#222222", padx=10, pady=10)
    
    # Current date for initial display
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    # Month and year display with navigation
    header_frame = tk.Frame(cal_frame, bg="#222222")
    header_frame.pack(fill="x", pady=5)
    
    # Left arrow
    left_btn = tk.Button(header_frame, text="<", bg="#333333", fg="white",
                       command=lambda: update_month(-1))
    left_btn.pack(side=tk.LEFT, padx=5)
    
    # Month/Year label
    month_year_label = tk.Label(header_frame, text=f"{now.strftime('%B %Y')}", 
                              bg="#222222", fg="white", width=15)
    month_year_label.pack(side=tk.LEFT, padx=5)
    
    # Right arrow
    right_btn = tk.Button(header_frame, text=">", bg="#333333", fg="white",
                        command=lambda: update_month(1))
    right_btn.pack(side=tk.LEFT, padx=5)
    
    # Days of week header
    days_frame = tk.Frame(cal_frame, bg="#222222")
    days_frame.pack(fill="x")
    
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for day in days:
        day_label = tk.Label(days_frame, text=day, width=3, bg="#333333", fg="white")
        day_label.pack(side=tk.LEFT, padx=1, pady=1)
    
    # Calendar grid
    cal_grid_frame = tk.Frame(cal_frame, bg="#222222")
    cal_grid_frame.pack()
    
    # Create 6 rows of 7 day buttons (max possible calendar view)
    day_buttons = []
    for row in range(6):
        button_row = []
        row_frame = tk.Frame(cal_grid_frame, bg="#222222")
        row_frame.pack()
        for col in range(7):
            day_btn = tk.Button(row_frame, text="", width=3, height=1,
                              bg="#222222", fg="white", relief=tk.FLAT)
            day_btn.pack(side=tk.LEFT, padx=1, pady=1)
            button_row.append(day_btn)
        day_buttons.append(button_row)
    
    def update_month(delta):
        nonlocal current_year, current_month
        
        # Update month and handle year change
        current_month += delta
        if current_month > 12:
            current_month = 1
            current_year += 1
        elif current_month < 1:
            current_month = 12
            current_year -= 1
        
        # Update display
        month_year_label.config(text=f"{calendar.month_name[current_month]} {current_year}")
        update_calendar()
    
    def update_calendar():
        # Get calendar for current month
        cal = calendar.monthcalendar(current_year, current_month)
        
        # Clear all buttons
        for row in day_buttons:
            for btn in row:
                btn.config(text="", bg="#222222", state=tk.DISABLED)
        
        # Fill in the days
        today = datetime.now().date()
        for i, week in enumerate(cal):
            for j, day in enumerate(week):
                if day != 0:
                    day_btn = day_buttons[i][j]
                    day_btn.config(text=str(day), state=tk.NORMAL)
                    
                    # Highlight today
                    if (day == today.day and 
                        current_month == today.month and 
                        current_year == today.year):
                        day_btn.config(bg="#444444")
                    else:
                        # Weekend days
                        if j == 0 or j == 6:  # Sunday or Saturday
                            day_btn.config(bg="#222222", fg="lightblue")
                        else:
                            day_btn.config(bg="#222222", fg="white")
    
    # Initial calendar update
    update_calendar()
    
    return cal_frame


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
        # Check if calendar is already open
        for widget in root.winfo_children():
            if isinstance(widget, tk.Toplevel) and hasattr(widget, 'calendar_window'):
                return  # Calendar already open
        
        try:
            # Create a new toplevel window
            cal_window = tk.Toplevel(root)
            cal_window.calendar_window = True  # Mark as calendar window
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
            try:
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
                
                # Use a more efficient approach for tracking mouse position
                def check_mouse_position():
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
                        cal_window.after(200, check_mouse_position)  # Check less frequently
                    else:
                        cal_window.destroy()
                
                # Start checking mouse position
                cal_window.after(200, check_mouse_position)
            except Exception as e:
                # Fallback if Calendar widget fails
                logging.error(f"Error creating calendar widget: {e}")
                error_label = tk.Label(cal_window, text=f"Calendar unavailable\n{str(e)}", 
                                     bg="#222222", fg="red", pady=20)
                error_label.pack(expand=True)
                
                close_btn = tk.Button(cal_window, text="Close",
                                    command=cal_window.destroy,
                                    bg="#333333", fg="white")
                close_btn.pack(pady=10)
        except Exception as e:
            logging.error(f"Error showing calendar: {e}")
            show_notification(APP_NAME, f"Error showing calendar: {str(e)}")
    
    # Bind click event to show calendar
    datetime_label.bind("<Button-1>", show_calendar)
    
    update_time()
    return datetime_frame

# Update datetime widget position
datetime_widget = create_datetime_widget(canvas)
datetime_widget.place(relx=0.99, rely=0.95, anchor="se")  # Keep at far right




# Update the rounded rectangle size
canvas.create_rounded_rect(0, 0, MENU_WIDTH, MENU_HEIGHT, radius, fill="#222222", outline="")

# Update window position calculation
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

def update_mute_button():
    if not throttle('mute', UPDATE_INTERVAL_MEDIUM):
        root.after(100, update_mute_button)
        return
        
    try:
        is_muted = is_speaker_muted()
        if 'speaker_button' in globals() and speaker_button and hasattr(speaker_button, 'config'):
            if 'speaker_label_ref' in globals() and speaker_label_ref:
                speaker_label_ref.config(text="Unmute" if is_muted else "Mute")
            speaker_button.config(
                command=unmute_speakers if is_muted else mute_speakers,
                image=images['volumemute'] if is_muted else images['volumeup']
            )
    except Exception as e:
        logging.error(f"Error updating mute button: {e}")
        print(f"Error updating mute button: {e}")
        
    root.after(UPDATE_INTERVAL_MEDIUM, update_mute_button)

# Optimize mouse position checking
def check_mouse_position():
    global last_mouse_position, hide_timer, menu_hidden
    
    try:
        # If menu is manually hidden or not enabled, don't show it
        if not menu_enabled:
            return
            
        x, y = root.winfo_pointerxy()
        last_mouse_position = (x, y)
        
        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        center_left = (screen_width - MENU_WIDTH) // 2
        center_right = center_left + MENU_WIDTH
        
        # Show window only if mouse is at top AND within center MENU_WIDTH
        if y < 0.1 and center_left <= x <= center_right:
            if not root.winfo_viewable() and not menu_hidden:
                root.deiconify()
                root.after(50, initialize_ui)
            if hide_timer:
                root.after_cancel(hide_timer)
                hide_timer = None
        else:
            if root.winfo_viewable() and not hide_timer:
                hide_timer = root.after(100, hide_window)
    except Exception as e:
        logging.error(f"Error checking mouse position: {e}")
        print(f"Error checking mouse position: {e}")

    root.after(200, check_mouse_position)

# Ensure the hide_window function is defined
def hide_window():
    global hide_timer
    # Only hide if mouse is still outside the window
    x, y = last_mouse_position
    
    # Get screen dimensions for center calculation
    screen_width = root.winfo_screenwidth()
    center_left = (screen_width - MENU_WIDTH) // 2
    center_right = center_left + MENU_WIDTH
    
    # Hide if y position is below threshold OR x is outside center width
    if (y >= MENU_HEIGHT) or (x < center_left or x > center_right): 
        root.withdraw()
    hide_timer = None


# Start checking mouse position
check_mouse_position()


# Create arrow buttons and page indicator
# ----------------------------------------------------------------------------------
def create_arrow_buttons():
    page_names = ["Main", "Apps", "Coming Soon", "AI Chat"]
    
    def switch_page(direction):
        global current_page
        pages = [main_page_frame, second_page_frame, third_page_frame, fourth_page_frame]
        total_pages = len(pages)
        
        if direction == "right":
            current_page = (current_page + 1) % total_pages
        elif direction == "left":
            current_page = (current_page - 1) % total_pages
        
        # Hide all pages
        for page in pages:
            page.pack_forget()
        
        # Show current page
        pages[current_page].pack(fill=tk.BOTH, expand=True)
        
        # Update page indicator
        update_page_indicator()
    
    def update_page_indicator():
        page_indicator.config(text=f"{page_names[current_page]} ({current_page + 1}/4)")
    
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
    
    # Page indicator
    global page_indicator
    page_indicator = tk.Label(canvas, text=f"{page_names[current_page]} ({current_page + 1}/4)",
                             bg="#222222", fg="lightgray", font=("Arial", 9))
    page_indicator.place(relx=0.5, rely=0.02, anchor="n")
    
    # Keep references to prevent garbage collection
    left_arrow_btn.image = images['leftarrow']
    right_arrow_btn.image = images['rightarrow']
    
    return left_arrow_frame, right_arrow_frame

# Add arrow buttons to the menu
left_arrow, right_arrow = create_arrow_buttons()


# Function to get user active status
# ----------------------------------------------------------------------------------
DEFAULT_INTERVAL = 180  # Default interval (fallback)
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

def is_internet_available():
    """Check if the internet connection is available."""
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.RequestException:
        logging.warning("No internet connection.")
        print("No internet connection.")
        return False
    
def format_interval(seconds):
    """
    Format the interval in seconds into a human-readable format.
    """
    if seconds < 60:
        return f"{seconds} second{'s' if seconds > 1 else ''}"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''}"


def fetch_interval():
    """
    Fetch the interval value from the remote URL and return it as a human-readable string.
    """
    try:
        response = requests.get(INTERVAL_URL, timeout=5)
        response.raise_for_status()
        interval_data = response.json()
        interval_seconds = interval_data.get("upmenu_activeuser_interval", DEFAULT_INTERVAL)
        human_readable_interval = format_interval(interval_seconds)
        print(f"\n-----Fetched interval (User Active Interval): {human_readable_interval}-----")
        return interval_seconds
    except requests.RequestException as e:
        logging.error(f"Failed to fetch interval from URL. Using default: {DEFAULT_INTERVAL} seconds")
        print(f"\n-----Failed to fetch interval from URL. Using default: {DEFAULT_INTERVAL} seconds-----")
        return DEFAULT_INTERVAL


def get_public_ip():
    """Get the public IP address of the user."""
    try:
        response = requests.get("https://api64.ipify.org?format=json")
        response.raise_for_status()
        return response.json().get("ip")
    except requests.RequestException as e:
        logging.error(f"Error fetching public IP: {e}")
        print(f"Error fetching public IP: {e}")
        return None


def get_geolocation(ip_address):
    """Get geolocation details for the given IP address."""
    try:
        # api_url = f"https://ipinfo.io/{ip_address}?token=ccb3ba52662beb"  # Replace with your ipinfo token
        api_url = f"https://ipinfo.io/{ip_address}?token={IPINFO_TOKEN}"  # Replace with your ipinfo token
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return (
            data.get("country", "N/A"),
            data.get("region", "N/A"),
            data.get("city", "N/A"),
            data.get("org", "N/A"),
            data.get("loc", "N/A"),
            data.get("postal", "N/A"),
            data.get("timezone", "N/A"),
        )
    except requests.RequestException as e:
        logging.error(f"Error fetching geolocation: {e}")
        print(f"Error fetching geolocation: {e}")
        return ("N/A",) * 7

ip_address = get_public_ip()
country, region, city, org, loc, postal, timezone = get_geolocation(ip_address)
# print(f"Country: {country}, Region: {region}, City: {city}")


def get_system_info():
    """Get detailed system information as a string."""
    info = {
        "System": platform.system(),
        "Node Name": platform.node(),
        "Release": platform.release(),
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "CPU Cores": psutil.cpu_count(logical=False),
        "Logical CPUs": psutil.cpu_count(logical=True),
        "Total RAM": f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
        "Available RAM": f"{psutil.virtual_memory().available / (1024 ** 3):.2f} GB",
        "Used RAM": f"{psutil.virtual_memory().used / (1024 ** 3):.2f} GB",
        "RAM Usage": f"{psutil.virtual_memory().percent}%",
        "Disk Usage": {
            partition.mountpoint: {
                "Total": f"{psutil.disk_usage(partition.mountpoint).total / (1024 ** 3):.2f} GB",
                "Used": f"{psutil.disk_usage(partition.mountpoint).used / (1024 ** 3):.2f} GB",
                "Free": f"{psutil.disk_usage(partition.mountpoint).free / (1024 ** 3):.2f} GB",
                "Usage": f"{psutil.disk_usage(partition.mountpoint).percent}%",
            }
            for partition in psutil.disk_partitions()
        },
        "IP Address": socket.gethostbyname(socket.gethostname()),
        "MAC Address": ":".join(
            ["{:02x}".format((uuid.getnode() >> elements) & 0xFF) for elements in range(0, 2 * 6, 2)][::-1]
        ),
    }
    logging.info(f"System Info: generated")
    print(f"System Info: generated")
    return json.dumps(info, separators=(",", ":"))


def update_active_user_file(new_entry, active_user):
    """Update the active user file on GitHub."""
    file_url = f"{API_BASE_URL}/repos/{REPO}/contents/{FILE_PATH}"
    
    max_retries = 12
    attempt = 0
    while attempt < max_retries:
        try:
            response = requests.get(file_url, headers=HEADERS)
            if response.status_code == 200:
                file_data = response.json()
                current_content = base64.b64decode(file_data["content"]).decode("utf-8")
                sha = file_data["sha"]
            else:
                print(f"Failed to fetch file content: {response.status_code} - {response.json()}")
                return

            updated_content = current_content + new_entry
            encoded_content = base64.b64encode(updated_content.encode("utf-8")).decode("utf-8")

            update_payload = {
                "message": f"Updating-{active_user}-{country}-{region}-{city}-{unique_id} active user log",
                "content": encoded_content,
                "sha": sha,
                "branch": BRANCH,
            }

            response = requests.put(file_url, headers=HEADERS, data=json.dumps(update_payload))
            if response.status_code == 200:
                print(f"Active-user File updated successfully! New entry: {new_entry}")
                return  # Exit function after successful update
            else:
                print(f"Failed to update file: {response.status_code} - {response.json()}")
        except Exception as e:
            logging.error(f"Error updating file: {e}")
            print(f"Error updating file: {e}")
        attempt += 1
        print(f"Retrying upload ({attempt}/{max_retries}) for {FILE_PATH}...")
        time.sleep(5)  # Wait before retrying
    print(f"Failed to update {FILE_PATH} after {max_retries} attempts.")


def log_active_user():
    """Log the active user information with system info."""
    if not is_internet_available():
        print("No internet connection. Skipping this user active update cycle.")
        return
    
    try:
        active_user = os.getlogin()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        user_ip = get_public_ip()
        country, region, city, org, loc, postal, timezone = get_geolocation(user_ip) if user_ip else ("N/A",) * 7
        system_info = get_system_info()

        new_entry = (
            f"{timestamp} - User: {active_user}, Unique_ID: {unique_id} , IP: {user_ip}, Location: {country}, {region}, {city}, Org: {org}, "
            f"Coordinates: {loc}, Postal: {postal}, TimeZone: {timezone}, System Info: {system_info}\n"
        )
        update_active_user_file(new_entry, active_user)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
              
# Function to check the active user periodically
def active_user_check():
    global DEFAULT_INTERVAL
    try:
        DEFAULT_INTERVAL = fetch_interval()  # Fetch updated interval
        log_active_user()
        time.sleep(DEFAULT_INTERVAL)
        threading.Timer(DEFAULT_INTERVAL, active_user_check).start() # 10 second
    except Exception as e:
        logging.error(f"Error in checking active user: {e}")
        print(f"Error in checking active user: {e}")
# # Start the periodic check
# active_user_check() # Start the active user check




# Take a screenshot
# ----------------------------------------------------------------------------------
def take_feedback_screenshot():
    """Enhanced screenshot function with active mode handling"""
    global screenshot_interval, is_running
    while True:
        try:
            if is_running:
                # Check if workstation is locked
                if ctypes.windll.user32.GetForegroundWindow() == 0:
                    logging.info("Skipping feedbackss - workstation locked")
                    time.sleep(10)
                    continue
                    
                timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
                filename = os.path.join(screenshot_folder, f"screenshot_{timestamp}.png")
                pyautogui.screenshot(filename)
                # logging.info(f"take_feedbackss-->feedbackss saved: {filename}")
                
            with lock:
                current_interval = screenshot_interval
            time.sleep(current_interval)
            
        except Exception as e:
            logging.error(f"feedbackss error: {str(e)}")
            time.sleep(30)  # Backoff on errors            


# Toggle screenshot taking
# ----------------------------------------------------------------------------------
def toggle_feedback_screenshots(icon, item):
    global is_running
    is_running = not is_running
    save_config()  # Save the updated state to the config file
    if (is_running == True):
        show_notification(APP_NAME, "Enabled taking Feedback")
    else:
        show_notification(APP_NAME, "Disabled taking Feedback")
    logging.info(f"toggle_feedback_feedbackss - {'Enabled' if is_running else 'Disabled'}")
    print(f"toggle_feedback_feedbackss - {'Enabled' if is_running else 'Disabled'}")


# function to upload the log filesss
# ----------------------------------------------------------------------------------

# set the upload log interval according to url if not url then default
# if url default then it uses default fallback interval
# if url is reached then it's not using fallback interval from url it uploads in the url interval

# Default upload interval and fallback interval in case of network error
DEFAULT_UPLOAD_INTERVAL = 600 # 10 minutes
# DEFAULT_UPLOAD_INTERVAL = 100 # 1.6 minutes
# DEFAULT_FALLBACK_INTERVAL = 20
DEFAULT_FALLBACK_INTERVAL = 300 # 5 minutes

# Number of retries for failed uploads
MAX_RETRIES = 12
RETRY_DELAY = 5  # Delay in seconds between retries

# URL to fetch the upload interval
# INTERVAL_URL = "https://raw.githubusercontent.com/bebedudu/autoupdate/main/interval.json"

CACHE_FILE = os.path.join(app_dir, "upmenufiles_cache.json")
# Cache for uploaded files to avoid re-uploading
data_uploaded_cache = set()
screenshots_uploaded_cache = set()

def format_interval(seconds):
    """
    Converts a time duration in seconds into a human-readable format.
    """
    if seconds < 60:
        # return f"{seconds} seconds"
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        # return f"{minutes} minute{'s' if minutes > 1 else ''}"
        return f"{seconds / 60:.2f} minute{'s' if minutes > 1 else ''}"
    elif seconds < 86400:
        hours = seconds // 3600
        # return f"{hours} hour{'s' if hours > 1 else ''}"
        return f"{seconds / 3600:.2f} hours{'s' if hours > 1 else ''}"
    elif seconds < 2592000:  # Approx. 30 days
        days = seconds // 86400
        # return f"{days} day{'s' if days > 1 else ''}"
        return f"{seconds / 86400:.2f} day{'s' if days > 1 else ''}"
    elif seconds < 31536000:  # Approx. 365 days
        months = seconds // 2592000
        # return f"{months} month{'s' if months > 1 else ''}"
        return f"{seconds / 2592000:.2f} month{'s' if months > 1 else ''}"
    else:
        years = seconds // 31536000
        # return f"{years} year{'s' if years > 1 else ''}"
        return f"{seconds / 31536000:.2f} year{'s' if years > 1 else ''}"

# Function to fetch the upload interval from a JSON file hosted online
def fetch_value_from_url(url, key, default_value):
    """
    Fetches a specific value from the provided URL's JSON response. Falls back to the default value on failure.
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if key in data:
            return int(data[key])
            # return int(data.get(key, default_value))
        else:
            logging.error(f"Key '{key}' not found in the JSON response.")
            print(f"Key '{key}' not found in the JSON response.")
    except requests.exceptions.RequestException as e:
        # logging.error(f"Network error while fetching {key}: {e}")
        print(f"Network error while fetching {key}: {e}")
    except ValueError as e:
        logging.error(f"Error parsing JSON for {key}: {e}")
        print(f"Error parsing JSON for {key}: {e}")

    return default_value

def get_last_upload_time():
    """
    Retrieves the last upload timestamp from a file. Returns None if not found.
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                last_upload_str = data.get("last_upload")
                if last_upload_str:  # Only try to parse if last_upload exists and is not None
                    last_upload_time = datetime.fromisoformat(last_upload_str)
                    # logging.info(f"Last served at {last_upload_time}")
                    print(f"Last served at {last_upload_time}")
                    return last_upload_time
                else:
                    logging.info("No previous upload time found")
                    print("No previous upload time found")
                    return None
        except Exception as e:
            logging.error(f"Error reading last serve file: {e}")
            print(f"Error reading last serve file: {e}")
    return None

def set_last_upload_time():
    """
    Updates the last upload timestamp in a file.
    """
    global last_upload
    try:
        last_upload = datetime.now().isoformat()
        save_config()
    except Exception as e:
        logging.error(f"Error writing last serve file: {e}")
        print(f"Error writing last serve file: {e}")

# Function to load the cache from the JSON file
def load_uploaded_cache(cache_file=CACHE_FILE):
    """
    Loads the uploaded files cache from a file.
    """
    global screenshots_uploaded_cache
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                screenshots_uploaded_cache = set(json.load(f))
            print(f"Loaded cache with {len(screenshots_uploaded_cache)} entries.")
        except Exception as e:
            logging.error(f"Error loading cache: {e}. Initializing an empty cache.")
            print(f"Error loading cache: {e}. Initializing an empty cache.")
            screenshots_uploaded_cache = set()
    else:
        # data_uploaded_cache = set()
        screenshots_uploaded_cache = set()
        print("No cache file found. Initializing an empty cache.")

# Function to save the cache to the JSON file
def save_uploaded_cache(cache_file=CACHE_FILE):
    """
    Saves the uploaded files cache to a file.
    """
    try:
        with open(cache_file, "w") as f:
            json.dump(list(screenshots_uploaded_cache), f, indent=4)
        print(f"Cache saved with {len(screenshots_uploaded_cache)} entries.")
    except Exception as e:
        logging.error(f"Error saving cache: {e}")
        print(f"Error saving cache: {e}")

# Function to check if a screenshot file is uploaded
def is_screenshot_uploaded(file_path):
    """
    Checks if the file has already been uploaded by comparing its unique identifier in the cache.
    """
    global screenshots_uploaded_cache
    return file_path in screenshots_uploaded_cache

# Function to mark a screenshot as uploaded
def mark_screenshot_uploaded(file_path):
    """
    Adds the file to the uploaded cache and persists the cache.
    """
    global screenshots_uploaded_cache
    if file_path not in screenshots_uploaded_cache:
        screenshots_uploaded_cache.add(file_path)
        save_uploaded_cache()  # Save the cache only if new files are added

def clean_uploaded_cache():
    """Removes stale entries from the uploaded files cache."""
    global screenshots_uploaded_cache
    valid_files = {path for path in screenshots_uploaded_cache if os.path.exists(path)}
    removed_files = screenshots_uploaded_cache - valid_files
    screenshots_uploaded_cache = valid_files
    if removed_files:
        print(f"Removed {len(removed_files)} stale cache entries")
        logging.info(f"Cleaned cache: Removed {len(removed_files)} stale entries")
    save_uploaded_cache()

def upload_screenshots_folder_to_github(folder_path, repo_name, repo_folder_name, branch_name, github_token):
    """Uploads all untracked screenshots in the specified folder to GitHub."""
    global screenshots_uploaded_cache
    
    # Use absolute path for screenshots folder
    abs_screenshots_folder = os.path.join(app_dir, "upmenufeedback")
    
    for root, _, files in os.walk(abs_screenshots_folder):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if not file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue  # Skip non-image files
                
            if not is_screenshot_uploaded(file_path):
                retry_count = 0
                while retry_count < MAX_RETRIES:
                    try:
                        print(f"Attempting to fetch feedbackss: {file_path}")
                        upload_file_to_github(file_path, repo_name, repo_folder_name, branch_name, github_token)
                        mark_screenshot_uploaded(file_path)
                        # logging.info(f"Successfully fetched feedbackss: {file_path}")
                        print(f"Successfully uploaded feedbackss: {file_path}")
                        break
                    except Exception as e:
                        retry_count += 1
                        logging.error(f"Error uploading {file_path} (Attempt {retry_count}/{MAX_RETRIES}): {e}")
                        if retry_count < MAX_RETRIES:
                            time.sleep(RETRY_DELAY)
                        else:
                            logging.warning(f"Permanently failed to upload {file_path}")
                            # Remove from cache if permanently failed
                            screenshots_uploaded_cache.discard(file_path)
                            save_uploaded_cache()
            # else:
            #     logging.info(f"Skipping {file_path} - already uploaded")
            #     print(f"Skipping {file_path} - already uploaded")

def upload_file_to_github(file_path, repo_name, repo_folder_name, branch_name, github_token):
    """
    Uploads a file to a specified folder in a GitHub repository.
    """
    max_retries = 12
    attempt = 0
    
    # Determine if this is a screenshot file
    is_screenshot = "screenshot" in file_path.lower()
    
    while attempt < max_retries:
        try:
            # Read file content based on type
            if is_screenshot:
                with open(file_path, 'rb') as f:
                    content = f.read()
                content_base64 = base64.b64encode(content).decode('utf-8')
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    new_content = f.read()

            file_name = os.path.basename(file_path)
            
            # Create unique filename based on file type
            if is_screenshot:
                unique_name = f"{repo_folder_name}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{username}_{unique_id}_{file_name}"
            else:
                # Stable filename for non-screenshot files
                unique_name = f"{repo_folder_name}/{username}_{unique_id}_{file_name}"

            api_url = f"https://api.github.com/repos/{repo_name}/contents/{unique_name}"

            headers = {"Authorization": f"token {github_token}"}

            # Check if file exists
            existing_file = requests.get(api_url, headers=headers).json()
            sha = None

            if not is_screenshot and 'sha' in existing_file:
                # Handle text file updates
                sha = existing_file['sha']
                existing_content = base64.b64decode(existing_file['content']).decode('utf-8')
                # append the new content to the top of the existing content
                # updated_content = f"{new_content}\n\n{'='*80}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - New Data Append\n{'='*80}\n{existing_content}"
                updated_content = f"\n\n{'='*80}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - New Data 👇 \n{'='*80} \n{new_content}\n\n{'='*80}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Previous Data 👇 \n{'='*80}\n{existing_content}"
                content_base64 = base64.b64encode(updated_content.encode('utf-8')).decode('utf-8')
            elif not is_screenshot:
                # New text file
                content_base64 = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')

            payload = {
                "message": f"{'Updating' if sha else 'Uploading'} {username}-{country}-{region}-{city}-{unique_id} {file_name}",
                "content": content_base64,
                "branch": branch_name
            }
            
            if sha:  # Add SHA if updating existing file
                payload["sha"] = sha

            response = requests.put(api_url, json=payload, headers=headers)

            if response.status_code in [200, 201]:
                # logging.info(f"Uploaded successfully: {response.json().get('content').get('html_url')}")
                print(f"✅ Served successfully: {response.json().get('content').get('html_url')}")
                return  # Exit function after successful upload
            else:
                logging.error(f"Failed to upload {file_name}: {response.status_code}, {response.text}")
                print(f"☠️ Failed to serve {file_name}: {response.status_code}, {response.text}")

        except Exception as e:
            # logging.error(f"Error serving file {file_path}: {e}")
            print(f"Error serving file {file_path}: {e}")
            
        attempt += 1
        print(f"Retrying upload ({attempt}/{max_retries}) for {file_path}...")
        time.sleep(3)  # Wait before retrying
    print(f"Failed to upload {file_path} after {max_retries} attempts.")
        
# Function to upload all files in a folder to GitHub
def upload_folder_to_github(folder_path, repo_name, repo_folder_name, branch_name, github_token):
    """Uploads all files in a folder to GitHub with extension filtering."""
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if not file_name.lower().endswith(('.txt', '.log', '.json')):  # Add allowed extensions
                continue  # Skip non-log files
                
            file_path = os.path.join(root, file_name)
            upload_file_to_github(file_path, repo_name, repo_folder_name, branch_name, github_token)

def upload_multiple_to_specific_folders(file_mapping, folder_mapping, repo_name, branch_name, github_token):
    """
    Uploads multiple files and folders to specific subfolders in a GitHub repository.
    """
    for file_path, subfolder in file_mapping.items():
        if os.path.exists(file_path):
            upload_file_to_github(file_path, repo_name, f"upmenu/{subfolder}", branch_name, github_token)
        else:
            logging.error(f"File not found: {file_path}")
            print(f"File not found: {file_path}")

    for folder_path, subfolder in folder_mapping.items():
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            upload_folder_to_github(folder_path, repo_name, f"upmenu/{subfolder}", branch_name, github_token)
        else:
            logging.error(f"Folder not found or not a directory: {folder_path}")
            print(f"Folder not found or not a directory: {folder_path}")

# Main upload logs function
def upload_logs():
    """
    Main function to upload logs and screenshots.
    Initializes the cache and monitors for file uploads.
    """
    # Configuration
    repo_name = REPO  # Replace with your GitHub repo
    branch_name = BRANCH  # Replace with your branch name
    github_token = GITHUB_TOKEN  # Replace with your GitHub token

    # Define file-to-subfolder mapping USING ABSOLUTE PATHS
    file_mapping = {
        os.path.join(app_dir, "upmenubookmarks.json"): "bookmarks",
        os.path.join(app_dir, "upmenuconfig.json"): "config",
        os.path.join(app_dir, "upmenushortcuts.json"): "shortcuts",
        os.path.join(app_dir, "upmenuerror.log"): "errorlog",
        os.path.join(app_dir, "upmenufiles_cache.json"): "cache",
    }
    
    # Define folder-to-subfolder mapping
    folder_mapping = {
        os.path.join(app_dir, "logs"): "logs",
    }
    
    # Define allowed log extensions
    LOG_EXTENSIONS = ('.log', '.txt', '.json', '.bat')  # Add other allowed extensions


    # Define the screenshots folder path
    screenshots_folder = "upmenufeedback"
    
    # Load the cache of uploaded screenshots
    load_uploaded_cache()
    
    # Load initial configuration
    load_config()

    print("Starting the serveing monitoring script...")

    while True:  # Infinite loop for continuous execution
        
        # Fetch the upload interval from the URL
        # Fetch the upload interval and fallback interval from the URL
        upload_interval = fetch_value_from_url(INTERVAL_URL, "upmenu_upload_interval", DEFAULT_UPLOAD_INTERVAL)
        fallback_interval = fetch_value_from_url(INTERVAL_URL, "upmenu_upload_interval_status", DEFAULT_FALLBACK_INTERVAL)
        
        if not isinstance(upload_interval, int):
            upmenu_upload_interval = DEFAULT_UPLOAD_INTERVAL
        
        # Fetch the upload interval dynamically
        readable_interval = format_interval(upload_interval)  # Format the interval
        logging.info(f"serve interval set to {readable_interval}.")
        print(f"\n-----serve interval set to {readable_interval}.-----")
        print(f"Fallback interval set to (interval to check serve time) {fallback_interval} seconds.")

        # Check the last upload time
        last_upload_time = get_last_upload_time()
        
        # Perform the uploads
        try:

            # Calculate time until the next upload
            if last_upload_time:
                time_since_last_upload = (datetime.now() - last_upload_time).total_seconds()
                # time_until_next_upload = upload_interval - time_since_last_upload
                time_until_next_upload = max(0, upload_interval - time_since_last_upload)
                # logging.info(f"Time until next serve: {format_interval(max(0, time_until_next_upload))}.")
                print(f"Time until next serve: {format_interval(time_until_next_upload)}.")
            else:
                time_until_next_upload = 0  # Upload immediately if no last upload time

            # Upload files if the interval has passed
            if time_until_next_upload <= 0:
                # Perform the upload
                print("serving files...")
                upload_multiple_to_specific_folders(file_mapping, folder_mapping, repo_name, branch_name, github_token)
                set_last_upload_time()
                print(f"🎉🎉 Files served successfully at {datetime.now().isoformat()}. 🎉🎉")

            # Upload screenshots if the interval has passed
            if time_until_next_upload <= 0:
                print("serving feedbackss folder...")
                upload_screenshots_folder_to_github(
                    screenshots_folder, repo_name, f"upmenu/{screenshots_folder}", branch_name, github_token
                )
                print(f"🎉🎉 Served feedbackss folder successfully at {datetime.now().isoformat()}. 🎉🎉")
                # Update the last upload time
                set_last_upload_time()
                
                # logging.info(f"Files served successfully at {datetime.now().isoformat()}.")
                print(f"🎉🎉🎉🎉 Files served successfully at {datetime.now().isoformat()}. 🎉🎉🎉🎉")
                
        except Exception as e:
            logging.error(f"Error during serve: {e}")
            print(f"Error during serve: {e}")

        # Sleep for a short time to avoid excessive checking
        # time.sleep(20)
        # time.sleep(interval_logs_Upload_status)
        # Wait for the next upload cycle
        # time.sleep(upload_interval if upload_interval != DEFAULT_UPLOAD_INTERVAL else FALLBACK_INTERVAL)
        time.sleep(upload_interval if upload_interval != DEFAULT_UPLOAD_INTERVAL else fallback_interval)


# auto delete logs folder & screenshot folder 
#----------------------------------------------------------------------------------
# Function to format the remaining time as "X days Y hours Z minutes W seconds"
def format_remaining_time(seconds):
    days = seconds // (24 * 3600)
    seconds %= 24 * 3600
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{int(days)} days {int(hours)} hours {int(minutes)} minutes {int(seconds)} seconds"

def fetch_config_from_url(url):
    """Fetch configuration from a URL and return as a dictionary."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"\n-----Values of interval.JSON-----\n{response.json()}")
            return response.json()
        else:
            logging.warning(f"Failed to fetch config. Status code: {response.status_code}")
            print(f"Failed to fetch config. Status code: {response.status_code}")
            return {}
    except Exception as e:
        # logging.error(f"Error fetching config from URL: {e}")
        print(f"Error fetching config from URL: {e}")
        return {}


# Function to calculate the folder's age and delete it if older than 90 days
def check_and_delete_old_folders():
    global remaining_log_days, remaining_screenshot_days
    try:
        # Fetch configuration from URL
        config_url = "https://raw.githubusercontent.com/bebedudu/autoupdate/refs/heads/main/programfeeds.json"
        config = fetch_config_from_url(config_url)
        
        # Extract values from config or use defaults
        remaining_screenshot_days = config.get("upmenu_remaining_feedback_days", threshold_seconds) # Default threshold_seconds is in seconds
        screenshot_delete_status = config.get("upmenu_feedback_delete_status", interval_logs_delete_status)
        
        # Print fetched and default intervals
        print("\n-----fetch status of feedbackss interval-----")
        print(f"Fetched remaining_feedbackss_days: {config.get('upmenu_remaining_feedback_days', 'Not found')} (default: {threshold_seconds} seconds - {format_remaining_time(threshold_seconds)})")
        print(f"Fetched feedbackss_delete_status: {config.get('upmenu_feedback_delete_status', 'Not found')} (default: {interval_logs_delete_status} seconds)")

        # Print currently using values
        # print("\n-----Currently Using Values-----")
        # print(f"Using remaining_screenshot_days: {upmenu_remaining_feedback_days} seconds")
        # print(f"Using screenshot_delete_status: {upmenu_feedback_delete_status} seconds")
        
        # Print currently using values
        print("\n-----Currently Using Values-----")
        print(f"Using remaining_feedbackss_seconds: {remaining_screenshot_days} seconds ({format_remaining_time(remaining_screenshot_days)})")
        print(f"Using feedbackss_delete_status: {screenshot_delete_status} seconds")
        
        current_time = datetime.now()
        # threshold_seconds = 120  # 2 minute in seconds for testing 
        # threshold_seconds = 5 * 24 * 60 * 60  # 5 days in seconds
        # global threshold_seconds

        # Screenshot folder cleaning
        if os.path.exists(screenshot_folder):
            remaining_screenshot_days = clean_folder(screenshot_folder, current_time, remaining_screenshot_days)
            # remaining_screenshot_days = clean_folder(screenshot_folder, current_time, threshold_seconds)
            # print("remaining screenshot days:- ", remaining_screenshot_days)
            # logging.warning(f"remaining time to delete screenshots: {format_remaining_time(remaining_screenshot_days)}")
            print(f"------------------------------------------------------------------------------------------\nremaining time to delete feedbackss: {format_remaining_time(remaining_screenshot_days)}\n==========================================================================================\n\n")

        # Save updated remaining seconds to upmenuconfig.json
        save_config()
        
        # Schedule next check based on the fetched or default interval
        threading.Timer(screenshot_delete_status, schedule_folder_check).start()

    except Exception as e:
        logging.error(f"Error in check_and_delete_old_folders: {e}")
        print(f"Error in check_and_delete_old_folders: {e}")

def clean_folder(folder_path, current_time, threshold_seconds):
    """
    Clean a folder by deleting files older than the threshold and return remaining time.
    """
    try:
        remaining_seconds = threshold_seconds
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_age = current_time - datetime.fromtimestamp(os.path.getmtime(file_path))
                file_age_seconds = file_age.total_seconds()

                # Delete files older than the threshold
                if file_age_seconds >= threshold_seconds:
                    try:
                        os.remove(file_path)
                        # logging.info(f"Deleted old file: {file_path}")
                        print(f"⚠️ Deleted old file: {file_path}")
                    except Exception as e:
                        logging.error(f"Error deleting file {file_path}: {e}")
                        print(f"Error deleting file {file_path}: {e}")
                else:
                    # Calculate remaining time for the newest file
                    remaining_seconds = min(remaining_seconds, threshold_seconds - file_age_seconds)
                    # print("remaining seconds:- ", remaining_seconds)

        # If folder is empty, delete it
        if not os.listdir(folder_path):
            os.rmdir(folder_path)
            logging.info(f"Deleted empty folder: {folder_path}")
            print(f"🗑️ Deleted empty folder: {folder_path}")
            os.makedirs(folder_path, exist_ok=True)  # Recreate the folder
            logging.info(f"Recreated folder: {folder_path}")
            print(f"📁 Recreated folder: {folder_path}")

        return max(0, remaining_seconds)  # Return remaining time
    except Exception as e:
        logging.error(f"Error cleaning folder {folder_path}: {e}")
        print(f"Error cleaning folder {folder_path}: {e}")
        return threshold_seconds  # Default remaining time if an error occurs

# Function to get the folder's last modified time
def get_folder_age(folder_path):
    try:
        folder_creation_time = datetime.fromtimestamp(os.path.getctime(folder_path))
        logging.info(f"Folder {folder_path} creation time: {folder_creation_time}")
        print(f"Folder {folder_path} creation time: {folder_creation_time}")
        return folder_creation_time
    except Exception as e:
        logging.error(f"Error getting folder age for {folder_path}: {e}")
        print(f"Error getting folder age for {folder_path}: {e}")
        return datetime.now()  # Return current time if there's an error


# Function to delete a folder
def delete_folder(folder_path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if os.path.exists(folder_path):
            for root, dirs, files in os.walk(folder_path, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    try:
                        os.remove(file_path)
                        logging.info(f"[{timestamp}] - Deleted file: {file_path}")
                        print(f"[{timestamp}] - Deleted file: {file_path}")
                    except Exception as e:
                        logging.error(f"Error deleting file {file_path}: {e}")
                        print(f"Error deleting file {file_path}: {e}")
                for name in dirs:
                    dir_path = os.path.join(root, name)
                    try:
                        os.rmdir(dir_path)
                        logging.info(f"[{timestamp}] - Deleted directory: {dir_path}")
                        print(f"[{timestamp}] - Deleted directory: {dir_path}")
                    except Exception as e:
                        logging.error(f"Error deleting directory {dir_path}: {e}")
                        print(f"Error deleting directory {dir_path}: {e}")
            os.rmdir(folder_path)
            logging.info(f"[{timestamp}] - Deleted folder: {folder_path}")
            print(f"[{timestamp}] - Deleted folder: {folder_path}")
    except Exception as e:
        logging.error(f"Error deleting folder {folder_path}: {e}")
        print(f"Error deleting folder {folder_path}: {e}")

# Function to check and update the folder deletion status periodically
def schedule_folder_check():
    global interval_logs_delete_status
    try:
        check_and_delete_old_folders()
        save_config()
        # Schedule the next execution after 24 hour for testing
        # threading.Timer(86400, schedule_folder_check).start() # 24 hour
        # threading.Timer(21600, schedule_folder_check).start() # 6 hour
        # threading.Timer(40, schedule_folder_check).start() # 10 second
        # threading.Timer(interval_logs_delete_status, schedule_folder_check).start() # 10 second
    except Exception as e:
        logging.error(f"Error in scheduling folder check: {e}")
        print(f"Error in scheduling folder check: {e}")
# Start the periodic check
# schedule_folder_check()




# Check for program update
#-----------------------------------------------------------------------------------
DEFAULT_UPDATE_INTERVAL = 900  # Default interval in seconds if not fetched from URL
is_downloading = False # Global variable to track download status

def format_size(size):
    """Dynamically format file size to B, KB, MB, or GB."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} GB"

def format_time(seconds):
    """Format time into seconds, minutes, hours, or days."""
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{seconds / 60:.2f} minute{'s' if minutes > 1 else ''}"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{seconds / 3600:.2f} hours{'s' if hours > 1 else ''}"
    elif seconds < 2592000:  # Approx. 30 days
        days = seconds // 86400
        return f"{seconds / 86400:.2f} day{'s' if days > 1 else ''}"
    elif seconds < 31536000:  # Approx. 365 days
        months = seconds // 2592000
        return f"{seconds / 2592000:.2f} month{'s' if months > 1 else ''}"
    else:
        years = seconds // 31536000
        return f"{seconds / 31536000:.2f} year{'s' if years > 1 else ''}"

def check_for_update_async():
    try:
        show_notification(APP_NAME, "Checking for updates .....")
        threading.Thread(target=check_for_update, daemon=True).start()
    except Exception as e:
        logging.error(f"Error checking for update: {e}")
        print(f"⚠️ Error checking for update: {e}")

def fetch_interval_data():
    """Fetch and return the interval.json data."""
    try:
        response = requests.get(INTERVAL_URL, timeout=10)
        response.raise_for_status()
        return response.json()  # Parse JSON response
    except requests.exceptions.RequestException as e:
        # logging.error(f"Failed to fetch interval data: {e}")
        print(f"Failed to fetch interval data: {e}")
        return None

def get_update_interval(interval_data):
    """Get the update interval from the interval data."""
    if interval_data and "upmenu_updatecheck_interval" in interval_data:
        return interval_data["upmenu_updatecheck_interval"]
    return DEFAULT_UPDATE_INTERVAL

def get_latest_version(interval_data):
    """Get the latest version from the interval data."""
    if interval_data and "upmenu_latest_version" in interval_data:
        return interval_data["upmenu_latest_version"]
    return None

def check_and_auto_update():
    """Check for auto-update and handle the update process."""
    global is_downloading
    
    if is_downloading:  # Skip if a download is already in progress
        print("::::::::::Download already in progress. Skipping this update check.::::::::::")
        return
    
    interval_data = fetch_interval_data()
    auto_update = interval_data.get("upmenu_auto_update", False) if interval_data else False
    latest_version = get_latest_version(interval_data)

    if auto_update:
        logging.info("Auto-update is enabled.")
        if latest_version and latest_version > CURRENT_VERSION:
            print(f"\n#####################################################################\nNew version available: {latest_version}. Updating automatically...\n#####################################################################")
            is_downloading = True
            # threading.Thread(target=lambda: run_tkinter_window(latest_version), daemon=True).start()
            start_download_window(latest_version)
        else:
            logging.info("🎉 You are already using the latest version. 🎉")
            print("\n\n🎉 You are already using the latest version. 🎉")
    else:
        logging.warning("Auto-update is disabled or configuration could not be fetched.")
        print("Auto-update is disabled or configuration could not be fetched.")
        # messagebox.showwarning("Auto-Update Disabled", "Auto-update is disabled or the interval configuration could not be fetched. Please check manually for updates.")


def start_auto_update_checker():
    """Start a loop to check for updates at regular intervals."""
    interval_data = fetch_interval_data()
    update_interval = get_update_interval(interval_data)

    while True:
        print(f"\n-----------------------------------------------------------------\nChecking for updates every {update_interval} seconds... \n-----------------------------------------------------------------\n")
        check_and_auto_update()
        time.sleep(update_interval)

def start_download_window(latest_version):
    """Create a minimized window during download."""
    def download_in_background():
        # download_update(latest_version)
        threading.Thread(target=lambda: run_tkinter_window(latest_version), daemon=True).start()
        update_window.destroy()  # Close the window after the download is complete

    update_window = tk.Tk()
    update_window.title("Downloading Update")
    update_window.geometry("300x50")
    update_window.iconify()  # Minimize the window

    tk.Label(update_window, text="Downloading update... Please wait.", pady=10).pack()
    threading.Thread(target=download_in_background, daemon=True).start()
    update_window.mainloop()       

def check_for_update(auto_update=False):
    """Check for updates and handle the update process."""
    try:
        interval_data = fetch_interval_data()
        latest_version = get_latest_version(interval_data)

        if latest_version > CURRENT_VERSION:
            print(f"\nUpdate Available: {latest_version}")
            if auto_update:
                logging.info("Auto-updating to the latest version...")
                print("\n\nAuto-updating to the latest version...")
                threading.Thread(target=lambda: run_tkinter_window(latest_version), daemon=True).start()
            else:
                # if messagebox.askyesno("Update Available", f"A new version (v{latest_version}) is available. Update now?"):
                #     threading.Thread(target=lambda: run_tkinter_window(latest_version), daemon=True).start()
                threading.Thread(target=lambda: run_tkinter_window(latest_version), daemon=True).start()
        else:
            show_notification(APP_NAME, f"You are using the latest version {CURRENT_VERSION}.")
            print("You are using the latest version.")
            if not auto_update:
                messagebox.showinfo("No Update", f"You are using the latest version {CURRENT_VERSION}.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to check for updates: {e}")
        if not auto_update:
            logging.warning("Error", "Failed to check for updates. Please try again later.")
            messagebox.showerror("Error", "Failed to check for updates. Please try again later.")

"""Download the update."""
def download_update(latest_version, retries=0, max_retries=3):
    global is_downloading
    try:
        download_url = f"{BASE_DOWNLOAD_URL}/v{latest_version}/{APPLICATION_NAME}"
        progress_label.config(text="Downloading update...")
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get("Content-Length", 0))
        progress_bar["maximum"] = total_size
        downloaded_size = 0
        start_time = time.time()

        with open("update_temp.exe", "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    progress_bar["value"] = downloaded_size

                    elapsed_time = time.time() - start_time
                    speed = downloaded_size / elapsed_time
                    remaining_time = (total_size - downloaded_size) / speed if speed > 0 else 0

                    progress_label.config(
                        text=f"Downloaded: {format_size(downloaded_size)} of {format_size(total_size)}"
                    )
                    time_label.config(
                        text=f"Speed: {format_size(speed)}/s | Remaining Time: {format_time(remaining_time)}"
                    )
                    update_window.update()

        replace_executable()
    except Exception as e:
        logging.error("Download Error downloading update")
        messagebox.showerror("Download Error", f"Failed to download update: {e}")
        if retries < max_retries:
            # Wait 5 seconds, then retry
            progress_label.config(text=f"Retrying download... (Attempt {retries+2}/{max_retries+1})")
            update_window.after(5000, lambda: download_update(latest_version, retries=retries+1, max_retries=max_retries))
        else:
            progress_label.config(text="Update failed after multiple attempts.")
    finally:
        is_downloading = False  # Reset the download flag after completion

def restart_program():
    """Restart the program silently."""
    try:
        logging.info("Restarting the application after update...")
        print("Restarting the application after update...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        logging.error(f"Failed to restart the application: {e}")
        print(f"Failed to restart the application: {e}")

def replace_executable():
    """Replace the old executable with the new one silently."""
    try:
        current_path = os.path.join(os.getcwd(), APPLICATION_NAME)
        backup_path = f"{current_path}.old"
        update_path = os.path.join(os.getcwd(), "update_temp.exe")

        if os.path.exists(backup_path):
            os.remove(backup_path)

        if os.path.exists(current_path):
            os.rename(current_path, backup_path)

        os.rename(update_path, current_path)
        logging.info("Application updated sucessfully!")
        print("Application updated sucessfully!")
        # messagebox.showinfo(APP_NAME, "The program has been updated successfully!")
        restart_program()
    except Exception as e:
        logging.error("error replacing file")
        messagebox.showerror("Error", f"Failed to replace the executable: {e}")
        print("Error", f"Failed to replace the executable: {e}")
        
def clean_partial_files():
    try:
        update_path = os.path.join(os.getcwd(), "update_temp.exe")
        if os.path.exists(update_path):
            os.remove(update_path)
    except Exception as e:
        logging.error("error cleaning up partial files")
        print(f"Error during cleanup: {e}")


def run_tkinter_window(latest_version=None):
    
    global update_window, progress_label, progress_bar, time_label

    update_window = tk.Tk()
    update_window.title("Updater")
    update_window.geometry("400x250")
    update_window.resizable(False, False)
    update_window.iconbitmap(ICON_PATH)
    
    # Get screen dimensions and position the window at the center
    screen_width = update_window.winfo_screenwidth()
    screen_height = update_window.winfo_screenheight()
    window_width, window_height = 400, 250  # Same as geometry
    position_x = (screen_width // 2) - (window_width // 2)
    position_y = (screen_height // 2) - (window_height // 2)
    update_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    update_window.iconify()  # Minimize the window
    # update_window.withdraw()  # Hides the window
    # update_window.overrideredirect(True)  # Removes window miminize, close decorations
    
    progress_label = ttk.Label(update_window, text="Click 'Check for Updates' to start.")
    progress_label.pack(pady=10)

    progress_bar = ttk.Progressbar(update_window, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)

    time_label = ttk.Label(update_window, text="", font=("Arial", 10))
    time_label.pack(pady=5)
    
    if latest_version:
        progress_label.config(text="Starting download...")
        logging.info("Starting download...")
        threading.Thread(target=download_update, args=(latest_version,), daemon=True).start()
        
    quit_button = ttk.Button(update_window, text="Quit", command=update_window.destroy)
    quit_button.pack(pady=5)

    update_window.mainloop()


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
            logging.info(f"Startup Enabled. Path: {app_path}")
            show_notification(APP_NAME, "Enabled startup at boot.")
            print(f"Startup Enabled. Path: {app_path}")
        else:
            try:
                winreg.DeleteValue(startup_key, APP_NAME)
                logging.info(f"Startup Disabled")
                show_notification(APP_NAME, "Disabled startup at boot.")
                print(f"Startup Disabled")
            except FileNotFoundError:
                # Key doesn't exist, which is fine when disabling
                pass
        
        is_startup_enabled = enable
        save_config()  # Save the state to config file
        winreg.CloseKey(startup_key)
    except Exception as e:
        logging.error(f"Error toggling startup: {e}")
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


# system tray
# ----------------------------------------------------------------------------------

# AI Settings Window
# ----------------------------------------------------------------------------------
def open_ai_settings(icon=None, item=None):
    """
    Open a dialog to configure AI settings.
    """
    settings_window = tk.Toplevel(root)
    settings_window.title("AI Settings")
    settings_window.geometry("400x350")
    settings_window.configure(bg="#333333")
    settings_window.attributes("-topmost", True)
    settings_window.resizable(False, False)
    
    if os.path.exists(ICON_PATHH):
        settings_window.iconbitmap(ICON_PATHH)

    # Center the window
    screen_width = settings_window.winfo_screenwidth()
    screen_height = settings_window.winfo_screenheight()
    window_width, window_height = 400, 350
    position_x = (screen_width // 2) - (window_width // 2)
    position_y = (screen_height // 2) - (window_height // 2)
    settings_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    # Header
    tk.Label(settings_window, text="AI Configuration", font=("Arial", 16, "bold"), 
             bg="#333333", fg="white").pack(pady=15)

    # Provider Selection
    provider_frame = tk.Frame(settings_window, bg="#333333")
    provider_frame.pack(fill=tk.X, padx=20, pady=10)
    
    tk.Label(provider_frame, text="AI Provider:", bg="#333333", fg="#d2d2d2", 
             font=("Arial", 11), width=12, anchor="w").pack(side=tk.LEFT)
    
    provider_var = tk.StringVar(value=ai_provider)
    provider_combo = ttk.Combobox(provider_frame, textvariable=provider_var, 
                                 state="readonly", font=("Arial", 10))
    provider_combo['values'] = ('OpenAI', 'Gemini')
    provider_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

    # API Key Entry
    key_frame = tk.Frame(settings_window, bg="#333333")
    key_frame.pack(fill=tk.X, padx=20, pady=10)
    
    tk.Label(key_frame, text="API Key:", bg="#333333", fg="#d2d2d2", 
             font=("Arial", 11), width=12, anchor="w").pack(side=tk.LEFT)
    
    key_var = tk.StringVar(value=ai_api_key)
    key_entry = tk.Entry(key_frame, textvariable=key_var, bg="#222222", fg="white", 
                        insertbackground="white", font=("Arial", 10), show="*")
    key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
    
    # Show/Hide API Key button
    show_key_var = tk.BooleanVar()
    def toggle_key_visibility():
        if show_key_var.get():
            key_entry.config(show="")
            show_key_btn.config(text="Hide")
        else:
            key_entry.config(show="*")
            show_key_btn.config(text="Show")
    
    show_key_btn = tk.Button(key_frame, text="Show", command=toggle_key_visibility,
                            bg="#555555", fg="white", font=("Arial", 9), width=6)
    show_key_btn.pack(side=tk.RIGHT, padx=(5, 0))

    # Instructions
    instructions_frame = tk.Frame(settings_window, bg="#333333")
    instructions_frame.pack(fill=tk.X, padx=20, pady=10)
    
    instructions_text = """Instructions:
• OpenAI: Get your API key from https://platform.openai.com/api-keys
• Gemini: Get your API key from https://aistudio.google.com/app/apikey
• Keep your API key secure and don't share it with others
• The key will be saved locally in your configuration file"""
    
    instructions_label = tk.Label(instructions_frame, text=instructions_text, 
                                 bg="#333333", fg="#b0b0b0", font=("Arial", 9),
                                 justify=tk.LEFT, wraplength=350)
    instructions_label.pack(anchor="w")

    # Test connection button
    test_frame = tk.Frame(settings_window, bg="#333333")
    test_frame.pack(fill=tk.X, padx=20, pady=10)
    
    def test_connection():
        temp_provider = provider_var.get()
        temp_key = key_var.get()
        
        if not temp_key:
            messagebox.showwarning("Warning", "Please enter an API key first.")
            return
        
        # Temporarily set the values for testing
        global ai_provider, ai_api_key
        old_provider = ai_provider
        old_key = ai_api_key
        
        ai_provider = temp_provider
        ai_api_key = temp_key
        
        test_btn.config(text="Testing...", state=tk.DISABLED)
        
        def run_test():
            try:
                response = chat_with_ai("Hello, this is a test message.")
                if response and not response.startswith("Error:"):
                    settings_window.after(0, lambda: show_test_result(True, "Connection successful!"))
                else:
                    settings_window.after(0, lambda: show_test_result(False, response))
            except Exception as e:
                settings_window.after(0, lambda: show_test_result(False, str(e)))
            finally:
                # Restore original values
                ai_provider = old_provider
                ai_api_key = old_key
        
        threading.Thread(target=run_test, daemon=True).start()
    
    def show_test_result(success, message):
        test_btn.config(text="Test Connection", state=tk.NORMAL)
        if success:
            messagebox.showinfo("Test Result", message)
        else:
            messagebox.showerror("Test Failed", f"Connection failed: {message}")
    
    test_btn = tk.Button(test_frame, text="Test Connection", command=test_connection,
                        bg="#666666", fg="white", font=("Arial", 10))
    test_btn.pack()

    def save_settings():
        global ai_provider, ai_api_key
        ai_provider = provider_var.get()
        ai_api_key = key_var.get()
        save_config()
        show_notification(APP_NAME, f"AI settings saved: {ai_provider}")
        logging.info(f"AI settings saved: Provider={ai_provider}, Key={'*' * len(ai_api_key) if ai_api_key else 'None'}")
        settings_window.destroy()

    # Buttons
    btn_frame = tk.Frame(settings_window, bg="#333333")
    btn_frame.pack(pady=20)
    
    tk.Button(btn_frame, text="Save", command=save_settings, 
              bg="#4CAF50", fg="white", width=12, font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
    
    tk.Button(btn_frame, text="Cancel", command=settings_window.destroy, 
              bg="#f44336", fg="white", width=12, font=("Arial", 10)).pack(side=tk.LEFT, padx=10)


def create_system_tray():
    """Create system tray icon with menu"""
    global system_tray_icon
    
    # If system tray icon already exists, return it
    if system_tray_icon is not None:
        return system_tray_icon

    def on_exit(icon, item):
        try:
            logging.info(f"Closing application...")
            show_notification(APP_NAME, "Closing application...")
            print(f"Closing application...")
            icon.stop()
            root.quit()
        except Exception as e:
            logging.error(f"Error closing application: {e}")
            print(f"Error closing application: {e}")
    
    # function to restart application 
    def on_restart(icon, item):
        try:
            icon.stop()
            logging.info(f"Restarting application...")
            show_notification(APP_NAME, "Restarting application...")
            print(f"Restarting application...")
            python = sys.executable
            os.execl(python, python, *sys.argv)
        except Exception as e:
            logging.error(f"Error restarting application: {e}")
            print(f"Error restarting application: {e}")
    
    # function to show developer menu
    def on_developer(icon, item):
        try:
            logging.info(f"Opening developer website")
            print(f"Opening developer website")
            webbrowser.open("https://bibekchandsah.com.np")
        except Exception as e:
            logging.error(f"Error opening developer website: {e}")
            print(f"Error opening developer website: {e}")
    
    def on_open_config(icon, item):
        try:
            if os.path.exists(CONFIG_FILE):
                os.startfile(CONFIG_FILE)
            else:
                raise FileNotFoundError("Config file not found.")
        except Exception as e:
            logging.error(f"Error opening config file: {e}")
            show_notification(APP_NAME, f"Error: {e}")
            print(f"Error opening config file: {e}")
    
    def on_open_bookmarks(icon, item):
        try:
            if os.path.exists(bookmarks_file):
                os.startfile(bookmarks_file)
            else:
                raise FileNotFoundError("Config file not found.")
        except Exception as e:
            logging.error(f"Error opening bookmarks file: {e}")
            show_notification(APP_NAME, f"Error: {e}")
            print(f"Error opening bookmarks file: {e}")
            
    def on_open_shortcuts(icon, item):
        try:
            if os.path.exists(shortcuts_file):
                os.startfile(shortcuts_file)
            else:
                raise FileNotFoundError("Shortcuts file not found.")
        except Exception as e:
            logging.error(f"Error opening shortcuts file: {e}")
            show_notification(APP_NAME, f"Error: {e}")
            print(f"Error opening shortcuts file: {e}")
    
    def on_open_log(icon, item):
        try:
            if os.path.exists(LOG_FILE):
                os.startfile(LOG_FILE)
            else:
                raise FileNotFoundError("Log file not found.")
        except Exception as e:
            logging.error(f"Error opening log file: {e}")
            show_notification(APP_NAME, f"Error: {e}")
            print(f"Error opening log file: {e}")
    
    def on_hide(icon, item):
        try:
            global menu_hidden, menu_enabled
            menu_hidden = True  # Set flag to prevent auto-show
            menu_enabled = False  # Disable menu showing
            logging.info("Application hidden to system tray")
            show_notification(APP_NAME, "Menu hidden")
            print(f"Application hidden to system tray")
            root.withdraw()
        except Exception as e:
            logging.error(f"Error hide_app: {e}")
            print(f"Error in hide_app: {e}")
    
    def on_show(icon, item):
        try:
            global menu_hidden, menu_enabled
            menu_hidden = False  # Reset hidden state
            menu_enabled = True  # Enable menu showing
            logging.info("Menu enabled and shown")
            show_notification(APP_NAME, "Menu enabled. Move mouse to top of screen to show")
            print(f"Menu enabled and shown")
            # Immediately show the menu
            root.deiconify()
            root.after(50, initialize_ui)
            check_mouse_position()
            print(f"Menu enabled and shown")
        except Exception as e:
            logging.error(f"Error show_app: {e}")
            print(f"Error in show_app: {e}")
    
    # Load the icon
    icon_image = Image.open(get_asset_path("assets/images/upmenu.ico"))
    
    # Create the menu
    menu = (
        pystray.MenuItem("Hide", on_hide),
        pystray.MenuItem("Show", on_show),
        pystray.MenuItem("Run on Startup", (on_toggle_startup), checked=is_startup_checked),
        pystray.MenuItem("Take Screenshot", take_screenshot),
        pystray.MenuItem("AI Settings", open_ai_settings),
        pystray.MenuItem("Toggle Keyboard", toggle_keyboard),
        pystray.MenuItem("Developer", on_developer),

        pystray.MenuItem("Restore Defaults", restore_defaults),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Open Config", on_open_config),
        pystray.MenuItem("Open Bookmarks", on_open_bookmarks),
        pystray.MenuItem("Open Shortcuts", on_open_shortcuts),
        pystray.MenuItem("Open Log", on_open_log),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Pause/Resume Feedback", toggle_feedback_screenshots, checked=lambda item: is_running),
        pystray.MenuItem("Check for Updates", check_for_update),
        # pystray.MenuItem("Check for Updates", check_and_auto_update),
        pystray.MenuItem("Restart", on_restart),
        pystray.MenuItem("Exit", on_exit)
    )
    
    # Create the icon and store in global variable
    shortcut_key = f"{APP_NAME} \n Ctrl + Alt + M"
    system_tray_icon = pystray.Icon(APP_NAME, icon_image, shortcut_key, menu)
    
    return system_tray_icon

# Add this code before root.mainloop()
def run_system_tray():
    global system_tray_icon
    if system_tray_icon is None:
        system_tray_icon = create_system_tray()
    system_tray_icon.run()

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

# Add this line after creating all UI elements but before the mainloop
# def initialize_ui():
#     """Initialize UI elements after everything is created"""
#     if update_app_buttons_ref:
#         update_app_buttons_ref()
#         logging.info("Initializing UI with saved apps")
#         print("Initializing UI with saved apps")
#     else:
#         print("Warning: update_app_buttons_ref not initialized")


# hide the file from the user
# ----------------------------------------------------------------------------------
def hide_folder(path):
    # Check if the path exists
    if not os.path.exists(path):
        logging.error(f"The path {path} does not exist.")
        print(f"The path {path} does not exist.")
        return
    
    # Use ctypes to set the file attribute to hidden
    try:
        # FILE_ATTRIBUTE_HIDDEN = 0x2
        ctypes.windll.kernel32.SetFileAttributesW(path, 0x2)
        # logging.info(f"Folder '{path}' has been hidden successfully.")
        print(f"Folder '{path}' has been hidden successfully.")
    except Exception as e:
        logging.error(f"Failed to hide folder: {e}")
        print(f"Failed to hide folder: {e}")

# Path to the folder you want to hide
folder_path = r"C:\BCSApplications\upmenu\upmenufeedback"
# Call the function to hide the folder
hide_folder(folder_path)


# def check_single_instance():
#     """
#     Ensure only one instance of the application is running.
#     Returns True if this is the first instance, False otherwise.
#     """
#     try:
#         # Create a unique mutex name using the app name
#         mutex_name = f"Global\\{APP_NAME}_{unique_id}_SingleInstance"
#         print(f"unique id of {APP_NAME} i.e. mutex name: {mutex_name}")
        
#         # Attempt to create/acquire the mutex
#         handle = win32event.CreateMutex(None, 1, mutex_name)
        
#         # Check if the mutex already exists
#         if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
#             logging.warning("Application is already running!")
#             print("Application is already running!")
#             show_notification(APP_NAME, "Application is already running!")
#             return False
            
#         return True
#     except Exception as e:
#         logging.error(f"Error checking single instance: {e}")
#         print(f"Error checking single instance: {e}")
#         return False

def check_single_instance():
    """Ensure only one instance of the application is running"""
    try:

        # Create a mutex using the application UUID
        mutex = ctypes.windll.kernel32.CreateMutexW(None, False, f"Global\\{APP_NAME}_{unique_id}_SingleInstance")
        print(f"unique id of {APP_NAME} i.e. mutex name: {mutex}")
        last_error = ctypes.windll.kernel32.GetLastError()
        
        if last_error == 183:  # ERROR_ALREADY_EXISTS
            print("Application is executed when application is already running")
            logging.warning("Application is executed when application is already running")
            ctypes.windll.user32.MessageBoxW(0, 
                "Application is already running", 
                "Instance Already Running", 
                0x40
            )
            sys.exit(1)
    except Exception as e:
        logging.error(f"Single instance check failed: {e}")
        print(f"Single instance check failed: {e}")
        sys.exit(1)

# Add system event monitoring
def system_event_monitor():
    """Monitor system events like lock/unlock"""
    while True:
        # Check if workstation is locked using a different method
        if ctypes.windll.user32.GetForegroundWindow() == 0:
            logging.info("Workstation locked - pausing activities")
            print("Workstation locked - pausing activities")
            global is_running
            is_running = False
            time.sleep(10)
        else:
            is_running = True
            time.sleep(5)

# Add interaction detection to menu items
def wrap_action(action):
    """Decorator to update interaction time for menu actions"""
    def wrapped(icon, item):
        action(icon, item)
    return wrapped

# root.mainloop()
# ----------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        # Check if another instance is running
        # if not check_single_instance():
        #     sys.exit(1)
        check_single_instance()
        
        initialize_ui()
            
        load_config()  # Load the interval from JSON
        
        # Reduce startup notifications to improve performance
        if not os.path.exists(os.path.join(app_dir, ".startup_shown")):
            show_notification(APP_NAME, "Starting application...")
            # Create a marker file to avoid showing notification on every startup
            with open(os.path.join(app_dir, ".startup_shown"), 'w') as f:
                f.write("1")
        
        # Start system tray in a separate thread
        if 'tray_thread' not in globals() or not tray_thread.is_alive():
            tray_thread = threading.Thread(target=run_system_tray, daemon=True)
            tray_thread.start()
        
        # Create system monitor first to ensure update_system_stats is defined
        system_monitor = create_system_monitor(canvas)
        system_monitor.place(relx=0.69, rely=0.98, anchor="sw")
        
        # Start update loops with staggered timing to prevent simultaneous updates
        root.after(100, update_mute_button)
        root.after(200, check_mouse_position)
        root.after(300, update_network_speed)
        
        # Only start system stats update if the function exists
        if 'update_system_stats' in globals():
            root.after(400, update_system_stats)
        else:
            logging.error("update_system_stats function not found")
            print("update_system_stats function not found")
        
        # Start screenshot thread
        screenshot_thread = threading.Thread(target=take_feedback_screenshot, daemon=True)
        screenshot_thread.start()
        
        # Start the periodic check
        # active_user_check() # Start the active user check
        activeuser_thread = threading.Thread(target=active_user_check, daemon=True)
        activeuser_thread.start()
        
        # upload logs 
        threading.Thread(target=upload_logs, daemon=True).start()
        threading.Thread(target=load_uploaded_cache, daemon=True).start()
        
        # Start folder check thread
        folder_check_thread = threading.Thread(target=schedule_folder_check, daemon=True)
        folder_check_thread.start()
    
        # check for the new updates
        clean_partial_files()
        # Start a background thread to check for updates at regular intervals
        threading.Thread(target=start_auto_update_checker, daemon=True).start()
        
        # Run the shortcut listener in a separate thread
        shortcut_thread = threading.Thread(target=listen_for_shortcuts, daemon=True)
        shortcut_thread.start()
        
        # Add system event monitoring
        system_monitor_thread = threading.Thread(target=system_event_monitor, daemon=True)
        system_monitor_thread.start()
        
        # Start the main loop
        root.mainloop()
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt detected. Exiting gracefully.")
        show_notification(APP_NAME, "Keyboard interrupt detected. Exiting gracefully.")
        print("Keyboard interrupt detected. Exiting gracefully.")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Error in main loop: {e}")
        show_notification(APP_NAME, f"Error in main loop: {e}")
        print(f"Error in main loop: {e}")
        sys.exit(1)
    finally:
        # Clean up system tray if it exists
        if system_tray_icon is not None:
            system_tray_icon.stop()
        root.quit()
        sys.exit(1)
