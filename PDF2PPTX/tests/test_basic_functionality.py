"""
Basic functionality tests for PDF2PNG/PDF2PPTX converter.
Simplified tests to verify core functionality without complex mocking.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.pdf_processor import ConversionConfig, validate_conversion_config
from config import get_app_config


class TestBasicFunctionality:
    """Test basic application functionality."""

    def test_conversion_config_creation(self):
        """Test ConversionConfig creation with valid values."""
        config = ConversionConfig(
            scale_factor=2.0,
            auto_rotate=True,
            slide_width_mm=420.0,
            slide_height_mm=297.0,
            target_dpi=150
        )

        assert config.scale_factor == 2.0
        assert config.auto_rotate is True
        assert config.slide_width_mm == 420.0
        assert config.slide_height_mm == 297.0
        assert config.target_dpi == 150

    def test_conversion_config_validation(self):
        """Test ConversionConfig validation."""
        # Valid config should not raise
        valid_config = ConversionConfig(scale_factor=1.5, target_dpi=150)
        validate_conversion_config(valid_config)  # Should not raise

        # Invalid scale factor should raise
        with pytest.raises(ValueError, match="Scale factor must be positive"):
            invalid_config = ConversionConfig(scale_factor=0)
            validate_conversion_config(invalid_config)

        # Invalid DPI should raise
        with pytest.raises(ValueError, match="DPI must be at least 72"):
            invalid_config = ConversionConfig(target_dpi=50)
            validate_conversion_config(invalid_config)

    def test_app_config_loading(self):
        """Test application configuration loading."""
        config = get_app_config()

        # Basic structure checks
        assert hasattr(config, 'powerpoint_label')
        assert hasattr(config.powerpoint_label, 'font_name')
        assert hasattr(config.powerpoint_label, 'font_size')
        assert hasattr(config.powerpoint_label, 'text_color')

    def test_utility_functions(self):
        """Test utility functions from pdf_processor."""
        from core.pdf_processor import mm_to_emu, points_to_emu

        # Test mm_to_emu conversion
        result = mm_to_emu(25.4)  # 25.4mm = 1 inch
        expected = int(25.4 * 36000)  # EMU conversion
        assert result == expected

        # Test points_to_emu conversion
        result = points_to_emu(72)  # 72 points = 1 inch
        expected = int(72 * 12700)  # EMU conversion
        assert result == expected

    def test_path_manager_imports(self):
        """Test that path manager can be imported and instantiated."""
        from utils.path_utils import PathManager

        path_manager = PathManager()
        assert hasattr(path_manager, 'base_path')
        assert hasattr(path_manager, 'input_dir')
        assert hasattr(path_manager, 'output_dir')


class TestApplicationStructure:
    """Test application structure and imports."""

    def test_core_imports(self):
        """Test that core modules can be imported."""
        from core.pdf_processor import ConversionConfig, PDFProcessingError
        from config import get_app_config, save_app_config
        from utils.error_handling import UserFriendlyError
        from utils.path_utils import PathManager

        # If we reach here, imports are successful
        assert True

    def test_ui_imports(self):
        """Test that UI modules can be imported."""
        try:
            from ui.main_window import MainWindow
            from ui.converters import ImageConverter, PPTXConverter
            # If we reach here, UI imports are successful
            assert True
        except ImportError as e:
            # UI imports might fail in headless environment
            pytest.skip(f"UI imports not available: {e}")

    def test_config_structure(self):
        """Test configuration structure."""
        config = get_app_config()

        # Check PowerPoint label configuration
        label_config = config.powerpoint_label
        assert isinstance(label_config.font_size, int)
        assert isinstance(label_config.font_bold, bool)
        assert isinstance(label_config.text_color, str)
        assert label_config.text_color.startswith('#')  # Hex color

        # Check position is valid
        valid_positions = ["top-left", "top-right", "bottom-left", "bottom-right"]
        assert label_config.position in valid_positions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])