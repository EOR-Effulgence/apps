"""
Main view component implementing the View part of MVP pattern.
Focuses purely on UI presentation without business logic.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Protocol, Optional, Dict, Any
from pathlib import Path

from ..widgets import ProgressWidget


class MainViewInterface(Protocol):
    """Interface for main view interactions."""

    def on_convert_to_images(self) -> None:
        """Called when user requests PDF to PNG conversion."""
        ...

    def on_convert_to_powerpoint(self) -> None:
        """Called when user requests PDF to PPTX conversion."""
        ...

    def on_reset_folders(self) -> None:
        """Called when user requests folder reset."""
        ...

    def on_save_powerpoint_settings(self) -> None:
        """Called when user saves PowerPoint settings."""
        ...


class MainView:
    """
    Main application view implementing clean UI separation.
    Handles only UI presentation and user interaction events.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.presenter: Optional[MainViewInterface] = None

        # UI state variables
        self.scale_var = tk.StringVar(value="1.5")
        self.auto_rotate_var = tk.BooleanVar(value=True)
        self.pptx_vars: Dict[str, tk.StringVar] = {}

        # UI components
        self.progress_widget: Optional[ProgressWidget] = None
        self.operation_buttons: Dict[str, tk.Button] = {}

        # Initialize UI
        self._setup_window()
        self._create_widgets()

    def set_presenter(self, presenter: MainViewInterface) -> None:
        """Set the presenter for this view."""
        self.presenter = presenter

    def _setup_window(self) -> None:
        """Configure the main window."""
        self.root.title("PDF2PPTX Converter v3.0")
        self.root.resizable(False, False)

        # Center window on screen
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        pos_x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

        # Configure window icon and style
        try:
            # Set window icon if available
            icon_path = Path(__file__).parent.parent.parent.parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass  # Ignore icon loading errors

    def _create_widgets(self) -> None:
        """Create and layout all UI widgets."""
        # Main container
        main_frame = tk.Frame(self.root, padx=20, pady=15)
        main_frame.pack(fill="both", expand=True)

        # Configuration section
        self._create_configuration_section(main_frame)

        # PowerPoint settings section
        self._create_powerpoint_section(main_frame)

        # Operation buttons section
        self._create_buttons_section(main_frame)

        # Progress section
        self._create_progress_section(main_frame)

        # Status section
        self._create_status_section(main_frame)

    def _create_configuration_section(self, parent: tk.Widget) -> None:
        """Create conversion configuration section."""
        config_frame = tk.LabelFrame(
            parent,
            text="変換設定",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        config_frame.pack(fill="x", pady=(0, 10))

        # Scale factor setting
        scale_frame = tk.Frame(config_frame)
        scale_frame.pack(fill="x", pady=(0, 5))

        tk.Label(
            scale_frame,
            text="スケール倍率:",
            font=("Arial", 10)
        ).pack(side="left")

        scale_entry = tk.Entry(
            scale_frame,
            textvariable=self.scale_var,
            width=8,
            font=("Arial", 10)
        )
        scale_entry.pack(side="left", padx=(10, 5))

        tk.Label(
            scale_frame,
            text="(推奨: 1.0-3.0)",
            font=("Arial", 9),
            fg="gray"
        ).pack(side="left")

        # Auto-rotation checkbox
        auto_rotate_check = tk.Checkbutton(
            config_frame,
            text="縦長ページを横向きに自動回転",
            variable=self.auto_rotate_var,
            font=("Arial", 10)
        )
        auto_rotate_check.pack(fill="x", pady=(5, 0))

    def _create_powerpoint_section(self, parent: tk.Widget) -> None:
        """Create PowerPoint settings section."""
        pptx_frame = tk.LabelFrame(
            parent,
            text="PowerPoint ラベル設定",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        pptx_frame.pack(fill="x", pady=(0, 10))

        # Color settings row
        color_frame = tk.Frame(pptx_frame)
        color_frame.pack(fill="x", pady=(0, 5))

        # Text color
        tk.Label(color_frame, text="文字色:", font=("Arial", 9)).pack(side="left")
        self.pptx_vars['text_color'] = tk.StringVar(value="#000000")
        tk.Entry(
            color_frame,
            textvariable=self.pptx_vars['text_color'],
            width=8,
            font=("Arial", 9)
        ).pack(side="left", padx=(5, 10))

        # Background color
        tk.Label(color_frame, text="背景色:", font=("Arial", 9)).pack(side="left")
        self.pptx_vars['background_color'] = tk.StringVar(value="#FFFFFF")
        tk.Entry(
            color_frame,
            textvariable=self.pptx_vars['background_color'],
            width=8,
            font=("Arial", 9)
        ).pack(side="left", padx=(5, 10))

        # Border color
        tk.Label(color_frame, text="枠線色:", font=("Arial", 9)).pack(side="left")
        self.pptx_vars['border_color'] = tk.StringVar(value="#FF0000")
        tk.Entry(
            color_frame,
            textvariable=self.pptx_vars['border_color'],
            width=8,
            font=("Arial", 9)
        ).pack(side="left", padx=(5, 0))

        # Font settings row
        font_frame = tk.Frame(pptx_frame)
        font_frame.pack(fill="x", pady=(5, 5))

        # Font name
        tk.Label(font_frame, text="フォント:", font=("Arial", 9)).pack(side="left")
        self.pptx_vars['font_name'] = tk.StringVar(value="Arial")
        tk.Entry(
            font_frame,
            textvariable=self.pptx_vars['font_name'],
            width=12,
            font=("Arial", 9)
        ).pack(side="left", padx=(5, 10))

        # Font size
        tk.Label(font_frame, text="サイズ:", font=("Arial", 9)).pack(side="left")
        self.pptx_vars['font_size'] = tk.StringVar(value="12")
        tk.Entry(
            font_frame,
            textvariable=self.pptx_vars['font_size'],
            width=4,
            font=("Arial", 9)
        ).pack(side="left", padx=(5, 10))

        # Position setting
        tk.Label(font_frame, text="位置:", font=("Arial", 9)).pack(side="left")
        self.pptx_vars['position'] = tk.StringVar(value="bottom-right")
        position_combo = ttk.Combobox(
            font_frame,
            textvariable=self.pptx_vars['position'],
            values=["top-left", "top-right", "bottom-left", "bottom-right"],
            state="readonly",
            width=12,
            font=("Arial", 9)
        )
        position_combo.pack(side="left", padx=(5, 0))

        # Save button
        save_button = tk.Button(
            pptx_frame,
            text="💾 設定を保存",
            command=self._on_save_powerpoint_settings,
            font=("Arial", 9),
            relief="groove"
        )
        save_button.pack(pady=(10, 0))

    def _create_buttons_section(self, parent: tk.Widget) -> None:
        """Create operation buttons section."""
        buttons_frame = tk.Frame(parent)
        buttons_frame.pack(fill="x", pady=(0, 10))

        button_config = {
            "width": 35,
            "height": 2,
            "font": ("Arial", 11),
            "relief": "groove",
            "borderwidth": 2
        }

        # PDF to PNG button
        self.operation_buttons['pdf2png'] = tk.Button(
            buttons_frame,
            text="📄 PDF → PNG 変換",
            command=self._on_convert_to_images,
            bg="#E3F2FD",
            **button_config
        )
        self.operation_buttons['pdf2png'].pack(pady=2)

        # PDF to PPTX button
        self.operation_buttons['pdf2pptx'] = tk.Button(
            buttons_frame,
            text="📈 PDF → PPTX 変換 (A3横)",
            command=self._on_convert_to_powerpoint,
            bg="#E8F5E8",
            **button_config
        )
        self.operation_buttons['pdf2pptx'].pack(pady=2)

        # Reset folders button
        self.operation_buttons['reset'] = tk.Button(
            buttons_frame,
            text="🧹 Input/Output フォルダ初期化",
            command=self._on_reset_folders,
            bg="#FFF3E0",
            **button_config
        )
        self.operation_buttons['reset'].pack(pady=2)

    def _create_progress_section(self, parent: tk.Widget) -> None:
        """Create progress tracking section."""
        self.progress_widget = ProgressWidget(parent, width=420)
        self.progress_widget.pack(pady=(0, 10))

    def _create_status_section(self, parent: tk.Widget) -> None:
        """Create status display section."""
        status_frame = tk.Frame(parent)
        status_frame.pack(fill="x")

        self.status_label = tk.Label(
            status_frame,
            text="作業ディレクトリ: 読み込み中...",
            font=("Arial", 9),
            fg="gray",
            justify="left"
        )
        self.status_label.pack()

    # Event handlers that delegate to presenter
    def _on_convert_to_images(self) -> None:
        """Handle PDF to PNG conversion request."""
        if self.presenter:
            self.presenter.on_convert_to_images()

    def _on_convert_to_powerpoint(self) -> None:
        """Handle PDF to PPTX conversion request."""
        if self.presenter:
            self.presenter.on_convert_to_powerpoint()

    def _on_reset_folders(self) -> None:
        """Handle folder reset request."""
        if self.presenter:
            self.presenter.on_reset_folders()

    def _on_save_powerpoint_settings(self) -> None:
        """Handle PowerPoint settings save request."""
        if self.presenter:
            self.presenter.on_save_powerpoint_settings()

    # Public interface for presenter to control view
    def get_conversion_settings(self) -> Dict[str, Any]:
        """Get current conversion settings from UI."""
        return {
            'scale_factor': self.scale_var.get(),
            'auto_rotate': self.auto_rotate_var.get()
        }

    def get_powerpoint_settings(self) -> Dict[str, str]:
        """Get current PowerPoint settings from UI."""
        return {key: var.get() for key, var in self.pptx_vars.items()}

    def set_powerpoint_settings(self, settings: Dict[str, str]) -> None:
        """Set PowerPoint settings in UI."""
        for key, value in settings.items():
            if key in self.pptx_vars:
                self.pptx_vars[key].set(value)

    def set_status(self, status: str) -> None:
        """Update status label."""
        self.status_label.configure(text=status)

    def set_buttons_enabled(self, enabled: bool) -> None:
        """Enable or disable operation buttons."""
        state = "normal" if enabled else "disabled"
        for button in self.operation_buttons.values():
            button.configure(state=state)

    def show_info(self, title: str, message: str) -> None:
        """Show information dialog."""
        messagebox.showinfo(title, message)

    def show_warning(self, title: str, message: str) -> None:
        """Show warning dialog."""
        messagebox.showwarning(title, message)

    def show_error(self, title: str, message: str) -> None:
        """Show error dialog."""
        messagebox.showerror(title, message)

    def ask_yes_no(self, title: str, message: str) -> bool:
        """Show yes/no confirmation dialog."""
        return messagebox.askyesno(title, message)

    def start_progress(self, maximum: int, status: str) -> None:
        """Start progress tracking."""
        if self.progress_widget:
            self.progress_widget.start_operation(maximum, status)

    def update_progress(self, increment: int = 1, status: Optional[str] = None) -> None:
        """Update progress."""
        if self.progress_widget:
            self.progress_widget.update_progress(increment, status)

    def complete_progress(self, status: str = "完了") -> None:
        """Complete progress tracking."""
        if self.progress_widget:
            self.progress_widget.complete_operation(status)

    def error_progress(self, status: str = "エラーが発生しました") -> None:
        """Mark progress as error."""
        if self.progress_widget:
            self.progress_widget.error_operation(status)

    def reset_progress(self) -> None:
        """Reset progress to initial state."""
        if self.progress_widget:
            self.progress_widget.reset()

    def run(self) -> None:
        """Start the main UI loop."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.destroy()
        except Exception as e:
            self.show_error(
                "アプリケーションエラー",
                f"アプリケーションでエラーが発生しました:\n\n{str(e)}"
            )