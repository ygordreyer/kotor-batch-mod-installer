# Knights of the Old Republic Mod Installer

A graphical tool for installing KOTOR mods on Android devices, supporting both loose-file mods and TSLPatcher mods.

## Features

- Drag & drop interface for mod files
- Supports .zip, .7z, and .rar archives
- Handles both loose-file mods and TSLPatcher mods
- Maintains proper installation order
- Shows installation progress
- Creates Android-ready file structure
- Handles nested directories and file organization
- Supports mod reordering with up/down buttons
- Collapsible log area with timestamps
- Quick access to work and final directories
- Tooltips for all buttons

## Requirements

- Python 3.8 or higher
- Required Python packages (install using `pip install -r requirements.txt`):
  - py7zr
  - rarfile
  - tkinterdnd2

## Installation

### Quick Start
1. Download this repository
2. Double-click `run_installer.bat` to:
   - Install required Python packages
   - Launch the installer

### Manual Installation
1. Clone or download this repository
2. Install Python if you haven't already
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the installer using either method:
   ```bash
   # Option 1: Using the batch file
   Double-click run_installer.bat
   
   # Option 2: Using Python directly
   python kotor_mod_installer.py
   ```

2. Add mods using either method:
   - Drag and drop mod files into the appropriate box
   - Use the "Add" buttons to select files

3. Arrange mods in the desired installation order:
   - Use the ↑↓ buttons to reorder mods
   - Loose-file mods: Drop in order of installation
   - TSLPatcher mods: Drop in order of installation

4. Click "Install Mods" to begin the installation process

5. When complete, copy the contents of `final_package/Android/data/com.aspyr.swkotor/files/` to your phone

## Directory Structure

The installer creates the following directory structure:
```
final_package/
└── Android/
    └── data/
        └── com.aspyr.swkotor/
            └── files/
                ├── dialog.tlk
                ├── Override/
                │   └── (mod files)
                └── Modules/
                    └── (module files)
```

## Troubleshooting

- If a TSLPatcher mod fails to install, check that:
  - The archive contains a `tslpatchdata` folder
  - TSLPatcher.exe is present
  - The mod's changes.ini file exists

- For .rar files, ensure you have WinRAR installed on Windows or unrar installed on Linux/Mac

- If files appear in the wrong location:
  1. Check the mod's archive structure
  2. Ensure the mod has an Override directory
  3. Try reordering mods if there are conflicts

## Credits

This tool was created to automate the KOTOR modding process and is based on the modding guide from https://kotor.neocities.org/modding/mod_builds/k1/spoiler-free_mobile


![kotor tool](https://github.com/user-attachments/assets/25237738-526e-49c8-9844-eecca7cd19a1)
