# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## natural-language
日本語で回答して

## Project Overview

PDF2PPTX_2 is a next-generation PDF conversion application implementing MVP architecture with Material Design 3 UI principles. The project converts PDF documents to PNG images or PowerPoint presentations using a modern Qt-based GUI interface. This is a complete rewrite based on the comprehensive specification in `PDF2PPTX_統合仕様書.md`.

## Architecture Overview

The project follows **MVP (Model-View-Presenter) Architecture** with strict separation of concerns:

### Core Architecture Components

```
src/
├── presentation/presenters/    # MVP Presenter layer - UI logic coordination
├── ui/                        # MVP View layer - Qt-based interface
│   ├── main_window.py         # Main application window
│   ├── components/            # Material Design 3 custom widgets
│   └── themes/                # Dynamic theme system (light/dark)
├── application/services/      # Application service layer
├── core/                      # Domain logic - PDF processing engine
├── utils/                     # Utilities and helpers
└── config.py                  # Configuration management
```

### Technology Stack

- **GUI Framework**: PySide6/Qt6 (replacing Tkinter for modern UI)
- **UI Design**: Material Design 3 with custom themes
- **Architecture**: MVP pattern with dependency injection
- **Async Processing**: Non-blocking PDF conversion operations
- **Configuration**: JSON-based settings with schema validation

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment (required)
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies (when available)
pip install -r requirements.txt
```

### Application Development
```bash
# Run main Qt application
python main.py

# Development mode
python -m src.ui.main_window
```

### Code Quality
```bash
# Format code with Black (88-character lines)
black src tests

# Type checking with MyPy
mypy src

# Linting with Ruff
ruff src tests

# Security scanning
bandit -r src/
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage (target: 80% overall)
pytest --cov=src tests/

# Run specific test categories
pytest -m security      # Security-focused tests
pytest -m integration   # Integration tests
```

### Building
```bash
# Build Windows executable
pyinstaller build_windows.spec --clean --noconfirm

# Build different variants
pyinstaller build_gui.spec     # GUI version
pyinstaller build_console.spec # Console version
```

## Key Features to Implement

### PDF Processing Core
- **PDF to PNG**: High-resolution output (up to 300 DPI), automatic rotation, customizable scaling (0.5x-3.0x)
- **PDF to PowerPoint**: A3 landscape format (420×297mm), custom label styling, professional templates
- **Batch Processing**: Folder-based operations with progress tracking
- **Async Operations**: Non-blocking conversions with cancellation support

### Modern UI Components
- **Material Design 3**: Custom Qt widgets following Material Design principles
- **Theme System**: Dynamic light/dark mode with accent color customization
- **Progress Components**: Real-time progress with detailed status updates
- **Drag & Drop**: File selection with visual feedback
- **Settings Panel**: Comprehensive configuration management

### Performance Targets
- **Conversion Speed**: A4 page in <0.5 seconds
- **Memory Usage**: Maximum 1GB
- **UI Responsiveness**: <0.1 second reaction time
- **Startup Time**: <3 seconds

## Code Style Guidelines

### Python Conventions
- Use Black formatting (88-character line length)
- Complete type hints for all functions and class attributes
- Google-style docstrings for public APIs
- PEP 8 naming conventions

### UI Component Structure
```python
class ModernWidget(CTkFrame):
    """Base class for Material Design 3 components"""

    def __init__(self, master, theme: str = 'auto', **kwargs):
        super().__init__(master, **kwargs)
        self._setup_ui()
        self._bind_events()

    def _setup_ui(self) -> None:
        """Initialize UI elements (override in subclasses)"""
        pass

    def _bind_events(self) -> None:
        """Bind event handlers (override in subclasses)"""
        pass
```

### Error Handling Strategy
- Use specific exception types (`PDFProcessingError`, `ConfigurationError`)
- Provide user-friendly error messages in Japanese
- Log detailed technical information for debugging
- Implement graceful degradation for non-critical failures

## Testing Strategy

### Coverage Targets
- **Core Logic**: 90% coverage for PDF processing
- **UI Components**: 70% coverage for interface logic
- **Utilities**: 85% coverage for helper functions
- **Overall**: 80% project coverage

### Test Categories
- **Unit Tests**: Individual component functionality
- **Integration Tests**: End-to-end conversion workflows
- **Security Tests**: Input validation and file handling
- **Performance Tests**: Large file processing benchmarks
- **UI Tests**: Critical user interaction paths

## Configuration Management

### Settings Structure
```json
{
  "conversion": {
    "default_scale": 1.5,
    "auto_rotate": true,
    "quality": "high"
  },
  "powerpoint": {
    "slide_size": [420, 297],
    "font_name": "Noto Sans CJK JP",
    "text_color": "#FFFFFF",
    "background_color": "#1976D2"
  },
  "ui": {
    "theme": "auto",
    "language": "ja",
    "animation_enabled": true
  }
}
```

## Security Considerations

- Input validation for all file paths and parameters
- Sandboxed PDF processing to prevent malicious content execution
- Secure temporary file handling with automatic cleanup
- No execution of embedded scripts or forms
- Regular dependency vulnerability scanning

## Agent Integration

The project includes specialized Claude agents:
- **python-pro**: Expert Python development with type safety and async programming
- **ui-designer**: Material Design 3 UI/UX implementation and design systems

## Implementation Notes

This project is currently in the design phase with only the specification document (`PDF2PPTX_統合仕様書.md`) available. The comprehensive 1000+ line specification includes:

- Detailed MVP architecture design
- Complete UI/UX specifications with Material Design 3
- Performance and security requirements
- Implementation guidelines and code examples
- Build and deployment strategies

All development should strictly follow the architectural patterns and requirements outlined in the specification document to ensure consistency with the planned design.