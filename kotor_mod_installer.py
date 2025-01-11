import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import shutil
import subprocess
import py7zr
import rarfile
import zipfile
from pathlib import Path

class ModInstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KOTOR Mod Installer")
        
        # Configure window
        self.root.geometry("800x800")
        self.root.minsize(600, 400)
        
        # Create main frame with padding
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Loose-file mods frame
        loose_frame = ttk.LabelFrame(main_frame, text="Loose-File Mods", padding="5")
        loose_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        loose_frame.columnconfigure(0, weight=1)
        
        self.loose_files_listbox = tk.Listbox(loose_frame, width=70, height=10, selectmode=tk.EXTENDED)
        self.loose_files_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        loose_scroll = ttk.Scrollbar(loose_frame, orient=tk.VERTICAL, command=self.loose_files_listbox.yview)
        loose_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.loose_files_listbox.configure(yscrollcommand=loose_scroll.set)
        
        # Loose-file mod buttons
        loose_buttons = ttk.Frame(loose_frame)
        loose_buttons.grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Button(loose_buttons, text="↑", width=3, command=lambda: self.move_item(self.loose_files_listbox, -1)).grid(row=0, column=0, padx=2)
        ttk.Button(loose_buttons, text="↓", width=3, command=lambda: self.move_item(self.loose_files_listbox, 1)).grid(row=0, column=1, padx=2)
        
        # TSLPatcher mods frame
        tsl_frame = ttk.LabelFrame(main_frame, text="TSLPatcher Mods", padding="5")
        tsl_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        tsl_frame.columnconfigure(0, weight=1)
        
        self.tsl_files_listbox = tk.Listbox(tsl_frame, width=70, height=10, selectmode=tk.EXTENDED)
        self.tsl_files_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        tsl_scroll = ttk.Scrollbar(tsl_frame, orient=tk.VERTICAL, command=self.tsl_files_listbox.yview)
        tsl_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tsl_files_listbox.configure(yscrollcommand=tsl_scroll.set)
        
        # TSLPatcher mod buttons
        tsl_buttons = ttk.Frame(tsl_frame)
        tsl_buttons.grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Button(tsl_buttons, text="↑", width=3, command=lambda: self.move_item(self.tsl_files_listbox, -1)).grid(row=0, column=0, padx=2)
        ttk.Button(tsl_buttons, text="↓", width=3, command=lambda: self.move_item(self.tsl_files_listbox, 1)).grid(row=0, column=1, padx=2)
        
        # Main buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(button_frame, text="Add Loose-File Mods", command=self.add_loose_files).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Add TSLPatcher Mods", command=self.add_tsl_files).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Clear All", command=self.clear_all).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, text="Install Mods", command=self.install_mods).grid(row=0, column=4, padx=5)
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(progress_frame, length=400, mode='determinate', variable=self.progress_var)
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Drag and drop mod files or use the Add buttons...")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, wraplength=700)
        self.status_label.grid(row=4, column=0, pady=5)
        
        # Setup directories
        self.setup_directories()
        
        # Setup drag and drop
        self.setup_drag_drop()

    def move_item(self, listbox, direction):
        """Move selected item up or down in the listbox"""
        selected = listbox.curselection()
        if not selected:
            return
        
        for pos in selected:
            if direction == -1 and pos == 0:  # Can't move up
                continue
            if direction == 1 and pos == listbox.size() - 1:  # Can't move down
                continue
            
            text = listbox.get(pos)
            listbox.delete(pos)
            new_pos = pos + direction
            listbox.insert(new_pos, text)
            listbox.selection_set(new_pos)

    def setup_directories(self):
        """Create necessary directories if they don't exist"""
        directories = ['dummy_kotor', 'dummy_kotor/Override', 'dummy_kotor/Modules',
                      'final_override', 'TSLPatcher', 'patcher_mods']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        self.loose_files_listbox.drop_target_register(DND_FILES)
        self.loose_files_listbox.dnd_bind('<<Drop>>', self.drop_loose_files)
        
        self.tsl_files_listbox.drop_target_register(DND_FILES)
        self.tsl_files_listbox.dnd_bind('<<Drop>>', self.drop_tsl_files)

    def add_loose_files(self):
        """Add loose-file mods through file dialog"""
        files = filedialog.askopenfilenames(
            filetypes=[("Archive files", "*.zip;*.7z;*.rar"), ("All files", "*.*")])
        for file in files:
            self.loose_files_listbox.insert(tk.END, file)

    def add_tsl_files(self):
        """Add TSLPatcher mods through file dialog"""
        files = filedialog.askopenfilenames(
            filetypes=[("Archive files", "*.zip;*.7z;*.rar"), ("All files", "*.*")])
        for file in files:
            self.tsl_files_listbox.insert(tk.END, file)

    def remove_selected(self):
        """Remove selected items from both listboxes"""
        for i in reversed(self.loose_files_listbox.curselection()):
            self.loose_files_listbox.delete(i)
        for i in reversed(self.tsl_files_listbox.curselection()):
            self.tsl_files_listbox.delete(i)

    def drop_loose_files(self, event):
        """Handle files dropped onto loose-file listbox"""
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if file.lower().endswith(('.zip', '.7z', '.rar')):
                self.loose_files_listbox.insert(tk.END, file)

    def drop_tsl_files(self, event):
        """Handle files dropped onto TSLPatcher listbox"""
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if file.lower().endswith(('.zip', '.7z', '.rar')):
                self.tsl_files_listbox.insert(tk.END, file)

    def clear_all(self):
        """Clear both listboxes"""
        self.loose_files_listbox.delete(0, tk.END)
        self.tsl_files_listbox.delete(0, tk.END)
        self.status_var.set("All files cleared. Ready for new mods...")

    def extract_archive(self, archive_path, extract_path):
        """Extract various archive formats"""
        try:
            if archive_path.lower().endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
            elif archive_path.lower().endswith('.7z'):
                with py7zr.SevenZipFile(archive_path, 'r') as sz:
                    sz.extractall(extract_path)
            elif archive_path.lower().endswith('.rar'):
                with rarfile.RarFile(archive_path, 'r') as rf:
                    rf.extractall(extract_path)
            return True
        except Exception as e:
            self.status_var.set(f"Error extracting {os.path.basename(archive_path)}: {str(e)}")
            return False

    def flatten_directory(self, source_dir, dest_dir):
        """Recursively copy all files from source_dir to dest_dir, flattening the directory structure"""
        self.status_var.set(f"Processing directory: {os.path.basename(source_dir)}")
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                src_path = os.path.join(root, file)
                # Skip dialog.tlk as it doesn't go in Override
                if file.lower() == 'dialog.tlk':
                    continue
                # Get relative path from source_dir to handle nested files
                rel_path = os.path.relpath(src_path, source_dir)
                # If file is in a subdirectory, just take the filename
                dest_file = os.path.basename(rel_path)
                dest_path = os.path.join(dest_dir, dest_file)
                self.status_var.set(f"Copying: {dest_file}")
                # Copy file to destination, overwriting if exists
                shutil.copy2(src_path, dest_path)
                self.root.update()

    def combine_mods(self):
        """Combine all mods into final Android directory structure"""
        # Create Android directory structure
        android_dir = os.path.join('final_package', 'Android', 'data', 'com.aspyr.swkotor', 'files')
        override_dir = os.path.join(android_dir, 'Override')
        modules_dir = os.path.join(android_dir, 'Modules')
        
        # Clean up existing final_package directory
        if os.path.exists('final_package'):
            shutil.rmtree('final_package')
        
        # Create directories
        os.makedirs(override_dir, exist_ok=True)
        os.makedirs(modules_dir, exist_ok=True)
        
        # Copy TSLPatcher results first
        if os.path.exists('dummy_kotor/Override'):
            self.status_var.set("Processing TSLPatcher results...")
            self.flatten_directory('dummy_kotor/Override', override_dir)
        if os.path.exists('dummy_kotor/Modules'):
            self.status_var.set("Processing TSLPatcher modules...")
            self.flatten_directory('dummy_kotor/Modules', modules_dir)
        
        # Copy loose-file mods last to ensure patches override their base mods
        if os.path.exists('final_override'):
            self.status_var.set("Processing loose-file mods...")
            for item in os.listdir('final_override'):
                src_path = os.path.join('final_override', item)
                if os.path.isfile(src_path):
                    if item.lower() == 'dialog.tlk':
                        self.status_var.set("Copying dialog.tlk...")
                        shutil.copy2(src_path, os.path.join(android_dir, item))
                    else:
                        self.status_var.set(f"Copying file: {item}")
                        shutil.copy2(src_path, os.path.join(override_dir, item))
                elif os.path.isdir(src_path):
                    # Look for files in Override subdirectory
                    override_subdir = os.path.join(src_path, 'Override')
                    if os.path.exists(override_subdir):
                        self.flatten_directory(override_subdir, override_dir)
                    else:
                        # If no Override subdirectory, process the directory itself
                        self.flatten_directory(src_path, override_dir)
                self.root.update()

    def install_mods(self):
        """Main installation process"""
        self.progress_var.set(0)
        total_steps = self.loose_files_listbox.size() + self.tsl_files_listbox.size() + 3
        current_step = 0
        
        try:
            # Process loose-file mods
            self.status_var.set("Installing loose-file mods...")
            for i in range(self.loose_files_listbox.size()):
                file_path = self.loose_files_listbox.get(i)
                if self.extract_archive(file_path, 'final_override'):
                    self.status_var.set(f"Extracted {os.path.basename(file_path)}")
                current_step += 1
                self.progress_var.set((current_step / total_steps) * 100)
                self.root.update()
            
            # Copy dialog.tlk to dummy_kotor
            if os.path.exists('final_override/dialog.tlk'):
                shutil.copy2('final_override/dialog.tlk', 'dummy_kotor/dialog.tlk')
            
            # Process TSLPatcher mods
            self.status_var.set("Installing TSLPatcher mods...")
            for i in range(self.tsl_files_listbox.size()):
                file_path = self.tsl_files_listbox.get(i)
                mod_name = os.path.splitext(os.path.basename(file_path))[0]
                extract_path = os.path.join('patcher_mods', mod_name)
                
                if self.extract_archive(file_path, extract_path):
                    self.status_var.set(f"Running TSLPatcher for {mod_name}")
                    
                    # Find and run TSLPatcher
                    for root, dirs, files in os.walk(extract_path):
                        if 'tslpatchdata' in dirs:
                            tsl_dir = os.path.dirname(root)
                            if os.path.exists(os.path.join(tsl_dir, 'TSLPatcher.exe')):
                                try:
                                    subprocess.run([os.path.join(tsl_dir, 'TSLPatcher.exe'), 
                                                 os.path.abspath('dummy_kotor')],
                                                 check=True)
                                except subprocess.CalledProcessError as e:
                                    self.status_var.set(f"Error running TSLPatcher for {mod_name}: {str(e)}")
                
                current_step += 1
                self.progress_var.set((current_step / total_steps) * 100)
                self.root.update()
            
            # Combine everything into final package
            self.status_var.set("Creating final package...")
            self.combine_mods()
            current_step += 1
            self.progress_var.set(100)
            
            self.status_var.set("Installation complete! Files are in final_package/Android/data/com.aspyr.swkotor/files/")
        except Exception as e:
            self.status_var.set(f"Error during installation: {str(e)}")

def main():
    root = TkinterDnD.Tk()
    app = ModInstallerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()