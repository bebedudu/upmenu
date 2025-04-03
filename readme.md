# UpMenu - Advanced Windows Menu Utility

## Overview

UpMenu is a comprehensive Windows utility that provides a customizable menu system with various productivity features. It offers quick access to applications, system controls, and utility functions through a sleek, modern interface. Designed to boost productivity and streamline your workflow, UpMenu floats at the top of your screen when needed and stays out of your way when not in use.

## Features

### Core Features
- **Customizable Menu System**: Access your favorite applications and tools from a convenient overlay menu
- **Hotkey Support**: Configurable keyboard shortcuts for all major functions
- **Screenshot Capability**: Take and manage screenshots with customizable intervals
- **System Monitoring**: Track system performance metrics including CPU, RAM, and network usage
- **Application Launcher**: Quick access to your favorite applications with customizable buttons
- **Volume Control**: Easily adjust system volume and mute/unmute with a single click
- **System Tray Integration**: Access UpMenu functions from the system tray even when the menu is hidden
- **Auto-startup Option**: Configure UpMenu to launch on system startup
- **Multi-page Interface**: Organized layout with different pages for various functions

### Additional Features
- **Media Controls**: Play, pause, and skip through media on supported applications
- **Brightness Control**: Adjust screen brightness directly from the menu
- **System Actions**: Quick access to shutdown, restart, lock screen, and show desktop
- **Window Management**: List, switch between, and manage open windows
- **Search Integration**: Search the web directly from the menu
- **Bookmarks Manager**: Save and access your favorite websites
- **Auto-Update System**: Stay up-to-date with the latest features and improvements
- **Calendar Widget**: Quick access to date and calendar information
- **Network Speed Monitor**: Real-time display of upload and download speeds
- **Customizable Appearance**: Modern, sleek interface with rounded corners

## Installation

1. Download the latest release from the [Download Setup](https://github.com/bebedudu/upmenu/releases/download/v0.0.5/MyUpmenuSetup.exe)  or [New Releases](https://github.com/bebedudu/upmenu/releases)
2. Run the installer and follow the instructions to install UpMenu
3. The menu will appear when you move your mouse to the top center of the screen

## Usage

### Main Controls

- **Show/Hide Menu**: Press `Ctrl+Alt+M` (default) or move mouse to top of screen
- **Take Screenshot**: Press `Ctrl+Alt+S` (default)
- **Open Calculator**: Press `Ctrl+Alt+C` (default)
- **Open Homepage**: Press `Ctrl+Alt+H` (default)
- **Restart Program**: Press `Ctrl+Alt+R` (default)
- **Toggle Brightness**: Press `Ctrl+Alt+B` (default)
- **Toggle Keyboard**: Press `Ctrl+Alt+K` (default)

### Navigation

- Use the left and right arrow buttons to navigate between pages
- First page: Search, media controls, and system actions
- Second page: Application launcher and window management
- Third page: System monitoring and additional tools

### Adding Applications

1. Navigate to the second page of the menu
2. Click the "+" button in the application launcher section
3. Select the executable file from the file dialog
4. Enter a custom name for the application
5. The application will appear as a button in the launcher

### Managing Windows

1. Navigate to the window management section
2. View a list of all open windows
3. Click on a window name to switch to it
4. Use the provided buttons to minimize, maximize, or close the selected window

### System Tray

Right-click the UpMenu icon in the system tray to:
- Show/Hide the menu
- Toggle "Run on Startup" option
- Take a screenshot
- Toggle keyboard shortcuts
- Access developer information
- Restore default settings
- Open configuration files
- Toggle feedback screenshots
- Check for updates
- Restart or exit the application

## Configuration

UpMenu stores its configuration in several files:

### upmenuconfig.json
- Current version
- Screenshot interval and settings
- Startup preferences
- User applications
- System monitoring settings

### upmenushortcuts.json
- Keyboard shortcut mappings
- Customize shortcuts for all major functions

### upmenubookmarks.json
- Saved website bookmarks
- Quick access to favorite sites

## Customization

### Keyboard Shortcuts
1. Open the shortcuts configuration file
2. Modify the key combinations for various functions
3. Save the file and restart UpMenu

### Application Launcher
- Add your most-used applications for quick access
- Remove applications you no longer need
- Organize your workflow with your preferred tools

## System Requirements

- Windows 10 or later
- .NET Framework 4.5 or later
- 80MB free disk space
- Internet connection for updates and some features

### For Source Code:
- Python 3.6+
- Required Python packages:
  - pystray
  - pillow
  - pyautogui
  - pynput
  - psutil
  - requests
  - tkinter
  - tkcalendar
  - pygetwindow
  - pycaw
  - and others as listed in the imports

## Troubleshooting

### Common Issues
- **Menu doesn't appear**: Ensure you're moving the mouse to the top center of the screen
- **Hotkeys don't work**: Check for conflicts with other applications
- **High CPU usage**: Adjust the screenshot interval in settings

### Logs
- Check the `upmenuerror.log` file for detailed error information
- Submit logs when reporting issues for faster resolution

## License

[License information]

## Support

For issues, feature requests, or questions:
- Please [open an issue](https://github.com/bebedudu/upmenu/issues) on the GitHub repository
- Include your system information and logs for faster resolution
- Check existing issues before creating a new one

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Version History

Current Version: 0.0.4
- Added system monitoring features
- Improved application launcher
- Enhanced window management
- Fixed various bugs and improved stability

Previous versions:
- 0.0.3: Added bookmarks and improved UI
- 0.0.2: Added window management and system tray features
- 0.0.1: Initial release with basic functionality

## Acknowledgements

- Thanks to all contributors and testers
- Special thanks to the open-source libraries that made this project possible 
