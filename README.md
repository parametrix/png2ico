# PNG to ICO Converter

A comprehensive PNG to ICO converter application with a modern GUI interface, batch processing capabilities, and extensive customization options.

## Features

- **Modern GUI Interface**: User-friendly tkinter-based interface
- **Batch Processing**: Convert multiple PNG files at once
- **Custom Icon Sizes**: Support for multiple icon sizes in a single ICO file
- **Flexible Output**: Choose output location and naming
- **Overwrite Protection**: Optional protection against overwriting existing files
- **Comprehensive Logging**: Detailed conversion logs and progress tracking
- **Cross-Platform**: Works on Windows, macOS, and Linux

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Python**: Python 3.8 or higher
- **Memory**: 512 MB RAM
- **Storage**: 50 MB free space

### Recommended Requirements
- **Operating System**: Windows 11, macOS 12+, or Ubuntu 20.04+
- **Python**: Python 3.10 or higher
- **Memory**: 1 GB RAM
- **Storage**: 100 MB free space

## Installation

### Method 1: Portable Version (Recommended)

1. Download the portable version from the releases page
2. Extract the ZIP file to your desired location
3. Run `png2ico-portable.exe` (Windows) or `png2ico-portable` (Linux/macOS)

The portable version includes all dependencies and requires no installation.

### Method 2: From Source Code

#### Prerequisites
- Python 3.8 or higher installed
- pip package manager

#### Installation Steps

1. **Clone or download the repository**
   ```bash
   git clone https://github.com/yourusername/png2ico.git
   cd png2ico
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

### Method 3: Using Build Scripts

#### Windows
```bash
# Build executable
python build\build.py

# Or use the simple build script
python build\build_simple.py

# Run the built executable
dist\png2ico.exe
```

#### Linux/macOS
```bash
# Build executable
python build/build.py

# Make executable
chmod +x dist/png2ico

# Run the built executable
./dist/png2ico
```

## Usage

### GUI Mode

1. **Launch the application**
   - Run `python main.py` or use the portable/executable version

2. **Select input**
   - Click "Browse..." next to "Input:"
   - Choose a PNG file for single conversion
   - Choose a directory for batch conversion

3. **Configure output**
   - Click "Browse..." next to "Output:"
   - Choose output file location (single) or directory (batch)

4. **Adjust settings** (optional)
   - **Icon Sizes**: Comma-separated list of sizes (e.g., "16,32,48,64")
   - **Overwrite existing files**: Allow overwriting existing ICO files
   - **Batch mode**: Process all PNG files in input directory

5. **Start conversion**
   - Click "Convert" button
   - Monitor progress in the progress bar and log area

### Command Line Usage

The application is primarily GUI-based, but you can modify the code to add command-line support if needed.

## Configuration

The application uses a `config.ini` file for settings:

```ini
[DEFAULT]
icon_sizes = 16,24,32,48,64,128,256
default_output_dir = output
batch_mode = false
overwrite_existing = false
```

### Configuration Options

- **icon_sizes**: Comma-separated list of icon sizes to include
- **default_output_dir**: Default output directory for batch operations
- **batch_mode**: Enable batch processing by default
- **overwrite_existing**: Allow overwriting existing files by default

## Supported Image Formats

### Input Formats
- PNG (Portable Network Graphics)
  - Supports transparency (alpha channel)
  - RGB and RGBA color modes
  - Various bit depths

### Output Format
- ICO (Windows Icon)
  - Multiple sizes in single file
  - Maintains transparency
  - Compatible with Windows applications

## Icon Sizes

The application supports standard Windows icon sizes:

- 16x16: Small icons, favicons
- 24x24: Toolbar icons
- 32x32: Desktop shortcuts, menus
- 48x48: Large icons
- 64x64: High-DPI displays
- 128x128: Very high-DPI displays
- 256x256: Ultra high-DPI displays

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'PIL'"
**Solution**: Install Pillow
```bash
pip install Pillow
```

#### "tkinter not found" or "No module named 'tkinter'"
**Solution**: Install tkinter (usually included with Python)
- **Windows**: tkinter is included with Python installer
- **macOS**: May need to install Python from python.org
- **Linux**: Install tkinter package
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-tk

  # CentOS/RHEL
  sudo yum install tkinter

  # Fedora
  sudo dnf install python3-tkinter
  ```

#### "Permission denied" when saving files
**Solution**:
- Check write permissions on output directory
- Run application as administrator (Windows) or with sudo (Linux/macOS)
- Choose a different output location

#### "MemoryError" with large images
**Solution**:
- Reduce the number of icon sizes
- Use smaller input images
- Close other memory-intensive applications

#### Application won't start
**Solution**:
- Check Python version (must be 3.8+)
- Verify all dependencies are installed
- Check the log file (`png2ico.log`) for error details

### Build Issues

#### PyInstaller fails to build
**Solution**:
- Ensure PyInstaller is installed: `pip install pyinstaller`
- Try the simple build script: `python build\build_simple.py`
- Check antivirus software isn't blocking the build process

#### NSIS installer creation fails
**Solution**:
- Install NSIS (Nullsoft Scriptable Install System)
- Download from: https://nsis.sourceforge.io/
- Add NSIS to system PATH
- Or use the portable version without installer

### Performance Issues

#### Slow conversion of large images
**Solution**:
- Reduce icon sizes in configuration
- Use fewer icon sizes
- Convert images individually instead of batch mode

#### High memory usage
**Solution**:
- Process fewer files at once in batch mode
- Close other applications
- Use smaller input images

## Development

### Project Structure

```
png2ico/
├── main.py                 # Main GUI application
├── test_converter.py       # Comprehensive test suite
├── config.ini             # Application configuration
├── requirements.txt       # Python dependencies
├── png2ico.spec          # PyInstaller specification
├── build/
│   ├── build.py          # Comprehensive build script
│   └── build_simple.py   # Simple build script
├── installer/
│   └── portable/         # Portable version
├── sample_data/          # Sample PNG files
├── test_output/          # Test output directory
└── README.md             # This documentation
```

### Running Tests

```bash
# Run all tests
python -m unittest test_converter.py

# Run with verbose output
python -m unittest test_converter.py -v

# Run specific test class
python -m unittest test_converter.TestImageConverter -v
```

### Building from Source

#### Development Build
```bash
# Install in development mode
pip install -e .

# Run tests
python -m unittest

# Build executable
python build/build.py
```

#### Creating Distribution Packages
```bash
# Build wheel
python setup.py bdist_wheel

# Build source distribution
python setup.py sdist
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `python -m unittest`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Add docstrings to all classes and methods
- Write comprehensive unit tests

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 1.0.0
- Initial release
- GUI interface with tkinter
- Batch processing support
- Multiple icon sizes
- Comprehensive test suite
- Cross-platform compatibility
- Portable version support

## Support

For support, please:
1. Check the troubleshooting section above
2. Review the log file (`png2ico.log`) for error details
3. Open an issue on GitHub with:
   - Your operating system and Python version
   - Steps to reproduce the issue
   - Error messages and log output
   - Sample input files (if applicable)

## Acknowledgments

- **Pillow**: Powerful image processing library
- **tkinter**: Python's standard GUI library
- **PyInstaller**: Application packaging tool
- **NSIS**: Windows installer creation tool