#!/usr/bin/env python3
"""
PNG to ICO Converter - GUI Application
A comprehensive PNG to ICO converter with batch processing capabilities.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import logging
from pathlib import Path
import configparser
from PIL import Image
import threading
import queue

class Config:
    """Configuration management for the application."""

    def __init__(self, config_file="config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.create_default_config()

    def create_default_config(self):
        """Create default configuration."""
        self.config.add_section('settings')
        self.config.set('settings', 'icon_sizes', '16,24,32,48,64,128,256')
        self.config.set('settings', 'default_output_dir', 'output')
        self.config.set('settings', 'batch_mode', 'false')
        self.config.set('settings', 'overwrite_existing', 'false')
        self.save_config()

    def save_config(self):
        """Save configuration to file."""
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def get_icon_sizes(self):
        """Get icon sizes as list of integers."""
        sizes_str = self.config.get('settings', 'icon_sizes', fallback='16,24,32,48,64,128,256')
        return [int(size.strip()) for size in sizes_str.split(',')]

    def get_default_output_dir(self):
        """Get default output directory."""
        return self.config.get('settings', 'default_output_dir', fallback='output')

    def get_batch_mode(self):
        """Get batch mode setting."""
        return self.config.getboolean('settings', 'batch_mode', fallback=False)

    def get_overwrite_existing(self):
        """Get overwrite existing files setting."""
        return self.config.getboolean('settings', 'overwrite_existing', fallback=False)

class ImageConverter:
    """Handles PNG to ICO conversion operations."""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def convert_png_to_ico(self, input_path, output_path=None, sizes=None, overwrite=False):
        """
        Convert PNG file to ICO format.

        Args:
            input_path (str): Path to input PNG file
            output_path (str, optional): Path to output ICO file
            sizes (list, optional): List of icon sizes to include
            overwrite (bool): Whether to overwrite existing files

        Returns:
            bool: True if conversion successful, False otherwise
        """
        try:
            if not os.path.exists(input_path):
                self.logger.error(f"Input file does not exist: {input_path}")
                return False

            # Open the PNG image
            with Image.open(input_path) as img:
                if img.format != 'PNG':
                    self.logger.error(f"Input file is not a PNG: {input_path}")
                    return False

                # Convert to RGBA if not already
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')

                # Determine output path
                if output_path is None:
                    input_name = Path(input_path).stem
                    output_path = f"{input_name}.ico"

                # Check if output file exists
                if os.path.exists(output_path) and not overwrite:
                    self.logger.warning(f"Output file already exists: {output_path}")
                    return False

                # Get icon sizes
                if sizes is None:
                    sizes = self.config.get_icon_sizes()

                # Create icon images for each size
                icon_images = []
                for size in sizes:
                    # Resize image maintaining aspect ratio
                    resized_img = self._resize_image(img, size)
                    icon_images.append(resized_img)

                # Save as ICO
                if len(icon_images) == 1:
                    icon_images[0].save(output_path, format='ICO')
                else:
                    icon_images[0].save(output_path, format='ICO', append_images=icon_images[1:])

                self.logger.info(f"Successfully converted {input_path} to {output_path}")
                return True

        except Exception as e:
            self.logger.error(f"Error converting {input_path}: {str(e)}")
            return False

    def _resize_image(self, img, size):
        """
        Resize image to fit within the given size while maintaining aspect ratio.

        Args:
            img: PIL Image object
            size (int): Target size (width and height)

        Returns:
            PIL Image: Resized image
        """
        # Calculate aspect ratio
        aspect_ratio = img.width / img.height

        if aspect_ratio > 1:
            # Image is wider than tall
            new_width = size
            new_height = int(size / aspect_ratio)
        else:
            # Image is taller than wide
            new_height = size
            new_width = int(size * aspect_ratio)

        # Resize image
        resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Create new square image with transparent background
        square_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))

        # Center the resized image
        x_offset = (size - new_width) // 2
        y_offset = (size - new_height) // 2
        square_img.paste(resized, (x_offset, y_offset), resized)

        return square_img

    def batch_convert(self, input_files, output_dir=None, sizes=None, overwrite=False, progress_callback=None):
        """
        Convert multiple PNG files to ICO format.

        Args:
            input_files (list): List of input PNG file paths
            output_dir (str, optional): Output directory
            sizes (list, optional): List of icon sizes
            overwrite (bool): Whether to overwrite existing files
            progress_callback (callable): Callback function for progress updates

        Returns:
            dict: Results with success/failure counts and details
        """
        results = {
            'total': len(input_files),
            'successful': 0,
            'failed': 0,
            'details': []
        }

        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for i, input_file in enumerate(input_files):
            try:
                input_path = Path(input_file)

                # Determine output path
                if output_dir:
                    output_path = os.path.join(output_dir, f"{input_path.stem}.ico")
                else:
                    output_path = f"{input_path.stem}.ico"

                # Convert the file
                success = self.convert_png_to_ico(str(input_path), output_path, sizes, overwrite)

                if success:
                    results['successful'] += 1
                    results['details'].append({
                        'file': str(input_path),
                        'status': 'success',
                        'output': output_path
                    })
                else:
                    results['failed'] += 1
                    results['details'].append({
                        'file': str(input_path),
                        'status': 'failed',
                        'error': 'Conversion failed'
                    })

            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'file': str(input_file),
                    'status': 'failed',
                    'error': str(e)
                })

            # Update progress
            if progress_callback:
                progress = (i + 1) / len(input_files) * 100
                progress_callback(progress, f"Processing: {Path(input_file).name}")

        return results

class PNGtoICOConverter:
    """Main GUI application for PNG to ICO conversion."""

    def __init__(self, root):
        self.root = root
        self.root.title("PNG to ICO Converter")
        self.root.geometry("1000x700")  # Increased size for preview pane
        self.root.resizable(True, True)

        # Initialize components
        self.config = Config()
        self.converter = ImageConverter(self.config)
        self.setup_logging()

        # Preview image reference (to prevent garbage collection)
        self.preview_photo = None

        # Queue for thread communication
        self.queue = queue.Queue()

        # Create GUI
        self.create_widgets()
        self.load_settings()

        # Check queue periodically
        self.root.after(100, self.check_queue)

    def load_settings(self):
        """Load settings from config and populate UI."""
        try:
            # Load icon sizes
            sizes = self.config.get_icon_sizes()
            self.sizes_entry.delete(0, tk.END)
            self.sizes_entry.insert(0, ','.join(map(str, sizes)))

            # Load other settings as needed
            # For now, just ensure sizes are loaded

        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")

    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('png2ico.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def create_widgets(self):
        """Create the GUI widgets."""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="PNG to ICO Converter",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))

        # Input file selection
        ttk.Label(main_frame, text="Input:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.input_entry = ttk.Entry(main_frame, width=40)
        self.input_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_input).grid(row=1, column=2, padx=(5, 0), pady=5)

        # Bind input entry to update preview on change
        self.input_entry.bind('<KeyRelease>', self.on_input_change)

        # Output file selection
        ttk.Label(main_frame, text="Output:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_entry = ttk.Entry(main_frame, width=40)
        self.output_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_output).grid(row=2, column=2, padx=(5, 0), pady=5)

        # Preview pane
        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="10")
        preview_frame.grid(row=1, column=3, rowspan=4, sticky=(tk.N, tk.S, tk.E, tk.W), padx=(10, 0))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(1, weight=1)

        # Preview canvas
        self.preview_canvas = tk.Canvas(preview_frame, width=200, height=200, bg='gray', relief='sunken')
        self.preview_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Preview info label
        self.preview_info = ttk.Label(preview_frame, text="No image selected")
        self.preview_info.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # File list for batch mode (initially hidden)
        self.file_list_frame = ttk.LabelFrame(main_frame, text="Files", padding="10")
        self.file_list_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        self.file_list_frame.grid_remove()  # Initially hidden
        self.file_list_frame.columnconfigure(0, weight=1)
        self.file_list_frame.rowconfigure(0, weight=1)

        # File listbox
        self.file_listbox = tk.Listbox(self.file_list_frame, height=6, selectmode=tk.SINGLE)
        file_scrollbar = ttk.Scrollbar(self.file_list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=file_scrollbar.set)

        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        file_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Bind file selection event
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)

        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(1, weight=1)

        # Icon sizes
        ttk.Label(options_frame, text="Icon Sizes:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.sizes_entry = ttk.Entry(options_frame, width=30)
        self.sizes_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        ttk.Label(options_frame, text="(comma-separated)", font=("Arial", 8)).grid(row=0, column=2, sticky=tk.W, padx=(5, 0), pady=2)

        # Overwrite checkbox
        self.overwrite_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Overwrite existing files", variable=self.overwrite_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)

        # Batch mode checkbox
        self.batch_var = tk.BooleanVar()
        self.batch_checkbox = ttk.Checkbutton(options_frame, text="Batch mode (process all PNG files in input directory)", variable=self.batch_var, command=self.toggle_batch_mode)
        self.batch_checkbox.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)

        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # Create text widget for log
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=7, column=0, columnspan=4, pady=(0, 10))

        ttk.Button(buttons_frame, text="Convert", command=self.start_conversion).grid(row=0, column=0, padx=5)
        ttk.Button(buttons_frame, text="Settings", command=self.show_settings).grid(row=0, column=1, padx=5)
        ttk.Button(buttons_frame, text="Clear Log", command=self.clear_log).grid(row=0, column=2, padx=5)
        ttk.Button(buttons_frame, text="Exit", command=self.root.quit).grid(row=0, column=3, padx=5)

    def toggle_batch_mode(self):
        """Toggle batch mode display."""
        if self.batch_var.get():
            self.file_list_frame.grid()
            self.load_batch_files()
        else:
            self.file_list_frame.grid_remove()
            self.update_preview()

    def update_preview(self, image_path=None):
        """Update the preview pane with the selected image."""
        # Clear current preview
        self.preview_canvas.delete("all")

        # Determine which image to preview
        if image_path is None:
            if self.batch_var.get():
                # In batch mode, get selected file from list
                selection = self.file_listbox.curselection()
                if selection:
                    selected_file = self.file_listbox.get(selection[0])
                    input_dir = self.input_entry.get().strip()
                    if input_dir:
                        image_path = os.path.join(input_dir, selected_file)
            else:
                # In single mode, use input file
                image_path = self.input_entry.get().strip()

        if not image_path or not os.path.exists(image_path):
            self.preview_info.config(text="No image selected")
            return

        try:
            # Open and display image
            with Image.open(image_path) as img:
                # Get image info
                width, height = img.size
                format_name = img.format or "Unknown"
                mode = img.mode

                # Resize for preview (max 180x180 to fit in 200x200 canvas)
                preview_size = (180, 180)
                img.thumbnail(preview_size, Image.Resampling.LANCZOS)

                # Convert to PhotoImage for tkinter
                self.preview_photo = self.image_to_photo(img)

                # Center the image on canvas
                canvas_width = 200
                canvas_height = 200
                x = (canvas_width - img.width) // 2
                y = (canvas_height - img.height) // 2

                self.preview_canvas.create_image(x, y, anchor=tk.NW, image=self.preview_photo)

                # Update info label
                filename = os.path.basename(image_path)
                self.preview_info.config(text=f"{filename}\n{format_name} • {width}×{height} • {mode}")

        except Exception as e:
            self.preview_info.config(text=f"Error loading image: {str(e)}")
            self.logger.error(f"Preview error: {e}")

    def image_to_photo(self, img):
        """Convert PIL Image to tkinter PhotoImage."""
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Create PhotoImage
        from PIL import ImageTk
        return ImageTk.PhotoImage(img)

    def on_file_select(self, event):
        """Handle file selection in batch mode."""
        self.update_preview()

    def on_input_change(self, event):
        """Handle input entry text changes."""
        if self.batch_var.get():
            self.load_batch_files()
        else:
            self.update_preview()

    def load_batch_files(self):
        """Load PNG files from input directory for batch mode."""
        self.file_listbox.delete(0, tk.END)

        input_dir = self.input_entry.get().strip()
        if not input_dir or not os.path.isdir(input_dir):
            return

        try:
            png_files = []
            for file in os.listdir(input_dir):
                if file.lower().endswith('.png'):
                    png_files.append(file)

            # Sort files
            png_files.sort()

            # Add to listbox
            for file in png_files:
                self.file_listbox.insert(tk.END, file)

            # Auto-select first file if available
            if png_files:
                self.file_listbox.selection_set(0)
                self.update_preview()

        except Exception as e:
            self.logger.error(f"Error loading batch files: {e}")

    def browse_input(self):
        """Browse for input file or directory."""
        if self.batch_var.get():
            path = filedialog.askdirectory(title="Select input directory")
        else:
            path = filedialog.askopenfilename(
                title="Select PNG file",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
        if path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, path)

            # Auto-suggest output path
            if not self.batch_var.get():
                input_path = Path(path)
                output_path = input_path.with_suffix('.ico')
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, str(output_path))

            # Update preview and file list
            if self.batch_var.get():
                self.load_batch_files()
            else:
                self.update_preview()

    def browse_output(self):
        """Browse for output file or directory."""
        if self.batch_var.get():
            path = filedialog.askdirectory(title="Select output directory")
        else:
            path = filedialog.asksaveasfilename(
                title="Save ICO file",
                defaultextension=".ico",
                filetypes=[("ICO files", "*.ico"), ("All files", "*.*")]
            )
        if path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, path)

    def start_conversion(self):
        """Start the conversion process."""
        input_path = self.input_entry.get().strip()
        output_path = self.output_entry.get().strip()

        if not input_path:
            messagebox.showerror("Error", "Please select an input file or directory.")
            return

        # Parse icon sizes
        try:
            sizes_str = self.sizes_entry.get().strip()
            sizes = [int(size.strip()) for size in sizes_str.split(',') if size.strip()]
            if not sizes:
                raise ValueError("No sizes specified")
        except ValueError:
            messagebox.showerror("Error", "Invalid icon sizes. Please enter comma-separated numbers.")
            return

        # Disable convert button
        self.progress_var.set(0)
        self.status_label.config(text="Starting conversion...")

        # Start conversion in separate thread
        thread = threading.Thread(
            target=self.convert_thread,
            args=(input_path, output_path, sizes, self.overwrite_var.get(), self.batch_var.get())
        )
        thread.daemon = True
        thread.start()

    def convert_thread(self, input_path, output_path, sizes, overwrite, batch_mode):
        """Conversion thread function."""
        try:
            if batch_mode:
                # Batch conversion
                if not os.path.isdir(input_path):
                    self.queue.put(('error', "Batch mode requires a directory as input."))
                    return

                # Find all PNG files
                png_files = []
                for file in os.listdir(input_path):
                    if file.lower().endswith('.png'):
                        png_files.append(os.path.join(input_path, file))

                if not png_files:
                    self.queue.put(('error', "No PNG files found in the selected directory."))
                    return

                # Convert all files
                results = self.converter.batch_convert(
                    png_files, output_path, sizes, overwrite,
                    progress_callback=lambda progress, status: self.queue.put(('progress', progress, status))
                )

                self.queue.put(('batch_complete', results))

            else:
                # Single file conversion
                success = self.converter.convert_png_to_ico(input_path, output_path, sizes, overwrite)
                if success:
                    self.queue.put(('complete', f"Successfully converted {Path(input_path).name} to ICO format."))
                else:
                    self.queue.put(('error', f"Failed to convert {Path(input_path).name}."))

        except Exception as e:
            self.queue.put(('error', f"Conversion error: {str(e)}"))

    def check_queue(self):
        """Check for messages from conversion thread."""
        try:
            while True:
                message = self.queue.get_nowait()
                msg_type = message[0]

                if msg_type == 'progress':
                    progress, status = message[1], message[2]
                    self.progress_var.set(progress)
                    self.status_label.config(text=status)
                    self.log_message(status)

                elif msg_type == 'complete':
                    self.progress_var.set(100)
                    self.status_label.config(text="Conversion completed successfully!")
                    self.log_message(message[1])
                    messagebox.showinfo("Success", message[1])

                elif msg_type == 'batch_complete':
                    results = message[1]
                    self.progress_var.set(100)
                    status = f"Batch conversion completed: {results['successful']} successful, {results['failed']} failed"
                    self.status_label.config(text=status)
                    self.log_message(status)

                    # Show detailed results
                    details = "\n".join([
                        f"{detail['file']}: {detail['status']}"
                        for detail in results['details']
                    ])
                    self.log_message(f"Details:\n{details}")

                    messagebox.showinfo("Batch Complete", status)

                elif msg_type == 'error':
                    self.status_label.config(text="Conversion failed!")
                    self.log_message(f"Error: {message[1]}")
                    messagebox.showerror("Error", message[1])

        except queue.Empty:
            pass

        # Schedule next check
        self.root.after(100, self.check_queue)

    def log_message(self, message):
        """Add message to log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        """Clear the log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def show_settings(self):
        """Show settings dialog."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)

        # Center the window
        settings_window.transient(self.root)
        settings_window.grab_set()

        # Settings content
        frame = ttk.Frame(settings_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text="Default Icon Sizes:").grid(row=0, column=0, sticky=tk.W, pady=5)
        sizes_entry = ttk.Entry(frame, width=30)
        sizes_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        sizes_entry.insert(0, ','.join(map(str, self.config.get_icon_sizes())))

        ttk.Label(frame, text="Default Output Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        output_dir_entry = ttk.Entry(frame, width=30)
        output_dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        output_dir_entry.insert(0, self.config.get_default_output_dir())

        def save_settings():
            try:
                # Update config
                self.config.config.set('settings', 'icon_sizes', sizes_entry.get())
                self.config.config.set('settings', 'default_output_dir', output_dir_entry.get())
                self.config.save_config()

                # Update current UI
                self.sizes_entry.delete(0, tk.END)
                self.sizes_entry.insert(0, sizes_entry.get())

                messagebox.showinfo("Settings", "Settings saved successfully!")
                settings_window.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Save", command=save_settings).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).grid(row=0, column=1, padx=5)

def main():
    """Main application entry point."""
    root = tk.Tk()
    app = PNGtoICOConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()