"""
PDF2PPTX v3.0 - Modern Main Window with Material Design 3

Advanced GUI application with modern UI components, responsive layout,
theme management, and enhanced user experience.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, filedialog
import webbrowser
import os
import threading
from typing import Callable, Optional, List
from pathlib import Path

# Import modern UI components
from .components.theme_manager import get_theme_manager, ThemeMode
from .components.modern_widgets import (
    ModernButton, ModernCard, ModernTextField, ModernProgressBar,
    ModernDropZone, ModernTabBar, MaterialColors, MaterialIcons
)
from .components.responsive_layout import ResponsiveContainer, BreakpointSize
from .components.animations import get_animation_manager, FadeInOut, AnimationConfig

# Import core functionality
from ..core.pdf_processor import ConversionConfig
from ..utils.error_handling import (
    UserFriendlyError, ErrorSeverity, format_exception_for_user, setup_logging
)
from ..utils.path_utils import PathManager
from ..config import get_app_config, save_app_config
from .converters import ImageConverter, PPTXConverter


class ModernProgressTracker:
    """Enhanced progress tracker with modern UI"""

    def __init__(self, progress_bar: ModernProgressBar, root: tk.Tk):
        self.progress_bar = progress_bar
        self.root = root
        self._current_value = 0
        self._maximum = 100
        self._cancelled = False

    def set_maximum(self, maximum: int) -> None:
        """Set maximum progress value"""
        self._maximum = maximum
        self.progress_bar.configure_maximum(maximum)
        self.progress_bar.configure_value(0)
        self._current_value = 0
        self._cancelled = False
        self.root.update_idletasks()

    def step(self, increment: int = 1) -> None:
        """Advance progress"""
        if self._cancelled:
            return

        self._current_value = min(self._maximum, self._current_value + increment)
        self.progress_bar.configure_value(self._current_value)
        self.root.update_idletasks()

    def cancel(self) -> None:
        """Cancel progress tracking"""
        self._cancelled = True

    def reset(self) -> None:
        """Reset progress"""
        self._current_value = 0
        self.progress_bar.configure_value(0)
        self._cancelled = False
        self.root.update_idletasks()

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled


class ModernConversionController:
    """Enhanced conversion controller with modern UI integration"""

    def __init__(self, progress_tracker: ModernProgressTracker, root: tk.Tk):
        self.progress_tracker = progress_tracker
        self.root = root
        self.path_manager = PathManager()
        self.image_converter = ImageConverter(self.progress_tracker)
        self.pptx_converter = PPTXConverter(self.progress_tracker)

    def convert_to_images(self, config: ConversionConfig) -> None:
        """Convert PDFs to images in separate thread"""
        def conversion_task():
            try:
                self.image_converter.convert_pdfs_to_images(config)
                self.root.after(0, self._on_conversion_success, "PNG conversion completed!")
            except Exception as e:
                self.root.after(0, self._on_conversion_error, e)

        threading.Thread(target=conversion_task, daemon=True).start()

    def convert_to_pptx(self, config: ConversionConfig) -> None:
        """Convert PDFs to PPTX in separate thread"""
        def conversion_task():
            try:
                self.pptx_converter.create_pptx_from_pdfs(config)
                self.root.after(0, self._on_conversion_success, "PPTX creation completed!")
            except Exception as e:
                self.root.after(0, self._on_conversion_error, e)

        threading.Thread(target=conversion_task, daemon=True).start()

    def _on_conversion_success(self, message: str):
        """Handle successful conversion"""
        self.progress_tracker.reset()
        messagebox.showinfo("Success", message)

        # Open output folder
        output_path = self.path_manager.get_output_dir()
        if output_path.exists():
            webbrowser.open(str(output_path))

    def _on_conversion_error(self, error: Exception):
        """Handle conversion error"""
        self.progress_tracker.reset()
        error_msg = format_exception_for_user(error)
        messagebox.showerror("Error", error_msg)


class ModernMainWindow:
    """PDF2PPTX v3.0 Main Window with Material Design 3"""

    def __init__(self):
        self.root = tk.Tk()
        self.theme_manager = get_theme_manager()
        self.animation_manager = get_animation_manager()

        # Configuration
        self.config = get_app_config()

        # Initialize UI components
        self._setup_window()
        self._create_widgets()
        self._setup_layout()
        self._bind_events()

        # Setup theme observer
        self.theme_manager.add_observer(self._on_theme_changed)

        # Apply initial theme
        self._apply_theme()

    def _setup_window(self):
        """Configure main window"""
        self.root.title("PDF2PPTX v3.0 - Modern PDF Converter")
        self.root.geometry("900x700")
        self.root.minsize(600, 500)

        # Set window icon (if available)
        try:
            icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass

    def _create_widgets(self):
        """Create all UI components"""
        # Main responsive container
        self.main_container = ResponsiveContainer(self.root)
        self.main_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Header section
        self._create_header()

        # Settings section
        self._create_settings_section()

        # Action buttons section
        self._create_action_section()

        # Progress section
        self._create_progress_section()

        # Footer section
        self._create_footer()

    def _create_header(self):
        """Create header with title and theme toggle"""
        header_card = ModernCard(self.main_container, elevation=2)
        self.main_container.add_responsive_widget(
            header_card,
            {
                BreakpointSize.XS: 12,
                BreakpointSize.SM: 12,
                BreakpointSize.MD: 12,
                BreakpointSize.LG: 12,
                BreakpointSize.XL: 12
            }
        )

        # Title
        title_frame = tk.Frame(header_card)
        title_frame.pack(fill='x', pady=10)

        self.title_label = tk.Label(
            title_frame,
            text="PDF2PPTX v3.0",
            font=("Segoe UI", 24, "bold")
        )
        self.title_label.pack(side='left')

        # Theme toggle button
        self.theme_button = ModernButton(
            title_frame,
            text=f"{MaterialIcons.REFRESH} Dark Mode",
            style="outlined",
            command=self._toggle_theme
        )
        self.theme_button.pack(side='right')

        # Subtitle
        self.subtitle_label = tk.Label(
            header_card,
            text="Modern PDF to PNG/PPTX converter with Material Design 3",
            font=("Segoe UI", 12)
        )
        self.subtitle_label.pack(pady=(0, 10))

    def _create_settings_section(self):
        """Create settings section with tabs"""
        settings_card = ModernCard(self.main_container, elevation=1)
        self.main_container.add_responsive_widget(
            settings_card,
            {
                BreakpointSize.XS: 12,
                BreakpointSize.SM: 12,
                BreakpointSize.MD: 12,
                BreakpointSize.LG: 8,
                BreakpointSize.XL: 8
            }
        )

        # Settings tabs
        self.settings_tabs = ModernTabBar(
            settings_card,
            tabs=["Conversion", "Advanced", "Preferences"],
            on_tab_change=self._on_settings_tab_change
        )
        self.settings_tabs.pack(fill='x', pady=(10, 0))

        # Tab content frame
        self.tab_content = tk.Frame(settings_card)
        self.tab_content.pack(fill='both', expand=True, pady=10)

        # Create tab contents
        self._create_conversion_tab()
        self._create_advanced_tab()
        self._create_preferences_tab()

        # Show first tab
        self._show_tab_content(0)

    def _create_conversion_tab(self):
        """Create conversion settings tab"""
        self.conversion_frame = tk.Frame(self.tab_content)

        # Scale factor setting
        scale_frame = tk.Frame(self.conversion_frame)
        scale_frame.pack(fill='x', pady=10)

        tk.Label(scale_frame, text="Scale Factor:", font=("Segoe UI", 12)).pack(anchor='w')
        self.scale_field = ModernTextField(
            scale_frame,
            placeholder="1.5",
            validator=self._validate_scale
        )
        self.scale_field.pack(fill='x', pady=(5, 0))
        self.scale_field.set(str(self.config.get('scale_factor', 1.5)))

        # Auto-rotate setting
        rotate_frame = tk.Frame(self.conversion_frame)
        rotate_frame.pack(fill='x', pady=10)

        self.auto_rotate_var = tk.BooleanVar(value=self.config.get('auto_rotate', True))
        auto_rotate_check = tk.Checkbutton(
            rotate_frame,
            text="Auto-rotate portrait pages to landscape",
            variable=self.auto_rotate_var,
            font=("Segoe UI", 11)
        )
        auto_rotate_check.pack(anchor='w')

    def _create_advanced_tab(self):
        """Create advanced settings tab"""
        self.advanced_frame = tk.Frame(self.tab_content)

        # DPI setting
        dpi_frame = tk.Frame(self.advanced_frame)
        dpi_frame.pack(fill='x', pady=10)

        tk.Label(dpi_frame, text="Output DPI:", font=("Segoe UI", 12)).pack(anchor='w')
        self.dpi_field = ModernTextField(
            dpi_frame,
            placeholder="300",
            validator=self._validate_dpi
        )
        self.dpi_field.pack(fill='x', pady=(5, 0))
        self.dpi_field.set(str(self.config.get('dpi', 300)))

        # Quality setting
        quality_frame = tk.Frame(self.advanced_frame)
        quality_frame.pack(fill='x', pady=10)

        tk.Label(quality_frame, text="JPEG Quality (%):", font=("Segoe UI", 12)).pack(anchor='w')
        self.quality_field = ModernTextField(
            quality_frame,
            placeholder="95",
            validator=self._validate_quality
        )
        self.quality_field.pack(fill='x', pady=(5, 0))
        self.quality_field.set(str(self.config.get('quality', 95)))

    def _create_preferences_tab(self):
        """Create preferences tab"""
        self.preferences_frame = tk.Frame(self.tab_content)

        # Auto-open results
        auto_open_frame = tk.Frame(self.preferences_frame)
        auto_open_frame.pack(fill='x', pady=10)

        self.auto_open_var = tk.BooleanVar(value=self.config.get('auto_open_results', True))
        auto_open_check = tk.Checkbutton(
            auto_open_frame,
            text="Automatically open results folder",
            variable=self.auto_open_var,
            font=("Segoe UI", 11)
        )
        auto_open_check.pack(anchor='w')

        # Show notifications
        notifications_frame = tk.Frame(self.preferences_frame)
        notifications_frame.pack(fill='x', pady=10)

        self.notifications_var = tk.BooleanVar(value=self.config.get('show_notifications', True))
        notifications_check = tk.Checkbutton(
            notifications_frame,
            text="Show completion notifications",
            variable=self.notifications_var,
            font=("Segoe UI", 11)
        )
        notifications_check.pack(anchor='w')

    def _create_action_section(self):
        """Create action buttons section"""
        action_card = ModernCard(self.main_container, elevation=1)
        self.main_container.add_responsive_widget(
            action_card,
            {
                BreakpointSize.XS: 12,
                BreakpointSize.SM: 12,
                BreakpointSize.MD: 12,
                BreakpointSize.LG: 4,
                BreakpointSize.XL: 4
            }
        )

        # File drop zone
        self.drop_zone = ModernDropZone(
            action_card,
            text=f"{MaterialIcons.UPLOAD}\\n\\nDrop PDF files here\\nor click to select",
            on_drop=self._on_files_dropped
        )
        self.drop_zone.pack(fill='both', expand=True, pady=10)

        # Action buttons
        button_frame = tk.Frame(action_card)
        button_frame.pack(fill='x', pady=10)

        self.convert_png_btn = ModernButton(
            button_frame,
            text=f"{MaterialIcons.FILE} Convert to PNG",
            style="filled",
            command=self._convert_to_png
        )
        self.convert_png_btn.pack(fill='x', pady=(0, 5))

        self.convert_pptx_btn = ModernButton(
            button_frame,
            text=f"{MaterialIcons.FILE} Convert to PPTX",
            style="filled",
            command=self._convert_to_pptx
        )
        self.convert_pptx_btn.pack(fill='x', pady=5)

        self.clear_btn = ModernButton(
            button_frame,
            text=f"{MaterialIcons.DELETE} Clear Folders",
            style="outlined",
            command=self._clear_folders
        )
        self.clear_btn.pack(fill='x', pady=5)

    def _create_progress_section(self):
        """Create progress section"""
        progress_card = ModernCard(self.main_container, elevation=1)
        self.main_container.add_responsive_widget(
            progress_card,
            {
                BreakpointSize.XS: 12,
                BreakpointSize.SM: 12,
                BreakpointSize.MD: 12,
                BreakpointSize.LG: 12,
                BreakpointSize.XL: 12
            }
        )

        tk.Label(progress_card, text="Progress", font=("Segoe UI", 14, "bold")).pack(anchor='w', pady=(10, 5))

        self.progress_bar = ModernProgressBar(progress_card)
        self.progress_bar.pack(fill='x', pady=10)

        self.progress_tracker = ModernProgressTracker(self.progress_bar, self.root)
        self.controller = ModernConversionController(self.progress_tracker, self.root)

    def _create_footer(self):
        """Create footer with info and links"""
        footer_card = ModernCard(self.main_container, elevation=0)
        self.main_container.add_responsive_widget(
            footer_card,
            {
                BreakpointSize.XS: 12,
                BreakpointSize.SM: 12,
                BreakpointSize.MD: 12,
                BreakpointSize.LG: 12,
                BreakpointSize.XL: 12
            }
        )

        footer_frame = tk.Frame(footer_card)
        footer_frame.pack(fill='x', pady=10)

        self.info_label = tk.Label(
            footer_frame,
            text="PDF2PPTX v3.0 | Material Design 3 | Python + tkinter",
            font=("Segoe UI", 10)
        )
        self.info_label.pack(side='left')

        help_btn = ModernButton(
            footer_frame,
            text=f"{MaterialIcons.INFO} Help",
            style="text",
            command=self._show_help
        )
        help_btn.pack(side='right')

    def _setup_layout(self):
        """Setup responsive layout"""
        # The layout is already configured in _create_widgets
        pass

    def _bind_events(self):
        """Bind window events"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_settings_tab_change(self, tab_index: int):
        """Handle settings tab change"""
        self._show_tab_content(tab_index)

    def _show_tab_content(self, tab_index: int):
        """Show specific tab content with animation"""
        # Hide all tab frames
        for frame in [self.conversion_frame, self.advanced_frame, self.preferences_frame]:
            frame.pack_forget()

        # Show selected tab frame
        frames = [self.conversion_frame, self.advanced_frame, self.preferences_frame]
        if 0 <= tab_index < len(frames):
            selected_frame = frames[tab_index]
            selected_frame.pack(fill='both', expand=True)

            # Animate tab transition
            config = AnimationConfig(duration=0.2)
            animation = FadeInOut.fade_in(selected_frame, config)
            self.animation_manager.start_animation(f"tab_transition_{tab_index}", animation)

    def _toggle_theme(self):
        """Toggle between light and dark themes"""
        self.theme_manager.toggle_theme()

    def _on_theme_changed(self, theme):
        """Handle theme changes"""
        self._apply_theme()

        # Update theme button text
        mode_text = "Light Mode" if theme.mode.value == "dark" else "Dark Mode"
        self.theme_button.configure(text=f"{MaterialIcons.REFRESH} {mode_text}")

    def _apply_theme(self):
        """Apply current theme to all components"""
        theme = self.theme_manager.current_theme
        colors = theme.colors

        # Apply to root window
        self.root.configure(bg=colors.background)

        # Apply to labels
        for label in [self.title_label, self.subtitle_label, self.info_label]:
            label.configure(
                bg=colors.background,
                fg=colors.on_background
            )

    def _validate_scale(self, value: str) -> bool:
        """Validate scale factor input"""
        try:
            scale = float(value)
            return 0.1 <= scale <= 10.0
        except ValueError:
            return False

    def _validate_dpi(self, value: str) -> bool:
        """Validate DPI input"""
        try:
            dpi = int(value)
            return 72 <= dpi <= 600
        except ValueError:
            return False

    def _validate_quality(self, value: str) -> bool:
        """Validate JPEG quality input"""
        try:
            quality = int(value)
            return 1 <= quality <= 100
        except ValueError:
            return False

    def _on_files_dropped(self, files: List[str]):
        """Handle dropped files"""
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        if pdf_files:
            messagebox.showinfo("Files Selected", f"Selected {len(pdf_files)} PDF file(s)")
        else:
            messagebox.showwarning("No PDF Files", "Please select PDF files only")

    def _convert_to_png(self):
        """Convert PDFs to PNG images"""
        config = self._get_conversion_config()
        if config:
            self.controller.convert_to_images(config)

    def _convert_to_pptx(self):
        """Convert PDFs to PPTX"""
        config = self._get_conversion_config()
        if config:
            self.controller.convert_to_pptx(config)

    def _get_conversion_config(self) -> Optional[ConversionConfig]:
        """Get current conversion configuration"""
        try:
            return ConversionConfig(
                scale_factor=float(self.scale_field.get() or "1.5"),
                auto_rotate=self.auto_rotate_var.get(),
                dpi=int(self.dpi_field.get() or "300"),
                quality=int(self.quality_field.get() or "95")
            )
        except ValueError as e:
            messagebox.showerror("Invalid Configuration", f"Please check your settings: {e}")
            return None

    def _clear_folders(self):
        """Clear input/output folders"""
        if messagebox.askyesno("Confirm", "Clear all input and output folders?"):
            try:
                path_manager = PathManager()
                path_manager.clear_directories()
                messagebox.showinfo("Success", "Folders cleared successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear folders: {e}")

    def _show_help(self):
        """Show help dialog"""
        help_text = """
PDF2PPTX v3.0 Help

Features:
• Convert PDF files to PNG images
• Convert PDF files directly to PPTX presentations
• Automatic portrait-to-landscape rotation
• Material Design 3 interface
• Dark/Light theme support
• Responsive layout

Usage:
1. Drop PDF files or click the drop zone to select files
2. Adjust settings in the Settings tabs
3. Click Convert to PNG or Convert to PPTX
4. Results will open automatically when complete

Settings:
• Scale Factor: Image resolution multiplier (0.1-10.0)
• DPI: Output image quality (72-600)
• Quality: JPEG compression quality (1-100%)
• Auto-rotate: Automatically rotate portrait pages
        """

        messagebox.showinfo("Help", help_text)

    def _save_preferences(self):
        """Save current preferences"""
        try:
            config = {
                'scale_factor': float(self.scale_field.get() or "1.5"),
                'auto_rotate': self.auto_rotate_var.get(),
                'dpi': int(self.dpi_field.get() or "300"),
                'quality': int(self.quality_field.get() or "95"),
                'auto_open_results': self.auto_open_var.get(),
                'show_notifications': self.notifications_var.get(),
                'theme_mode': self.theme_manager.current_theme.mode.value
            }
            save_app_config(config)
        except Exception as e:
            print(f"Failed to save preferences: {e}")

    def _on_closing(self):
        """Handle window closing"""
        self._save_preferences()
        self.animation_manager.stop_all_animations()
        self.root.destroy()

    def run(self):
        """Run the application"""
        setup_logging()

        # Show startup animation
        config = AnimationConfig(duration=0.5)
        animation = FadeInOut.fade_in(self.main_container, config)
        self.animation_manager.start_animation("startup", animation)

        self.root.mainloop()


def main():
    """Main entry point for PDF2PPTX v3.0"""
    app = ModernMainWindow()
    app.run()


if __name__ == "__main__":
    main()