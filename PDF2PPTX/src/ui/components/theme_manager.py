"""
Theme Management System for PDF2PPTX v3.0

Material Design 3 compliant theming system with support for light/dark themes,
custom color tokens, typography, and spacing specifications.
"""

from __future__ import annotations
import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, Callable, List
from enum import Enum


class ThemeMode(Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


@dataclass
class ColorTokens:
    """Material Design 3 Color Tokens"""
    # Primary colors
    primary: str
    on_primary: str
    primary_container: str
    on_primary_container: str

    # Secondary colors
    secondary: str
    on_secondary: str
    secondary_container: str
    on_secondary_container: str

    # Tertiary colors
    tertiary: str
    on_tertiary: str
    tertiary_container: str
    on_tertiary_container: str

    # Error colors
    error: str
    on_error: str
    error_container: str
    on_error_container: str

    # Surface colors
    surface: str
    on_surface: str
    surface_variant: str
    on_surface_variant: str

    # Background
    background: str
    on_background: str

    # Outline and borders
    outline: str
    outline_variant: str

    # Additional semantic colors
    success: str
    warning: str
    info: str


@dataclass
class TypographyTokens:
    """Typography system tokens"""
    # Font families
    font_family_primary: str = "Segoe UI"
    font_family_mono: str = "Consolas"

    # Font sizes (in points)
    display_large: int = 57
    display_medium: int = 45
    display_small: int = 36

    headline_large: int = 32
    headline_medium: int = 28
    headline_small: int = 24

    title_large: int = 22
    title_medium: int = 16
    title_small: int = 14

    body_large: int = 16
    body_medium: int = 14
    body_small: int = 12

    label_large: int = 14
    label_medium: int = 12
    label_small: int = 11


@dataclass
class SpacingTokens:
    """Spacing system tokens (in pixels)"""
    xs: int = 4
    sm: int = 8
    md: int = 16
    lg: int = 24
    xl: int = 32
    xxl: int = 48
    xxxl: int = 64


class Theme:
    """Theme container with all design tokens"""

    def __init__(self, mode: ThemeMode, colors: ColorTokens,
                 typography: TypographyTokens, spacing: SpacingTokens):
        self.mode = mode
        self.colors = colors
        self.typography = typography
        self.spacing = spacing

    def to_dict(self) -> Dict[str, Any]:
        """Convert theme to dictionary for serialization"""
        return {
            'mode': self.mode.value,
            'colors': asdict(self.colors),
            'typography': asdict(self.typography),
            'spacing': asdict(self.spacing)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Theme':
        """Create theme from dictionary"""
        return cls(
            mode=ThemeMode(data['mode']),
            colors=ColorTokens(**data['colors']),
            typography=TypographyTokens(**data['typography']),
            spacing=SpacingTokens(**data['spacing'])
        )


class ThemeManager:
    """Central theme management system with observer pattern"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self._current_theme: Optional[Theme] = None
        self._observers: List[Callable[[Theme], None]] = []

        # Initialize with light theme as default
        self._current_theme = self.get_light_theme()
        self.load_preferences()

    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config_dir = os.path.join(app_dir, 'config')
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, 'theme_config.json')

    def get_light_theme(self) -> Theme:
        """Get Material Design 3 light theme"""
        colors = ColorTokens(
            # Primary - Blue
            primary="#1976D2",
            on_primary="#FFFFFF",
            primary_container="#BBDEFB",
            on_primary_container="#0D47A1",

            # Secondary - Teal
            secondary="#00695C",
            on_secondary="#FFFFFF",
            secondary_container="#B2DFDB",
            on_secondary_container="#004D40",

            # Tertiary - Orange
            tertiary="#F57C00",
            on_tertiary="#FFFFFF",
            tertiary_container="#FFE0B2",
            on_tertiary_container="#E65100",

            # Error - Red
            error="#D32F2F",
            on_error="#FFFFFF",
            error_container="#FFCDD2",
            on_error_container="#B71C1C",

            # Surface
            surface="#FAFAFA",
            on_surface="#212121",
            surface_variant="#F5F5F5",
            on_surface_variant="#424242",

            # Background
            background="#FFFFFF",
            on_background="#212121",

            # Outline
            outline="#9E9E9E",
            outline_variant="#E0E0E0",

            # Semantic colors
            success="#388E3C",
            warning="#F57C00",
            info="#1976D2"
        )

        return Theme(
            mode=ThemeMode.LIGHT,
            colors=colors,
            typography=TypographyTokens(),
            spacing=SpacingTokens()
        )

    def get_dark_theme(self) -> Theme:
        """Get Material Design 3 dark theme"""
        colors = ColorTokens(
            # Primary - Blue (adjusted for dark)
            primary="#64B5F6",
            on_primary="#0D47A1",
            primary_container="#1565C0",
            on_primary_container="#E3F2FD",

            # Secondary - Teal (adjusted for dark)
            secondary="#26A69A",
            on_secondary="#004D40",
            secondary_container="#00695C",
            on_secondary_container="#E0F2F1",

            # Tertiary - Orange (adjusted for dark)
            tertiary="#FFB74D",
            on_tertiary="#E65100",
            tertiary_container="#F57C00",
            on_tertiary_container="#FFF3E0",

            # Error - Red (adjusted for dark)
            error="#EF5350",
            on_error="#B71C1C",
            error_container="#C62828",
            on_error_container="#FFEBEE",

            # Surface
            surface="#1E1E1E",
            on_surface="#E0E0E0",
            surface_variant="#2D2D2D",
            on_surface_variant="#BDBDBD",

            # Background
            background="#121212",
            on_background="#E0E0E0",

            # Outline
            outline="#616161",
            outline_variant="#424242",

            # Semantic colors
            success="#66BB6A",
            warning="#FFB74D",
            info="#64B5F6"
        )

        return Theme(
            mode=ThemeMode.DARK,
            colors=colors,
            typography=TypographyTokens(),
            spacing=SpacingTokens()
        )

    @property
    def current_theme(self) -> Theme:
        """Get current active theme"""
        return self._current_theme

    def set_theme(self, theme: Theme) -> None:
        """Set current theme and notify observers"""
        self._current_theme = theme
        self._notify_observers()
        self.save_preferences()

    def set_theme_mode(self, mode: ThemeMode) -> None:
        """Set theme by mode"""
        if mode == ThemeMode.LIGHT:
            self.set_theme(self.get_light_theme())
        elif mode == ThemeMode.DARK:
            self.set_theme(self.get_dark_theme())
        elif mode == ThemeMode.SYSTEM:
            # For now, default to light theme
            # TODO: Implement system theme detection
            self.set_theme(self.get_light_theme())

    def toggle_theme(self) -> None:
        """Toggle between light and dark themes"""
        if self._current_theme.mode == ThemeMode.LIGHT:
            self.set_theme_mode(ThemeMode.DARK)
        else:
            self.set_theme_mode(ThemeMode.LIGHT)

    def add_observer(self, callback: Callable[[Theme], None]) -> None:
        """Add theme change observer"""
        self._observers.append(callback)

    def remove_observer(self, callback: Callable[[Theme], None]) -> None:
        """Remove theme change observer"""
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self) -> None:
        """Notify all observers of theme change"""
        for callback in self._observers:
            try:
                callback(self._current_theme)
            except Exception as e:
                print(f"Error notifying theme observer: {e}")

    def save_preferences(self) -> None:
        """Save current theme preferences to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._current_theme.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving theme preferences: {e}")

    def load_preferences(self) -> None:
        """Load theme preferences from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._current_theme = Theme.from_dict(data)
        except Exception as e:
            print(f"Error loading theme preferences: {e}")
            # Fall back to light theme
            self._current_theme = self.get_light_theme()


# Global theme manager instance
_theme_manager = None

def get_theme_manager() -> ThemeManager:
    """Get global theme manager instance"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager