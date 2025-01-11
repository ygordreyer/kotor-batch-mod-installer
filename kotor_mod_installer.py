import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import shutil
import subprocess
import py7zr
import rarfile
import zipfile
from pathlib import Path
import datetime

class ModInstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KOTOR Mod Installer")
        
        # Initialize variables first
        self.output_path = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Desktop", "KOTOR_Mods"))
        self.output_path.trace_add("write", self.update_directory_info)  # Update info when path changes
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Drag and drop mod files or use the Add buttons...")
        self.log_expanded = tk.BooleanVar(value=False)
        
        # Show initial warning
        self.show_directory_info()
        
        # Configure window
        self.root.geometry("1000x800")
        self.root.minsize(800, 600)
        
        # Create main frame with padding
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Output directory selection
        output_frame = ttk.LabelFrame(main_frame, text="Output Directory", padding="5")
        output_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="Output:").grid(row=0, column=0, padx=5)
        ttk.Entry(output_frame, textvariable=self.output_path).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        path_buttons = ttk.Frame(output_frame)
        path_buttons.grid(row=0, column=2, padx=5)
        
        browse_btn = ttk.Button(path_buttons, text="Browse", command=self.browse_output)
        browse_btn.pack(side=tk.LEFT, padx=2)
        self.create_tooltip(browse_btn, "Select where to save mod files")
        
        open_work_btn = ttk.Button(path_buttons, text="Open Work Dir", command=lambda: self.open_directory("work"))
        open_work_btn.pack(side=tk.LEFT, padx=2)
        self.create_tooltip(open_work_btn, "Open work directory in File Explorer")
        
        open_final_btn = ttk.Button(path_buttons, text="Open Final Dir", command=lambda: self.open_directory("final"))
        open_final_btn.pack(side=tk.LEFT, padx=2)
        self.create_tooltip(open_final_btn, "Open final package directory in File Explorer")
        
        # Directory structure info (with label stored as instance variable)
        self.dir_info_label = ttk.Label(output_frame, justify=tk.LEFT)
        self.dir_info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        self.update_directory_info()  # Initial update of directory info
        
        # Loose-file mods frame
        loose_frame = ttk.LabelFrame(main_frame, text="Loose-File Mods", padding="5")
        loose_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        loose_frame.columnconfigure(0, weight=1)
        
        self.loose_files_listbox = tk.Listbox(loose_frame, width=70, height=10, selectmode=tk.EXTENDED)
        self.loose_files_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        loose_scroll = ttk.Scrollbar(loose_frame, orient=tk.VERTICAL, command=self.loose_files_listbox.yview)
        loose_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.loose_files_listbox.configure(yscrollcommand=loose_scroll.set)
        
        # Loose-file mod buttons
        loose_buttons = ttk.Frame(loose_frame)
        loose_buttons.grid(row=1, column=0, columnspan=2, pady=5)
        up_btn = ttk.Button(loose_buttons, text="↑", width=3, command=lambda: self.move_item(self.loose_files_listbox, -1))
        up_btn.grid(row=0, column=0, padx=2)
        self.create_tooltip(up_btn, "Move selected mod up in load order")
        
        down_btn = ttk.Button(loose_buttons, text="↓", width=3, command=lambda: self.move_item(self.loose_files_listbox, 1))
        down_btn.grid(row=0, column=1, padx=2)
        self.create_tooltip(down_btn, "Move selected mod down in load order")
        
        # TSLPatcher mods frame
        tsl_frame = ttk.LabelFrame(main_frame, text="TSLPatcher Mods", padding="5")
        tsl_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        tsl_frame.columnconfigure(0, weight=1)
        
        self.tsl_files_listbox = tk.Listbox(tsl_frame, width=70, height=10, selectmode=tk.EXTENDED)
        self.tsl_files_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        tsl_scroll = ttk.Scrollbar(tsl_frame, orient=tk.VERTICAL, command=self.tsl_files_listbox.yview)
        tsl_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tsl_files_listbox.configure(yscrollcommand=tsl_scroll.set)
        
        # TSLPatcher mod buttons
        tsl_buttons = ttk.Frame(tsl_frame)
        tsl_buttons.grid(row=1, column=0, columnspan=2, pady=5)
        tsl_up_btn = ttk.Button(tsl_buttons, text="↑", width=3, command=lambda: self.move_item(self.tsl_files_listbox, -1))
        tsl_up_btn.grid(row=0, column=0, padx=2)
        self.create_tooltip(tsl_up_btn, "Move selected mod up in load order")
        
        tsl_down_btn = ttk.Button(tsl_buttons, text="↓", width=3, command=lambda: self.move_item(self.tsl_files_listbox, 1))
        tsl_down_btn.grid(row=0, column=1, padx=2)
        self.create_tooltip(tsl_down_btn, "Move selected mod down in load order")
        
        # Main buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=10)
        
        add_loose_btn = ttk.Button(button_frame, text="Add Loose-File Mods", command=self.add_loose_files)
        add_loose_btn.grid(row=0, column=0, padx=5)
        self.create_tooltip(add_loose_btn, "Add mods that don't use TSLPatcher")
        
        add_tsl_btn = ttk.Button(button_frame, text="Add TSLPatcher Mods", command=self.add_tsl_files)
        add_tsl_btn.grid(row=0, column=1, padx=5)
        self.create_tooltip(add_tsl_btn, "Add mods that use TSLPatcher")
        
        remove_btn = ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected)
        remove_btn.grid(row=0, column=2, padx=5)
        self.create_tooltip(remove_btn, "Remove selected mods from the lists")
        
        clear_btn = ttk.Button(button_frame, text="Clear All", command=self.clear_all)
        clear_btn.grid(row=0, column=3, padx=5)
        self.create_tooltip(clear_btn, "Clear all mod lists")
        
        install_btn = ttk.Button(button_frame, text="Install Mods", command=self.install_mods)
        install_btn.grid(row=0, column=4, padx=5)
        self.create_tooltip(install_btn, "Install all mods in the lists")
        
        clean_btn = ttk.Button(button_frame, text="Clean Work Files", command=self.clean_work_files)
        clean_btn.grid(row=0, column=5, padx=5)
        self.create_tooltip(clean_btn, "Delete temporary work files (not your mod files)")
        
        help_btn = ttk.Button(button_frame, text="Help", command=self.show_directory_info)
        help_btn.grid(row=0, column=6, padx=5)
        self.create_tooltip(help_btn, "Show directory structure information")
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(progress_frame, length=400, mode='determinate', variable=self.progress_var)
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Drag and drop mod files or use the Add buttons...")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, wraplength=700)
        self.status_label.grid(row=5, column=0, pady=5)
        
        # Log frame (collapsible)
        self.log_expanded = tk.BooleanVar(value=False)
        log_header = ttk.Frame(main_frame)
        log_header.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(10,0))
        
        self.toggle_button = ttk.Button(log_header, text="▼ Show Log", command=self.toggle_log)
        self.toggle_button.grid(row=0, column=0, sticky=tk.W)
        
        self.log_frame = ttk.Frame(main_frame)
        self.log_frame.grid(row=7, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.log_frame.grid_remove()  # Initially hidden
        
        self.log_text = tk.Text(self.log_frame, height=10, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scroll = ttk.Scrollbar(self.log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=log_scroll.set)
        
        # Setup directories
        self.setup_directories()
        
        # Setup drag and drop
        self.setup_drag_drop()

    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(tooltip, text=text, justify=tk.LEFT,
                            relief=tk.SOLID, borderwidth=1)
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            widget.tooltip = tooltip
            widget.bind('<Leave>', lambda e: hide_tooltip())
            
        widget.bind('<Enter>', show_tooltip)

    def update_directory_info(self, *args):
        """Update directory structure info text"""
        info_text = (
            "Directory Structure:\n"
            "• Work Files: {output}/work/\n"
            "• Final Package: {output}/Android/data/com.aspyr.swkotor/files/"
        ).format(output=self.output_path.get())
        self.dir_info_label.configure(text=info_text)

    def browse_output(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(
            initialdir=self.output_path.get(),
            title="Select Output Directory"
        )
        if directory:
            self.output_path.set(directory)
            # Directory info will update automatically due to trace

    def open_directory(self, dir_type):
        """Open directory in File Explorer"""
        if dir_type == "work":
            path = os.path.join(self.output_path.get(), "work")
        else:  # final
            path = os.path.join(self.output_path.get(), "Android/data/com.aspyr.swkotor/files")
        
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showinfo("Directory Not Found", 
                f"The {dir_type} directory hasn't been created yet.\n"
                "It will be created when you install mods.")

    def show_directory_info(self):
        """Show information about directory structure"""
        info_text = (
            "KOTOR Mod Installer Directory Structure\n\n"
            "This installer will create two main directories:\n\n"
            "1. Work Directory:\n"
            "   • Location: {output}/work/\n"
            "   • Purpose: Temporary files used during installation\n"
            "   • Content: Extracted mods and TSLPatcher files\n"
            "   • Note: Can be safely deleted after successful installation\n\n"
            "2. Final Package:\n"
            "   • Location: {output}/Android/data/com.aspyr.swkotor/files/\n"
            "   • Purpose: Ready-to-use mod files for your phone\n"
            "   • Content: Properly organized Override and Modules folders\n"
            "   • Note: This is what you copy to your phone\n\n"
            "The work directory will NOT be automatically deleted.\n"
            "You can use the 'Clean Work Files' button to remove it when you're done."
        ).format(output=self.output_path.get())
        
        messagebox.showinfo("Directory Structure", info_text)

    def toggle_log(self):
        """Toggle the visibility of the log frame"""
        if self.log_expanded.get():
            self.log_frame.grid_remove()
            self.toggle_button.configure(text="▼ Show Log")
        else:
            self.log_frame.grid()
            self.toggle_button.configure(text="▲ Hide Log")
        self.log_expanded.set(not self.log_expanded.get())

    def log(self, message):
        """Add a message to the log with timestamp"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()

    def setup_directories(self):
        """Create necessary directories if they don't exist"""
        work_dir = os.path.join(self.output_path.get(), "work")
        directories = [
            os.path.join(work_dir, d) for d in [
                'dummy_kotor/Override',
                'dummy_kotor/Modules',
                'final_override',
                'TSLPatcher',
                'patcher_mods'
            ]
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        self.log(f"Created working directories in: {work_dir}")

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
            self.log(f"Added loose-file mod: {os.path.basename(file)}")

    def add_tsl_files(self):
        """Add TSLPatcher mods through file dialog"""
        files = filedialog.askopenfilenames(
            filetypes=[("Archive files", "*.zip;*.7z;*.rar"), ("All files", "*.*")])
        for file in files:
            self.tsl_files_listbox.insert(tk.END, file)
            self.log(f"Added TSLPatcher mod: {os.path.basename(file)}")

    def remove_selected(self):
        """Remove selected items from both listboxes"""
        for i in reversed(self.loose_files_listbox.curselection()):
            self.log(f"Removed loose-file mod: {self.loose_files_listbox.get(i)}")
            self.loose_files_listbox.delete(i)
        for i in reversed(self.tsl_files_listbox.curselection()):
            self.log(f"Removed TSLPatcher mod: {self.tsl_files_listbox.get(i)}")
            self.tsl_files_listbox.delete(i)

    def drop_loose_files(self, event):
        """Handle files dropped onto loose-file listbox"""
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if file.lower().endswith(('.zip', '.7z', '.rar')):
                self.loose_files_listbox.insert(tk.END, file)
                self.log(f"Dropped loose-file mod: {os.path.basename(file)}")

    def drop_tsl_files(self, event):
        """Handle files dropped onto TSLPatcher listbox"""
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if file.lower().endswith(('.zip', '.7z', '.rar')):
                self.tsl_files_listbox.insert(tk.END, file)
                self.log(f"Dropped TSLPatcher mod: {os.path.basename(file)}")

    def clear_all(self):
        """Clear both listboxes"""
        self.loose_files_listbox.delete(0, tk.END)
        self.tsl_files_listbox.delete(0, tk.END)
        self.status_var.set("All files cleared. Ready for new mods...")
        self.log("Cleared all mod lists")

    def clean_work_files(self):
        """Clean up temporary work files with user confirmation"""
        work_dir = os.path.join(self.output_path.get(), "work")
        if os.path.exists(work_dir):
            if messagebox.askyesno("Clean Work Files", 
                "This will delete all temporary work files, but NOT your mod files or the final package.\n\n"
                "Do you want to continue?"):
                try:
                    shutil.rmtree(work_dir)
                    self.log("Cleaned up work directory")
                    messagebox.showinfo("Success", "Work files have been cleaned up")
                except Exception as e:
                    error_msg = f"Error cleaning work files: {str(e)}"
                    self.log(error_msg)
                    messagebox.showerror("Error", error_msg)
        else:
            messagebox.showinfo("Info", "No work files to clean")

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
            self.log(f"Extracted: {os.path.basename(archive_path)} to {extract_path}")
            return True
        except Exception as e:
            error_msg = f"Error extracting {os.path.basename(archive_path)}: {str(e)}"
            self.status_var.set(error_msg)
            self.log(error_msg)
            return False

    def flatten_directory(self, source_dir, dest_dir):
        """Recursively copy all files from source_dir to dest_dir, flattening the directory structure"""
        self.log(f"Flattening directory: {source_dir}")
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
                self.log(f"Copying: {rel_path} -> {dest_file}")
                # Copy file to destination, overwriting if exists
                shutil.copy2(src_path, dest_path)

    def combine_mods(self):
        """Combine all mods into final Android directory structure"""
        # Create Android directory structure
        android_dir = os.path.join(self.output_path.get(), "Android/data/com.aspyr.swkotor/files")
        override_dir = os.path.join(android_dir, "Override")
        modules_dir = os.path.join(android_dir, "Modules")
        
        self.log(f"\nCreating final package in: {android_dir}")
        
        # Clean up existing final_package directory
        if os.path.exists(android_dir):
            self.log("Cleaning up existing output directory")
            shutil.rmtree(android_dir)
        
        # Create directories
        os.makedirs(override_dir, exist_ok=True)
        os.makedirs(modules_dir, exist_ok=True)
        
        work_dir = os.path.join(self.output_path.get(), "work")
        
        # Copy TSLPatcher results first
        dummy_override = os.path.join(work_dir, "dummy_kotor/Override")
        dummy_modules = os.path.join(work_dir, "dummy_kotor/Modules")
        
        if os.path.exists(dummy_override):
            self.log("Processing TSLPatcher results...")
            self.flatten_directory(dummy_override, override_dir)
        if os.path.exists(dummy_modules):
            self.log("Processing TSLPatcher modules...")
            self.flatten_directory(dummy_modules, modules_dir)
        
        # Copy loose-file mods last to ensure patches override their base mods
        final_override = os.path.join(work_dir, "final_override")
        if os.path.exists(final_override):
            self.log("Processing loose-file mods...")
            for item in os.listdir(final_override):
                src_path = os.path.join(final_override, item)
                if os.path.isfile(src_path):
                    if item.lower() == 'dialog.tlk':
                        self.log("Copying dialog.tlk...")
                        shutil.copy2(src_path, os.path.join(android_dir, item))
                    else:
                        self.log(f"Copying file: {item}")
                        shutil.copy2(src_path, os.path.join(override_dir, item))
                elif os.path.isdir(src_path):
                    # Look for files in Override subdirectory
                    override_subdir = os.path.join(src_path, "Override")
                    if os.path.exists(override_subdir):
                        self.flatten_directory(override_subdir, override_dir)
                    else:
                        # If no Override subdirectory, process the directory itself
                        self.flatten_directory(src_path, override_dir)
        
        self.log("\nMod installation complete!")
        self.log(f"Files are ready in: {android_dir}")

    def install_mods(self):
        """Main installation process"""
        self.progress_var.set(0)
        total_steps = self.loose_files_listbox.size() + self.tsl_files_listbox.size() + 3
        current_step = 0
        
        try:
            work_dir = os.path.join(self.output_path.get(), "work")
            
            # Process loose-file mods
            self.status_var.set("Installing loose-file mods...")
            final_override = os.path.join(work_dir, "final_override")
            for i in range(self.loose_files_listbox.size()):
                file_path = self.loose_files_listbox.get(i)
                if self.extract_archive(file_path, final_override):
                    self.status_var.set(f"Extracted {os.path.basename(file_path)}")
                current_step += 1
                self.progress_var.set((current_step / total_steps) * 100)
            
            # Copy dialog.tlk to dummy_kotor
            dialog_tlk = os.path.join(final_override, "dialog.tlk")
            dummy_kotor = os.path.join(work_dir, "dummy_kotor")
            if os.path.exists(dialog_tlk):
                shutil.copy2(dialog_tlk, os.path.join(dummy_kotor, "dialog.tlk"))
            
            # Process TSLPatcher mods
            self.status_var.set("Installing TSLPatcher mods...")
            for i in range(self.tsl_files_listbox.size()):
                file_path = self.tsl_files_listbox.get(i)
                mod_name = os.path.splitext(os.path.basename(file_path))[0]
                extract_path = os.path.join(work_dir, "patcher_mods", mod_name)
                
                if self.extract_archive(file_path, extract_path):
                    self.status_var.set(f"Running TSLPatcher for {mod_name}")
                    
                    # Find and run TSLPatcher
                    for root, dirs, files in os.walk(extract_path):
                        if 'tslpatchdata' in dirs:
                            tsl_dir = os.path.dirname(root)
                            if os.path.exists(os.path.join(tsl_dir, 'TSLPatcher.exe')):
                                try:
                                    subprocess.run([os.path.join(tsl_dir, 'TSLPatcher.exe'), 
                                                 os.path.abspath(dummy_kotor)],
                                                 check=True)
                                except subprocess.CalledProcessError as e:
                                    error_msg = f"Error running TSLPatcher for {mod_name}: {str(e)}"
                                    self.status_var.set(error_msg)
                                    self.log(error_msg)
                
                current_step += 1
                self.progress_var.set((current_step / total_steps) * 100)
            
            # Combine everything into final package
            self.status_var.set("Creating final package...")
            self.combine_mods()
            current_step += 1
            self.progress_var.set(100)
            
            final_path = os.path.join(self.output_path.get(), "Android/data/com.aspyr.swkotor/files")
            self.status_var.set(
                f"Installation complete!\n\n"
                f"Files are in:\n{final_path}\n\n"
                f"Work files are in:\n{work_dir}\n\n"
                "You can use 'Clean Work Files' to remove temporary files after confirming everything works."
            )
            
        except Exception as e:
            error_msg = f"Error during installation: {str(e)}"
            self.status_var.set(error_msg)
            self.log(error_msg)

def main():
    root = TkinterDnD.Tk()
    app = ModInstallerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()