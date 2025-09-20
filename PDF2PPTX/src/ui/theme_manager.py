"""
Deep Blue Theme management system for PDF2PPTX application.
Provides professional deep blue interface design with modern styling.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path


class ThemeMode(Enum):
    """Available theme modes."""
    LIGHT = "light"
    DEEP_BLUE = "deep_blue"
    AUTO = "auto"  # Follow system preference (future feature)


@dataclass
class ThemeColors:
    """Color scheme for a theme."""
    # Background colors
    bg_primary: str
    bg_secondary: str
    bg_tertiary: str

    # Foreground colors
    fg_primary: str
    fg_secondary: str
    fg_muted: str

    # Accent colors
    accent_primary: str
    accent_secondary: str

    # Status colors
    success: str
    warning: str
    error: str
    info: str

    # Interactive elements
    button_bg: str
    button_fg: str
    button_hover: str
    button_active: str

    # Input elements
    entry_bg: str
    entry_fg: str
    entry_border: str
    entry_focus: str

    # Progress elements
    progress_bg: str
    progress_fg: str


@dataclass
class ThemeStyle:
    """Complete theme style definition."""
    name: str
    display_name: str
    colors: ThemeColors
    fonts: Dict[str, tuple]  # Font families and sizes
    borders: Dict[str, Dict[str, Any]]  # Border styles
    spacing: Dict[str, int]  # Padding and margin values


class ThemeManager:
    """
    Manages application themes and provides styling for UI components.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.cwd() / "config"
        self.config_dir.mkdir(exist_ok=True)

        self.current_theme: ThemeMode = ThemeMode.DEEP_BLUE
        self.custom_themes: Dict[str, ThemeStyle] = {}
        self.theme_callbacks: Dict[str, Callable] = {}

        # Initialize default themes
        self._init_default_themes()

        # Load saved theme preference
        self._load_theme_config()

    def _init_default_themes(self) -> None:
        """Initialize built-in light and dark themes."""
        # Light theme
        light_colors = ThemeColors(
            bg_primary="#FFFFFF",
            bg_secondary="#F8F9FA",
            bg_tertiary="#E9ECEF",
            fg_primary="#212529",
            fg_secondary="#495057",
            fg_muted="#6C757D",
            accent_primary="#007BFF",
            accent_secondary="#6C757D",
            success="#28A745",
            warning="#FFC107",
            error="#DC3545",
            info="#17A2B8",
            button_bg="#007BFF",
            button_fg="#FFFFFF",
            button_hover="#0056B3",
            button_active="#004085",
            entry_bg="#FFFFFF",
            entry_fg="#212529",
            entry_border="#CED4DA",
            entry_focus="#007BFF",
            progress_bg="#E9ECEF",
            progress_fg="#007BFF"
        )

        self.light_theme = ThemeStyle(
            name="light",
            display_name="ライトテーマ",
            colors=light_colors,
            fonts={
                "default": ("Arial", 10),
                "heading": ("Arial", 12, "bold"),
                "small": ("Arial", 8),
                "button": ("Arial", 10)
            },
            borders={
                "default": {"width": 1, "style": "solid"},
                "focus": {"width": 2, "style": "solid"},
                "button": {"width": 1, "style": "solid", "radius": 4}
            },
            spacing={
                "small": 5,
                "medium": 10,
                "large": 20,
                "button_padding": 8
            }
        )

        # Deep Blue theme
        deep_blue_colors = ThemeColors(
            bg_primary="#0F2A44",      # Deep navy blue
            bg_secondary="#1B3A5C",    # Slightly lighter blue
            bg_tertiary="#2A4A6B",     # Medium blue
            fg_primary="#FFFFFF",      # Pure white text
            fg_secondary="#E0E8F0",    # Light blue-white
            fg_muted="#B8CDE0",        # Muted blue-white
            accent_primary="#4A90E2",  # Bright blue
            accent_secondary="#6BA3F5", # Light blue
            success="#28A745",         # Green
            warning="#FFC107",         # Yellow
            error="#DC3545",           # Red
            info="#17A2B8",            # Cyan
            button_bg="#2E5A87",       # Medium blue for buttons
            button_fg="#FFFFFF",       # White text
            button_hover="#4A90E2",    # Bright blue on hover
            button_active="#1C4A73",   # Dark blue when active
            entry_bg="#1B3A5C",        # Dark blue entry background
            entry_fg="#FFFFFF",        # White text
            entry_border="#4A90E2",    # Blue border
            entry_focus="#6BA3F5",     # Light blue focus
            progress_bg="#2A4A6B",     # Medium blue progress background
            progress_fg="#4A90E2"      # Bright blue progress
        )

        self.deep_blue_theme = ThemeStyle(
            name="deep_blue",
            display_name="深い青のテーマ",
            colors=deep_blue_colors,
            fonts={
                "default": ("Arial", 10),
                "heading": ("Arial", 12, "bold"),
                "small": ("Arial", 8),
                "button": ("Arial", 10, "bold")
            },
            borders={
                "default": {"width": 1, "style": "solid"},
                "focus": {"width": 2, "style": "solid"},
                "button": {"width": 1, "style": "solid", "radius": 6}
            },
            spacing={
                "small": 6,
                "medium": 12,
                "large": 24,
                "button_padding": 10
            }
        )

    def get_current_theme(self) -> ThemeStyle:
        """Get the currently active theme."""
        if self.current_theme == ThemeMode.DEEP_BLUE:
            return self.deep_blue_theme
        elif self.current_theme == ThemeMode.LIGHT:
            return self.light_theme
        else:
            # Auto mode - default to deep blue for now
            return self.deep_blue_theme

    def set_theme(self, theme_mode: ThemeMode) -> None:
        """
        Set the active theme and notify all registered callbacks.

        Args:
            theme_mode: Theme mode to activate
        """
        if theme_mode == self.current_theme:
            return

        self.current_theme = theme_mode
        self._save_theme_config()

        # Notify all registered callbacks about theme change
        for callback in self.theme_callbacks.values():
            try:
                callback(self.get_current_theme())
            except Exception as e:
                print(f"Error in theme callback: {e}")

    def register_theme_callback(self, name: str, callback: Callable[[ThemeStyle], None]) -> None:
        """
        Register a callback to be called when theme changes.

        Args:
            name: Unique name for the callback
            callback: Function to call with new theme
        """
        self.theme_callbacks[name] = callback

    def unregister_theme_callback(self, name: str) -> None:
        """Remove a theme change callback."""
        self.theme_callbacks.pop(name, None)

    def apply_theme_to_widget(self, widget: tk.Widget, style_type: str = "default") -> None:
        """
        Apply current theme styling to a tkinter widget.

        Args:
            widget: Widget to style
            style_type: Type of styling to apply (default, button, entry, etc.)
        """
        theme = self.get_current_theme()

        if isinstance(widget, tk.Button):
            self._style_button(widget, theme)
        elif isinstance(widget, tk.Entry):
            self._style_entry(widget, theme)
        elif isinstance(widget, tk.Label):
            self._style_label(widget, theme)
        elif isinstance(widget, tk.Frame):
            self._style_frame(widget, theme)
        elif isinstance(widget, ttk.Progressbar):
            self._style_progressbar(widget, theme)
        else:
            # Apply basic styling for other widgets
            self._style_generic(widget, theme)

    def _style_button(self, button: tk.Button, theme: ThemeStyle) -> None:
        """Apply theme styling to a button."""
        button.configure(
            bg=theme.colors.button_bg,
            fg=theme.colors.button_fg,
            activebackground=theme.colors.button_hover,
            activeforeground=theme.colors.button_fg,
            relief="raised",
            borderwidth=2,
            font=theme.fonts["button"],
            highlightthickness=0,
            padx=theme.spacing["button_padding"],
            pady=theme.spacing["small"]
        )

        # Add advanced hover effects for deep blue theme
        def on_enter(e):
            button.configure(
                bg=theme.colors.button_hover,
                relief="raised",
                borderwidth=3
            )

        def on_leave(e):
            button.configure(
                bg=theme.colors.button_bg,
                relief="raised",
                borderwidth=2
            )

        def on_press(e):
            button.configure(
                bg=theme.colors.button_active,
                relief="sunken"
            )

        def on_release(e):
            button.configure(
                bg=theme.colors.button_hover,
                relief="raised"
            )

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        button.bind("<Button-1>", on_press)
        button.bind("<ButtonRelease-1>", on_release)

    def _style_entry(self, entry: tk.Entry, theme: ThemeStyle) -> None:
        """Apply theme styling to an entry widget."""
        entry.configure(
            bg=theme.colors.entry_bg,
            fg=theme.colors.entry_fg,
            insertbackground=theme.colors.fg_primary,
            relief="solid",
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=theme.colors.entry_focus,
            highlightbackground=theme.colors.entry_border,
            font=theme.fonts["default"]
        )

    def _style_label(self, label: tk.Label, theme: ThemeStyle) -> None:
        """Apply theme styling to a label."""
        label.configure(
            bg=theme.colors.bg_primary,
            fg=theme.colors.fg_primary,
            font=theme.fonts["default"]
        )

    def _style_frame(self, frame: tk.Frame, theme: ThemeStyle) -> None:
        """Apply theme styling to a frame."""
        frame.configure(
            bg=theme.colors.bg_primary,
            highlightthickness=0
        )

    def _style_progressbar(self, progressbar: ttk.Progressbar, theme: ThemeStyle) -> None:
        """Apply theme styling to a progress bar."""
        # Configure ttk style for progress bar
        style = ttk.Style()
        style.theme_use('clam')

        style.configure(
            "Themed.Horizontal.TProgressbar",
            background=theme.colors.progress_fg,
            troughcolor=theme.colors.progress_bg,
            borderwidth=1,
            lightcolor=theme.colors.progress_fg,
            darkcolor=theme.colors.progress_fg
        )

        progressbar.configure(style="Themed.Horizontal.TProgressbar")

    def _style_generic(self, widget: tk.Widget, theme: ThemeStyle) -> None:
        """Apply basic theme styling to any widget."""
        try:
            widget.configure(
                bg=theme.colors.bg_primary,
                fg=theme.colors.fg_primary
            )
        except tk.TclError:
            # Some widgets may not support all options
            pass

    def get_theme_colors(self) -> ThemeColors:
        """Get colors for the current theme."""
        return self.get_current_theme().colors

    def get_theme_fonts(self) -> Dict[str, tuple]:
        """Get fonts for the current theme."""
        return self.get_current_theme().fonts

    def create_styled_button(self, parent: tk.Widget, text: str, **kwargs) -> tk.Button:
        """
        Create a button with current theme styling applied.

        Args:
            parent: Parent widget
            text: Button text
            **kwargs: Additional button configuration

        Returns:
            Styled button widget
        """
        button = tk.Button(parent, text=text, **kwargs)
        self.apply_theme_to_widget(button, "button")
        return button

    def create_styled_entry(self, parent: tk.Widget, **kwargs) -> tk.Entry:
        """
        Create an entry with current theme styling applied.

        Args:
            parent: Parent widget
            **kwargs: Additional entry configuration

        Returns:
            Styled entry widget
        """
        entry = tk.Entry(parent, **kwargs)
        self.apply_theme_to_widget(entry, "entry")
        return entry

    def create_styled_label(self, parent: tk.Widget, text: str, **kwargs) -> tk.Label:
        """
        Create a label with current theme styling applied.

        Args:
            parent: Parent widget
            text: Label text
            **kwargs: Additional label configuration

        Returns:
            Styled label widget
        """
        label = tk.Label(parent, text=text, **kwargs)
        self.apply_theme_to_widget(label, "label")
        return label

    def create_styled_frame(self, parent: tk.Widget, **kwargs) -> tk.Frame:
        """
        Create a frame with current theme styling applied.

        Args:
            parent: Parent widget
            **kwargs: Additional frame configuration

        Returns:
            Styled frame widget
        """
        frame = tk.Frame(parent, **kwargs)
        self.apply_theme_to_widget(frame, "frame")
        return frame

    def _load_theme_config(self) -> None:
        """Load theme configuration from file."""
        config_file = self.config_dir / "theme_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    theme_name = config.get('current_theme', 'light')
                    self.current_theme = ThemeMode(theme_name)
            except Exception:
                # Use default theme if loading fails
                self.current_theme = ThemeMode.LIGHT

    def _save_theme_config(self) -> None:
        """Save current theme configuration to file."""
        config_file = self.config_dir / "theme_config.json"
        try:
            config = {
                'current_theme': self.current_theme.value,
                'version': '1.0'
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save theme config: {e}")

    def toggle_theme(self) -> None:
        """Toggle between light and deep blue themes."""
        if self.current_theme == ThemeMode.LIGHT:
            self.set_theme(ThemeMode.DEEP_BLUE)
        else:
            self.set_theme(ThemeMode.LIGHT)

    def get_available_themes(self) -> Dict[ThemeMode, str]:
        """Get available theme modes with display names."""
        return {
            ThemeMode.LIGHT: self.light_theme.display_name,
            ThemeMode.DEEP_BLUE: self.deep_blue_theme.display_name
        }


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """Get or create the global theme manager instance."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def set_global_theme(theme_mode: ThemeMode) -> None:
    """Set the global application theme."""
    theme_manager = get_theme_manager()
    theme_manager.set_theme(theme_mode)


def get_current_theme_colors() -> ThemeColors:
    """Get colors for the current global theme."""
    theme_manager = get_theme_manager()
    return theme_manager.get_theme_colors()


def apply_theme_to_widget(widget: tk.Widget, style_type: str = "default") -> None:
    """Apply current global theme to a widget."""
    theme_manager = get_theme_manager()
    theme_manager.apply_theme_to_widget(widget, style_type)