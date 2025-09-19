"""
Modern UI Components for PDF2PPTX v3.0

Material Design 3 inspired widgets built on tkinter with custom styling,
animations, and accessibility features.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, font
from typing import Optional, Callable, Any, Dict, List
import threading
import time
from dataclasses import dataclass
from .theme_manager import get_theme_manager, Theme


class MaterialColors:
    """Material Design 3 color utilities"""

    @staticmethod
    def get_current_colors() -> Dict[str, str]:
        """Get current theme colors as dictionary"""
        theme = get_theme_manager().current_theme
        return {
            'primary': theme.colors.primary,
            'on_primary': theme.colors.on_primary,
            'primary_container': theme.colors.primary_container,
            'secondary': theme.colors.secondary,
            'surface': theme.colors.surface,
            'on_surface': theme.colors.on_surface,
            'background': theme.colors.background,
            'error': theme.colors.error,
            'success': theme.colors.success,
            'warning': theme.colors.warning,
            'outline': theme.colors.outline
        }


class MaterialIcons:
    """Material Design icons using Unicode symbols"""

    # Navigation
    MENU = "☰"
    CLOSE = "✕"
    BACK = "←"
    FORWARD = "→"

    # Actions
    ADD = "+"
    REMOVE = "−"
    EDIT = "✏"
    DELETE = "🗑"
    SAVE = "💾"
    REFRESH = "⟳"

    # File operations
    FOLDER = "📁"
    FILE = "📄"
    DOWNLOAD = "⬇"
    UPLOAD = "⬆"

    # Status
    CHECK = "✓"
    ERROR = "⚠"
    INFO = "ℹ"
    SUCCESS = "✓"

    # Media
    PLAY = "▶"
    PAUSE = "⏸"
    STOP = "⏹"


class ModernButton(tk.Button):
    """Material Design 3 button with hover effects and states"""

    def __init__(self, parent, text: str = "", command: Optional[Callable] = None,
                 style: str = "filled", icon: str = "", **kwargs):
        # Remove custom arguments before passing to parent
        custom_args = {'style', 'icon'}
        button_kwargs = {k: v for k, v in kwargs.items() if k not in custom_args}

        super().__init__(parent, text=text, command=command, **button_kwargs)

        self.style = style
        self.icon = icon
        self._is_hovered = False
        self._is_pressed = False

        self._setup_styling()
        self._bind_events()

        # Subscribe to theme changes
        get_theme_manager().add_observer(self._on_theme_changed)

    def _setup_styling(self):
        """Apply Material Design 3 styling"""
        theme = get_theme_manager().current_theme
        colors = theme.colors

        # Configure font
        self.configure(
            font=(theme.typography.font_family_primary, theme.typography.body_large),
            relief='flat',
            borderwidth=0,
            cursor='hand2'
        )

        # Apply style-specific colors
        if self.style == "filled":
            self.configure(
                bg=colors.primary,
                fg=colors.on_primary,
                activebackground=self._lighten_color(colors.primary),
                activeforeground=colors.on_primary
            )
        elif self.style == "outlined":
            self.configure(
                bg=colors.surface,
                fg=colors.primary,
                highlightbackground=colors.outline,
                highlightthickness=1,
                activebackground=colors.primary_container,
                activeforeground=colors.on_primary_container
            )
        elif self.style == "text":
            self.configure(
                bg=colors.surface,
                fg=colors.primary,
                activebackground=colors.primary_container,
                activeforeground=colors.on_primary_container
            )

        # Add icon if specified
        if self.icon:
            current_text = self.cget('text')
            self.configure(text=f"{self.icon} {current_text}")

    def _bind_events(self):
        """Bind mouse events for interactions"""
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)

    def _on_enter(self, event):
        """Handle mouse enter"""
        self._is_hovered = True
        self._update_visual_state()

    def _on_leave(self, event):
        """Handle mouse leave"""
        self._is_hovered = False
        self._update_visual_state()

    def _on_press(self, event):
        """Handle mouse press"""
        self._is_pressed = True
        self._update_visual_state()

    def _on_release(self, event):
        """Handle mouse release"""
        self._is_pressed = False
        self._update_visual_state()

    def _update_visual_state(self):
        """Update button appearance based on state"""
        theme = get_theme_manager().current_theme
        colors = theme.colors

        if self._is_pressed:
            # Pressed state
            if self.style == "filled":
                self.configure(bg=self._darken_color(colors.primary))
        elif self._is_hovered:
            # Hovered state
            if self.style == "filled":
                self.configure(bg=self._lighten_color(colors.primary))
            elif self.style in ["outlined", "text"]:
                self.configure(bg=colors.primary_container)
        else:
            # Normal state
            self._setup_styling()

    def _lighten_color(self, color: str, factor: float = 0.1) -> str:
        """Lighten a hex color"""
        # Simple lightening by adding to RGB values
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        lightened = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
        return f"#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}"

    def _darken_color(self, color: str, factor: float = 0.1) -> str:
        """Darken a hex color"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * (1 - factor))) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def _on_theme_changed(self, theme: Theme):
        """Handle theme changes"""
        self._setup_styling()


class ModernCard(tk.Frame):
    """Material Design 3 card component with elevation and content area"""

    def __init__(self, parent, elevation: int = 1, **kwargs):
        super().__init__(parent, **kwargs)

        self.elevation = elevation
        self._setup_styling()

        # Subscribe to theme changes
        get_theme_manager().add_observer(self._on_theme_changed)

    def _setup_styling(self):
        """Apply card styling with elevation"""
        theme = get_theme_manager().current_theme
        colors = theme.colors
        spacing = theme.spacing

        self.configure(
            bg=colors.surface,
            relief='flat',
            bd=0,
            padx=spacing.md,
            pady=spacing.md
        )

        # Simulate elevation with border
        if self.elevation > 0:
            self.configure(
                highlightbackground=colors.outline_variant,
                highlightthickness=1
            )

    def _on_theme_changed(self, theme: Theme):
        """Handle theme changes"""
        self._setup_styling()


class ModernTextField(tk.Frame):
    """Material Design 3 text field with floating label and validation"""

    def __init__(self, parent, label: str = "", placeholder: str = "",
                 validator: Optional[Callable[[str], bool]] = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.label_text = label
        self.placeholder_text = placeholder
        self.validator = validator
        self._is_focused = False
        self._is_valid = True

        self._create_widgets()
        self._setup_styling()
        self._bind_events()

        # Subscribe to theme changes
        get_theme_manager().add_observer(self._on_theme_changed)

    def _create_widgets(self):
        """Create internal widgets"""
        theme = get_theme_manager().current_theme

        # Label
        self.label = tk.Label(self, text=self.label_text)
        self.label.pack(anchor='w')

        # Entry container frame
        self.entry_frame = tk.Frame(self)
        self.entry_frame.pack(fill='x', pady=(4, 0))

        # Entry widget
        self.entry = tk.Entry(self.entry_frame)
        self.entry.pack(fill='x', padx=2, pady=2)

        # Helper text label
        self.helper_label = tk.Label(self, text="")
        self.helper_label.pack(anchor='w')

        # Set placeholder if empty
        if self.placeholder_text:
            self._set_placeholder()

    def _setup_styling(self):
        """Apply Material Design 3 styling"""
        theme = get_theme_manager().current_theme
        colors = theme.colors
        typography = theme.typography

        # Configure label
        self.label.configure(
            font=(typography.font_family_primary, typography.label_medium),
            fg=colors.on_surface_variant,
            bg=colors.background
        )

        # Configure entry frame
        self.entry_frame.configure(
            bg=colors.surface_variant,
            highlightbackground=colors.outline,
            highlightthickness=1,
            relief='flat'
        )

        # Configure entry
        self.entry.configure(
            font=(typography.font_family_primary, typography.body_large),
            fg=colors.on_surface,
            bg=colors.surface_variant,
            relief='flat',
            bd=0,
            insertbackground=colors.primary
        )

        # Configure helper text
        self.helper_label.configure(
            font=(typography.font_family_primary, typography.label_small),
            fg=colors.on_surface_variant,
            bg=colors.background
        )

        self.configure(bg=colors.background)

    def _bind_events(self):
        """Bind events for interactions"""
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)
        self.entry.bind('<KeyRelease>', self._on_text_changed)

    def _on_focus_in(self, event):
        """Handle focus in"""
        self._is_focused = True
        self._clear_placeholder()
        self._update_styling()

    def _on_focus_out(self, event):
        """Handle focus out"""
        self._is_focused = False
        if not self.entry.get():
            self._set_placeholder()
        self._validate_input()
        self._update_styling()

    def _on_text_changed(self, event):
        """Handle text changes"""
        if self._is_focused:
            self._validate_input()

    def _set_placeholder(self):
        """Set placeholder text"""
        if self.placeholder_text:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.placeholder_text)
            self.entry.configure(fg=get_theme_manager().current_theme.colors.on_surface_variant)

    def _clear_placeholder(self):
        """Clear placeholder text"""
        if self.entry.get() == self.placeholder_text:
            self.entry.delete(0, tk.END)
            self.entry.configure(fg=get_theme_manager().current_theme.colors.on_surface)

    def _validate_input(self):
        """Validate current input"""
        if self.validator and self.entry.get() != self.placeholder_text:
            self._is_valid = self.validator(self.entry.get())
            self._update_styling()

    def _update_styling(self):
        """Update styling based on state"""
        theme = get_theme_manager().current_theme
        colors = theme.colors

        if self._is_focused:
            self.entry_frame.configure(highlightbackground=colors.primary, highlightthickness=2)
        elif not self._is_valid:
            self.entry_frame.configure(highlightbackground=colors.error, highlightthickness=2)
        else:
            self.entry_frame.configure(highlightbackground=colors.outline, highlightthickness=1)

    def get(self) -> str:
        """Get entry value"""
        value = self.entry.get()
        return "" if value == self.placeholder_text else value

    def set(self, value: str):
        """Set entry value"""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
        self.entry.configure(fg=get_theme_manager().current_theme.colors.on_surface)

    def set_helper_text(self, text: str, is_error: bool = False):
        """Set helper text"""
        colors = get_theme_manager().current_theme.colors
        self.helper_label.configure(
            text=text,
            fg=colors.error if is_error else colors.on_surface_variant
        )

    def _on_theme_changed(self, theme: Theme):
        """Handle theme changes"""
        self._setup_styling()


class ModernProgressBar(tk.Frame):
    """Material Design 3 progress indicator with determinate and indeterminate modes"""

    def __init__(self, parent, mode: str = "determinate", **kwargs):
        super().__init__(parent, **kwargs)

        self.mode = mode
        self._value = 0.0
        self._maximum = 100.0
        self._animation_running = False

        self._create_widgets()
        self._setup_styling()

        # Subscribe to theme changes
        get_theme_manager().add_observer(self._on_theme_changed)

    def _create_widgets(self):
        """Create progress bar widgets"""
        self.track = tk.Frame(self)
        self.track.pack(fill='x', pady=2)

        self.indicator = tk.Frame(self.track)
        self.indicator.pack(side='left')

    def _setup_styling(self):
        """Apply Material Design 3 styling"""
        theme = get_theme_manager().current_theme
        colors = theme.colors

        self.configure(bg=colors.background)

        # Track styling
        self.track.configure(
            bg=colors.outline_variant,
            height=4,
            relief='flat'
        )

        # Indicator styling
        self.indicator.configure(
            bg=colors.primary,
            height=4,
            relief='flat'
        )

        self._update_progress()

    def _update_progress(self):
        """Update progress indicator width"""
        if self.mode == "determinate":
            track_width = self.track.winfo_width()
            if track_width > 1:  # Ensure track is rendered
                progress_width = int((self._value / self._maximum) * track_width)
                self.indicator.configure(width=max(0, progress_width))

    def configure_value(self, value: float):
        """Set progress value (0-100)"""
        self._value = max(0, min(self._maximum, value))
        self._update_progress()

    def configure_maximum(self, maximum: float):
        """Set maximum value"""
        self._maximum = maximum
        self._update_progress()

    def start_indeterminate(self):
        """Start indeterminate animation"""
        if self.mode == "indeterminate" and not self._animation_running:
            self._animation_running = True
            self._animate_indeterminate()

    def stop_indeterminate(self):
        """Stop indeterminate animation"""
        self._animation_running = False

    def _animate_indeterminate(self):
        """Animate indeterminate progress"""
        if not self._animation_running:
            return

        # Simple animation - move indicator across track
        track_width = self.track.winfo_width()
        if track_width > 1:
            # Animation logic here - simplified for now
            pass

        # Schedule next frame
        self.after(50, self._animate_indeterminate)

    def _on_theme_changed(self, theme: Theme):
        """Handle theme changes"""
        self._setup_styling()


class ModernDropZone(tk.Frame):
    """Drag and drop zone with visual feedback"""

    def __init__(self, parent, text: str = "Drop files here",
                 on_drop: Optional[Callable[[List[str]], None]] = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.drop_text = text
        self.on_drop_callback = on_drop
        self._is_drag_active = False

        self._create_widgets()
        self._setup_styling()
        self._setup_drag_drop()

        # Subscribe to theme changes
        get_theme_manager().add_observer(self._on_theme_changed)

    def _create_widgets(self):
        """Create drop zone widgets"""
        self.label = tk.Label(self, text=self.drop_text)
        self.label.pack(expand=True, fill='both')

    def _setup_styling(self):
        """Apply Material Design 3 styling"""
        theme = get_theme_manager().current_theme
        colors = theme.colors
        typography = theme.typography

        self.configure(
            bg=colors.surface_variant,
            relief='solid',
            bd=2,
            highlightbackground=colors.outline,
            highlightthickness=0
        )

        self.label.configure(
            font=(typography.font_family_primary, typography.body_large),
            fg=colors.on_surface_variant,
            bg=colors.surface_variant,
            justify='center'
        )

    def _setup_drag_drop(self):
        """Setup drag and drop functionality"""
        # Note: Full drag-drop implementation would require tkinterdnd2
        # This is a simplified version
        self.bind('<Button-1>', self._on_click)

    def _on_click(self, event):
        """Handle click (simulate file selection)"""
        from tkinter import filedialog
        files = filedialog.askopenfilenames(
            title="Select files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if files and self.on_drop_callback:
            self.on_drop_callback(list(files))

    def set_drag_active(self, active: bool):
        """Set drag active state"""
        self._is_drag_active = active
        colors = get_theme_manager().current_theme.colors

        if active:
            self.configure(
                bg=colors.primary_container,
                highlightbackground=colors.primary,
                highlightthickness=2
            )
            self.label.configure(
                bg=colors.primary_container,
                fg=colors.on_primary_container
            )
        else:
            self._setup_styling()

    def _on_theme_changed(self, theme: Theme):
        """Handle theme changes"""
        self._setup_styling()


class ModernTabBar(tk.Frame):
    """Material Design 3 tab bar with smooth transitions"""

    def __init__(self, parent, tabs: List[str], on_tab_change: Optional[Callable[[int], None]] = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.tabs = tabs
        self.on_tab_change_callback = on_tab_change
        self._active_tab = 0
        self._tab_buttons = []

        self._create_tabs()
        self._setup_styling()

        # Subscribe to theme changes
        get_theme_manager().add_observer(self._on_theme_changed)

    def _create_tabs(self):
        """Create tab buttons"""
        for i, tab_text in enumerate(self.tabs):
            btn = tk.Button(
                self,
                text=tab_text,
                command=lambda idx=i: self._on_tab_clicked(idx)
            )
            btn.pack(side='left', fill='x', expand=True)
            self._tab_buttons.append(btn)

        # Create indicator line
        self.indicator = tk.Frame(self)
        self.indicator.pack(side='bottom', fill='x', pady=(2, 0))

    def _setup_styling(self):
        """Apply Material Design 3 styling"""
        theme = get_theme_manager().current_theme
        colors = theme.colors
        typography = theme.typography

        self.configure(bg=colors.surface)

        for i, btn in enumerate(self._tab_buttons):
            is_active = i == self._active_tab
            btn.configure(
                font=(typography.font_family_primary, typography.label_large),
                bg=colors.surface,
                fg=colors.primary if is_active else colors.on_surface_variant,
                relief='flat',
                bd=0,
                cursor='hand2',
                activebackground=colors.primary_container
            )

        # Indicator styling
        self.indicator.configure(
            bg=colors.primary,
            height=2
        )

    def _on_tab_clicked(self, index: int):
        """Handle tab click"""
        if index != self._active_tab:
            self._active_tab = index
            self._setup_styling()
            if self.on_tab_change_callback:
                self.on_tab_change_callback(index)

    def set_active_tab(self, index: int):
        """Set active tab programmatically"""
        if 0 <= index < len(self.tabs):
            self._on_tab_clicked(index)

    def _on_theme_changed(self, theme: Theme):
        """Handle theme changes"""
        self._setup_styling()