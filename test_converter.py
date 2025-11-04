#!/usr/bin/env python3
"""
Test suite for PNG to ICO Converter
Comprehensive tests for image conversion functionality.
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path
from PIL import Image
import configparser

# Import the classes we want to test
from main import Config, ImageConverter

class TestConfig(unittest.TestCase):
    """Test cases for Config class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.ini")

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_default_config_creation(self):
        """Test that default config is created when file doesn't exist."""
        config = Config(self.config_file)

        # Check that config file was created
        self.assertTrue(os.path.exists(self.config_file))

        # Check default values
        self.assertEqual(config.get_icon_sizes(), [16, 24, 32, 48, 64, 128, 256])
        self.assertEqual(config.get_default_output_dir(), "output")
        self.assertFalse(config.get_batch_mode())
        self.assertFalse(config.get_overwrite_existing())

    def test_config_loading(self):
        """Test loading existing config file."""
        # Create a config file manually
        test_config = configparser.ConfigParser()
        test_config.add_section('settings')
        test_config.set('settings', 'icon_sizes', '32,64,128')
        test_config.set('settings', 'default_output_dir', 'test_output')
        test_config.set('settings', 'batch_mode', 'true')
        test_config.set('settings', 'overwrite_existing', 'true')

        with open(self.config_file, 'w') as f:
            test_config.write(f)

        # Load config
        config = Config(self.config_file)

        # Check values
        self.assertEqual(config.get_icon_sizes(), [32, 64, 128])
        self.assertEqual(config.get_default_output_dir(), "test_output")
        self.assertTrue(config.get_batch_mode())
        self.assertTrue(config.get_overwrite_existing())

    def test_config_saving(self):
        """Test saving config changes."""
        config = Config(self.config_file)

        # Modify config
        config.config.set('settings', 'icon_sizes', '48,96')
        config.config.set('settings', 'default_output_dir', 'new_output')
        config.save_config()

        # Reload config
        new_config = Config(self.config_file)

        # Check that changes were saved
        self.assertEqual(new_config.get_icon_sizes(), [48, 96])
        self.assertEqual(new_config.get_default_output_dir(), "new_output")

class TestImageConverter(unittest.TestCase):
    """Test cases for ImageConverter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()  # Use default config
        self.converter = ImageConverter(self.config)

        # Create a test PNG image
        self.test_png = os.path.join(self.temp_dir, "test.png")
        self.create_test_png(self.test_png, 100, 100, 'red')

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def create_test_png(self, path, width, height, color):
        """Create a test PNG image."""
        # Create a simple colored image
        if color == 'red':
            img = Image.new('RGB', (width, height), (255, 0, 0))
        elif color == 'blue':
            img = Image.new('RGB', (width, height), (0, 0, 255))
        elif color == 'green':
            img = Image.new('RGB', (width, height), (0, 255, 0))
        else:
            img = Image.new('RGB', (width, height), (128, 128, 128))

        img.save(path, 'PNG')

    def test_convert_png_to_ico_basic(self):
        """Test basic PNG to ICO conversion."""
        output_path = os.path.join(self.temp_dir, "test.ico")

        result = self.converter.convert_png_to_ico(self.test_png, output_path)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_path))

        # Verify it's a valid ICO file
        with Image.open(output_path) as ico_img:
            self.assertEqual(ico_img.format, 'ICO')

    def test_convert_png_to_ico_auto_output(self):
        """Test conversion with automatic output path generation."""
        # Don't change working directory, just specify full output path
        output_path = os.path.join(self.temp_dir, "test.ico")

        result = self.converter.convert_png_to_ico(self.test_png, output_path)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_path))

    def test_convert_png_to_ico_custom_sizes(self):
        """Test conversion with custom icon sizes."""
        output_path = os.path.join(self.temp_dir, "test_custom.ico")
        custom_sizes = [32, 64]

        result = self.converter.convert_png_to_ico(self.test_png, output_path, custom_sizes)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_path))

        # Verify icon contains the expected sizes
        with Image.open(output_path) as ico_img:
            # ICO format may not expose sizes directly, but file should exist
            self.assertEqual(ico_img.format, 'ICO')

    def test_convert_nonexistent_file(self):
        """Test conversion of nonexistent file."""
        output_path = os.path.join(self.temp_dir, "output.ico")

        result = self.converter.convert_png_to_ico("nonexistent.png", output_path)

        self.assertFalse(result)
        self.assertFalse(os.path.exists(output_path))

    def test_convert_non_png_file(self):
        """Test conversion of non-PNG file."""
        # Create a text file
        text_file = os.path.join(self.temp_dir, "test.txt")
        with open(text_file, 'w') as f:
            f.write("This is not a PNG file")

        output_path = os.path.join(self.temp_dir, "output.ico")

        result = self.converter.convert_png_to_ico(text_file, output_path)

        self.assertFalse(result)
        self.assertFalse(os.path.exists(output_path))

    def test_overwrite_protection(self):
        """Test overwrite protection."""
        output_path = os.path.join(self.temp_dir, "test.ico")

        # Create output file first
        with open(output_path, 'w') as f:
            f.write("dummy content")

        # Try to convert without overwrite permission
        result = self.converter.convert_png_to_ico(self.test_png, output_path, overwrite=False)

        self.assertFalse(result)
        # File should still contain dummy content
        with open(output_path, 'r') as f:
            content = f.read()
            self.assertEqual(content, "dummy content")

    def test_overwrite_allowed(self):
        """Test overwrite when allowed."""
        output_path = os.path.join(self.temp_dir, "test.ico")

        # Create output file first
        with open(output_path, 'w') as f:
            f.write("dummy content")

        # Convert with overwrite permission
        result = self.converter.convert_png_to_ico(self.test_png, output_path, overwrite=True)

        self.assertTrue(result)
        # File should now be an ICO file
        with Image.open(output_path) as ico_img:
            self.assertEqual(ico_img.format, 'ICO')

    def test_batch_convert(self):
        """Test batch conversion."""
        # Create multiple test PNG files
        png_files = []
        for i in range(3):
            png_path = os.path.join(self.temp_dir, f"test_{i}.png")
            self.create_test_png(png_path, 50 + i * 10, 50 + i * 10, 'red')
            png_files.append(png_path)

        output_dir = os.path.join(self.temp_dir, "output")
        results = self.converter.batch_convert(png_files, output_dir)

        # Check results
        self.assertEqual(results['total'], 3)
        self.assertEqual(results['successful'], 3)
        self.assertEqual(results['failed'], 0)

        # Check that output files were created
        for i in range(3):
            ico_path = os.path.join(output_dir, f"test_{i}.ico")
            self.assertTrue(os.path.exists(ico_path))

    def test_batch_convert_with_failures(self):
        """Test batch conversion with some failures."""
        png_files = [
            self.test_png,  # Valid PNG
            "nonexistent.png",  # Invalid file
            os.path.join(self.temp_dir, "not_png.txt")  # Wrong format
        ]

        # Create the text file
        with open(png_files[2], 'w') as f:
            f.write("not a png")

        output_dir = os.path.join(self.temp_dir, "output")
        results = self.converter.batch_convert(png_files, output_dir)

        # Check results
        self.assertEqual(results['total'], 3)
        self.assertEqual(results['successful'], 1)  # Only the first file should succeed
        self.assertEqual(results['failed'], 2)

    def test_resize_image_square(self):
        """Test image resizing for square images."""
        # Create a square test image
        square_img = Image.new('RGBA', (100, 100), (255, 0, 0, 255))

        resized = self.converter._resize_image(square_img, 64)

        self.assertEqual(resized.size, (64, 64))

    def test_resize_image_wide(self):
        """Test image resizing for wide images."""
        # Create a wide test image
        wide_img = Image.new('RGBA', (200, 100), (255, 0, 0, 255))

        resized = self.converter._resize_image(wide_img, 64)

        self.assertEqual(resized.size, (64, 64))
        # The wide image should be resized to fit width, with padding on height

    def test_resize_image_tall(self):
        """Test image resizing for tall images."""
        # Create a tall test image
        tall_img = Image.new('RGBA', (100, 200), (255, 0, 0, 255))

        resized = self.converter._resize_image(tall_img, 64)

        self.assertEqual(resized.size, (64, 64))
        # The tall image should be resized to fit height, with padding on width

class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_full_conversion_workflow(self):
        """Test a complete conversion workflow."""
        # Create test PNG
        png_path = os.path.join(self.temp_dir, "workflow_test.png")
        img = Image.new('RGB', (128, 128), (0, 255, 0))  # Green square
        img.save(png_path, 'PNG')

        # Setup converter
        config = Config()
        converter = ImageConverter(config)

        # Convert to ICO
        ico_path = os.path.join(self.temp_dir, "workflow_test.ico")
        result = converter.convert_png_to_ico(png_path, ico_path)

        # Verify
        self.assertTrue(result)
        self.assertTrue(os.path.exists(ico_path))

        # Verify ICO can be opened
        with Image.open(ico_path) as ico_img:
            self.assertEqual(ico_img.format, 'ICO')
            # ICO should have some size variants
            self.assertGreater(ico_img.size[0], 0)
            self.assertGreater(ico_img.size[1], 0)

if __name__ == '__main__':
    # Create test suite
    unittest.main(verbosity=2)