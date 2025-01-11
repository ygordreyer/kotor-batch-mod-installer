import os
import shutil
from pathlib import Path

def cleanup():
    """Clean up temporary directories and files"""
    print("Cleaning up temporary files and directories...")
    
    # Directories to clean
    temp_dirs = [
        'dummy_kotor',
        'final_override',
        'TSLPatcher',
        'patcher_mods'
    ]
    
    # Clean each directory
    for dir_name in temp_dirs:
        if os.path.exists(dir_name):
            print(f"Removing {dir_name}...")
            try:
                shutil.rmtree(dir_name)
                print(f"✓ Removed {dir_name}")
            except Exception as e:
                print(f"❌ Error removing {dir_name}: {str(e)}")
    
    # Check if final_package exists
    if os.path.exists('final_package'):
        print("\nFound final_package directory.")
        print("This directory contains your mod files ready for Android.")
        response = input("Do you want to keep final_package? (y/n): ").lower()
        if response == 'n':
            try:
                shutil.rmtree('final_package')
                print("✓ Removed final_package")
            except Exception as e:
                print(f"❌ Error removing final_package: {str(e)}")
        else:
            print("✓ Kept final_package")
    
    print("\nCleanup complete!")
    
    # Print reminder about copying files
    if os.path.exists('final_package'):
        print("\nReminder: Copy the contents of final_package/Android/data/com.aspyr.swkotor/files/")
        print("to the same location on your Android device.")

if __name__ == "__main__":
    cleanup()