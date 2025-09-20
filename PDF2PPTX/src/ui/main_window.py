"""
Refactored main GUI application with improved architecture.
Separates UI logic from business logic and implements proper error handling.
"""

from __future__ import annotations

import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk
from typing import Callable, Optional
from pathlib import Path

from ..core.pdf_processor import ConversionConfig
from ..utils.error_handling import (
    UserFriendlyError,
    ErrorSeverity,
    format_exception_for_user,
    setup_logging
)
from ..utils.path_utils import PathManager
from ..config import get_app_config, save_app_config
from .converters import ImageConverter, PPTXConverter


class ProgressTracker:
    """
    Handles progress tracking and UI updates during conversion operations.
    """

    def __init__(self, progress_bar: ttk.Progressbar, root: tk.Tk):
        self.progress_bar = progress_bar
        self.root = root
        self._current_value = 0
        self._maximum = 0
        self._cancelled = False

    def set_maximum(self, maximum: int) -> None:
        """Set the maximum value for progress tracking."""
        self._maximum = maximum
        self.progress_bar.configure(maximum=maximum, value=0)
        self._current_value = 0
        self._cancelled = False
        self.root.update_idletasks()

    def step(self, increment: int = 1) -> None:
        """Advance progress by specified increment."""
        if self._cancelled:
            return

        self._current_value += increment
        self.progress_bar.configure(value=self._current_value)
        self.root.update_idletasks()

    def reset(self) -> None:
        """Reset progress to zero."""
        self._current_value = 0
        self.progress_bar.configure(value=0)

    def cancel(self) -> None:
        """Mark operation as cancelled."""
        self._cancelled = True

    @property
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self._cancelled


class ConversionController:
    """
    Controls conversion operations with proper error handling and progress tracking.
    """

    def __init__(self, path_manager: PathManager, progress_tracker: ProgressTracker):
        self.path_manager = path_manager
        self.progress_tracker = progress_tracker
        self.logger = setup_logging()

    def convert_to_images(self, config: ConversionConfig) -> None:
        """
        Convert PDFs to images with progress tracking.

        Args:
            config: Conversion configuration

        Raises:
            UserFriendlyError: If conversion fails
        """
        try:
            converter = ImageConverter(self.path_manager, self.progress_tracker)
            output_files = converter.convert_all_pdfs(config)

            if output_files:
                self._show_completion_message(
                    "PNG変換完了",
                    f"変換が完了しました。{len(output_files)}個のファイルが生成されました。",
                    self.path_manager.output_dir
                )
            else:
                messagebox.showwarning("警告", "変換するPDFファイルが見つかりませんでした。")

        except UserFriendlyError:
            raise  # Re-raise user-friendly errors
        except Exception as e:
            self.logger.error(f"Image conversion failed: {e}", exc_info=True)
            raise UserFriendlyError(
                message="PNG変換中に予期しないエラーが発生しました",
                suggestion="アプリケーションを再起動してお試しください",
                original_error=e
            )
        finally:
            self.progress_tracker.reset()

    def convert_to_pptx(self, config: ConversionConfig) -> None:
        """
        Convert PDFs to PPTX with progress tracking.

        Args:
            config: Conversion configuration

        Raises:
            UserFriendlyError: If conversion fails
        """
        try:
            converter = PPTXConverter(self.path_manager, self.progress_tracker)
            output_file = converter.convert_all_pdfs(config)

            if output_file:
                self._show_completion_message(
                    "PPTX変換完了",
                    f"PowerPointファイルが作成されました。",
                    output_file
                )
            else:
                messagebox.showwarning("警告", "変換するPDFファイルが見つかりませんでした。")

        except UserFriendlyError:
            raise  # Re-raise user-friendly errors
        except Exception as e:
            self.logger.error(f"PPTX conversion failed: {e}", exc_info=True)
            raise UserFriendlyError(
                message="PPTX変換中に予期しないエラーが発生しました",
                suggestion="アプリケーションを再起動してお試しください",
                original_error=e
            )
        finally:
            self.progress_tracker.reset()

    def reset_folders(self) -> None:
        """
        Reset input and output folders.

        Raises:
            UserFriendlyError: If reset fails
        """
        try:
            input_count = self.path_manager.clean_directory(self.path_manager.input_dir)
            output_count = self.path_manager.clean_directory(self.path_manager.output_dir)

            total_cleaned = input_count + output_count
            messagebox.showinfo(
                "フォルダ初期化完了",
                f"Input/Outputフォルダを初期化しました。\n削除されたアイテム数: {total_cleaned}"
            )

        except Exception as e:
            self.logger.error(f"Folder reset failed: {e}", exc_info=True)
            raise UserFriendlyError(
                message="フォルダの初期化に失敗しました",
                suggestion="ファイルが他のプログラムで使用されていないか確認してください",
                original_error=e
            )

    def _show_completion_message(self, title: str, message: str, path: Path) -> None:
        """Show completion message and open output location."""
        messagebox.showinfo(title, f"{message}\n\n保存先: {path}")
        try:
            webbrowser.open(str(path))
        except Exception:
            # Silently fail if can't open file browser
            pass


class MainWindow:
    """
    Main application window with improved error handling and user experience.
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF2PPTX Converter")
        self.root.resizable(False, False)

        # Initialize components
        self.path_manager = PathManager()
        self._setup_logging()
        self._validate_environment()
        self._create_widgets()
        self._setup_controller()

    def _setup_logging(self) -> None:
        """Set up application logging."""
        log_file = self.path_manager.base_path / "logs" / "conversion.log"
        self.logger = setup_logging(log_file)

    def _validate_environment(self) -> None:
        """Validate application environment on startup."""
        try:
            self.path_manager.validate_working_directory()
        except Exception as e:
            messagebox.showerror(
                "初期化エラー",
                f"アプリケーションの初期化に失敗しました:\n\n{format_exception_for_user(e)}"
            )
            self.root.destroy()
            return

    def _create_widgets(self) -> None:
        """Create and layout GUI widgets."""
        # Main menu bar
        self._create_menu_bar()

        # Configuration frame
        config_frame = self.theme_manager.create_styled_frame(self.root)
        config_frame.pack(padx=10, pady=10, fill="x")

        # Scale factor input
        tk.Label(config_frame, text="スケール倍率:", font=("Arial", 10)).grid(
            row=0, column=0, sticky="e", padx=(0, 5), pady=5
        )

        self.scale_var = tk.StringVar(value="1.5")
        self.scale_entry = tk.Entry(config_frame, textvariable=self.scale_var, width=8)
        self.scale_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(config_frame, text="(推奨: 1.0-3.0)", font=("Arial", 8), fg="gray").grid(
            row=0, column=2, padx=(5, 0), pady=5, sticky="w"
        )

        # Auto-rotation checkbox
        self.auto_rotate_var = tk.BooleanVar(value=True)
        self.auto_rotate_check = tk.Checkbutton(
            config_frame,
            text="縦長ページを横向きに自動回転",
            variable=self.auto_rotate_var,
            font=("Arial", 10)
        )
        self.auto_rotate_check.grid(row=1, column=0, columnspan=3, pady=(0, 5), sticky="w")

        # PowerPoint label settings frame
        pptx_frame = tk.LabelFrame(self.root, text="PowerPoint ラベル設定", font=("Arial", 10))
        pptx_frame.pack(padx=10, pady=5, fill="x")

        # Create PowerPoint settings UI
        self._create_powerpoint_settings(pptx_frame)

        # Buttons frame
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(padx=10, pady=(0, 10), fill="x")

        button_config = {"width": 35, "height": 2, "font": ("Arial", 10)}

        self.btn_pdf2png = self.theme_manager.create_styled_button(
            buttons_frame,
            text="🖼️ PDF → PNG 変換",
            command=self._safe_execute(self._convert_to_images),
            **button_config
        )
        self.btn_pdf2png.pack(pady=3)

        self.btn_pdf2pptx = self.theme_manager.create_styled_button(
            buttons_frame,
            text="📊 PDF → PPTX 変換 (A3横)",
            command=self._safe_execute(self._convert_to_pptx),
            **button_config
        )
        self.btn_pdf2pptx.pack(pady=3)

        self.btn_reset = self.theme_manager.create_styled_button(
            buttons_frame,
            text="🗂️ Input/Output フォルダ初期化",
            command=self._safe_execute(self._reset_folders),
            **button_config
        )
        self.btn_reset.pack(pady=3)

        # Progress bar
        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=380,
            mode="determinate"
        )
        self.progress.pack(padx=10, pady=(0, 10))

        # Status label
        self.status_label = tk.Label(
            self.root,
            text=f"作業ディレクトリ: {self.path_manager.get_relative_path(self.path_manager.base_path)}",
            font=("Arial", 8),
            fg="gray"
        )
        self.status_label.pack(pady=(0, 5))

    def _setup_controller(self) -> None:
        """Set up the conversion controller."""
        progress_tracker = ProgressTracker(self.progress, self.root)
        self.controller = ConversionController(self.path_manager, progress_tracker)

    def _safe_execute(self, operation: Callable[[], None]) -> Callable[[], None]:
        """
        Wrap operation with error handling for GUI safety.

        Args:
            operation: Operation to wrap

        Returns:
            Wrapped operation that handles errors safely
        """
        def wrapped_operation():
            try:
                # Disable buttons during operation
                self._set_buttons_enabled(False)
                operation()
            except UserFriendlyError as e:
                self._show_error(e)
            except Exception as e:
                self.logger.error(f"Unexpected error in {operation.__name__}: {e}", exc_info=True)
                self._show_error(UserFriendlyError(
                    message="予期しないエラーが発生しました",
                    suggestion="アプリケーションを再起動してお試しください",
                    original_error=e
                ))
            finally:
                # Re-enable buttons
                self._set_buttons_enabled(True)

        return wrapped_operation

    def _set_buttons_enabled(self, enabled: bool) -> None:
        """Enable or disable all operation buttons."""
        state = "normal" if enabled else "disabled"
        self.btn_pdf2png.configure(state=state)
        self.btn_pdf2pptx.configure(state=state)
        self.btn_reset.configure(state=state)

    def _get_conversion_config(self) -> ConversionConfig:
        """
        Get conversion configuration from GUI inputs.

        Returns:
            Validated conversion configuration

        Raises:
            UserFriendlyError: If configuration is invalid
        """
        try:
            scale_factor = float(self.scale_var.get())
        except ValueError:
            raise UserFriendlyError(
                message="スケール倍率は数値で入力してください",
                suggestion="例: 1.5 または 2.0"
            )

        config = ConversionConfig(
            scale_factor=scale_factor,
            auto_rotate=self.auto_rotate_var.get()
        )

        # Validate configuration
        try:
            from ..core.pdf_processor import validate_conversion_config
            validate_conversion_config(config)
        except ValueError as e:
            raise UserFriendlyError(
                message=f"設定が無効です: {e}",
                suggestion="有効な値の範囲で入力してください"
            )

        return config

    def _convert_to_images(self) -> None:
        """Handle PNG conversion button click."""
        config = self._get_conversion_config()
        self.controller.convert_to_images(config)

    def _convert_to_pptx(self) -> None:
        """Handle PPTX conversion button click."""
        config = self._get_conversion_config()
        self.controller.convert_to_pptx(config)

    def _reset_folders(self) -> None:
        """Handle folder reset button click."""
        # Confirm before destructive operation
        result = messagebox.askyesno(
            "確認",
            "Input/Outputフォルダの全ファイルが削除されます。\n\n続行しますか？",
            icon="warning"
        )
        if result:
            self.controller.reset_folders()

    def _create_powerpoint_settings(self, parent_frame) -> None:
        """Create PowerPoint label configuration UI."""
        # Load current configuration
        config = get_app_config()
        label_config = config.powerpoint_label

        # Store variables for configuration
        self.pptx_vars = {}

        # Text color setting
        color_frame = tk.Frame(parent_frame)
        color_frame.pack(fill="x", padx=5, pady=2)

        tk.Label(color_frame, text="文字色:", font=("Arial", 9)).pack(side="left")
        self.pptx_vars['text_color'] = tk.StringVar(value=label_config.text_color)
        text_color_entry = tk.Entry(color_frame, textvariable=self.pptx_vars['text_color'], width=8)
        text_color_entry.pack(side="left", padx=(5, 0))

        # Background color setting
        tk.Label(color_frame, text="背景色:", font=("Arial", 9)).pack(side="left", padx=(10, 0))
        self.pptx_vars['background_color'] = tk.StringVar(value=label_config.background_color)
        bg_color_entry = tk.Entry(color_frame, textvariable=self.pptx_vars['background_color'], width=8)
        bg_color_entry.pack(side="left", padx=(5, 0))

        # Border color setting (set to red as requested)
        tk.Label(color_frame, text="枠線色:", font=("Arial", 9)).pack(side="left", padx=(10, 0))
        self.pptx_vars['border_color'] = tk.StringVar(value="#FF0000")  # Red as requested
        border_color_entry = tk.Entry(color_frame, textvariable=self.pptx_vars['border_color'], width=8)
        border_color_entry.pack(side="left", padx=(5, 0))

        # Font settings frame
        font_frame = tk.Frame(parent_frame)
        font_frame.pack(fill="x", padx=5, pady=2)

        tk.Label(font_frame, text="フォント:", font=("Arial", 9)).pack(side="left")
        self.pptx_vars['font_name'] = tk.StringVar(value=label_config.font_name)
        font_entry = tk.Entry(font_frame, textvariable=self.pptx_vars['font_name'], width=12)
        font_entry.pack(side="left", padx=(5, 0))

        tk.Label(font_frame, text="サイズ:", font=("Arial", 9)).pack(side="left", padx=(10, 0))
        self.pptx_vars['font_size'] = tk.StringVar(value=str(label_config.font_size))
        font_size_entry = tk.Entry(font_frame, textvariable=self.pptx_vars['font_size'], width=4)
        font_size_entry.pack(side="left", padx=(5, 0))

        # Position setting
        position_frame = tk.Frame(parent_frame)
        position_frame.pack(fill="x", padx=5, pady=2)

        tk.Label(position_frame, text="ラベル位置:", font=("Arial", 9)).pack(side="left")
        self.pptx_vars['position'] = tk.StringVar(value=label_config.position)
        position_combo = ttk.Combobox(
            position_frame,
            textvariable=self.pptx_vars['position'],
            values=["top-left", "top-right", "bottom-left", "bottom-right"],
            state="readonly",
            width=12
        )
        position_combo.pack(side="left", padx=(5, 0))

        # Save button
        save_button = tk.Button(
            parent_frame,
            text="💾 設定を保存",
            command=self._save_powerpoint_settings,
            font=("Arial", 9)
        )
        save_button.pack(pady=5)

    def _save_powerpoint_settings(self) -> None:
        """Save PowerPoint label configuration."""
        try:
            # Get current configuration
            config = get_app_config()

            # Update PowerPoint label settings
            config.powerpoint_label.text_color = self.pptx_vars['text_color'].get()
            config.powerpoint_label.background_color = self.pptx_vars['background_color'].get()
            config.powerpoint_label.border_color = self.pptx_vars['border_color'].get()
            config.powerpoint_label.font_name = self.pptx_vars['font_name'].get()
            config.powerpoint_label.font_size = int(self.pptx_vars['font_size'].get())
            config.powerpoint_label.position = self.pptx_vars['position'].get()

            # Validate and save configuration
            config.powerpoint_label.validate()
            save_app_config(config)

            messagebox.showinfo("設定保存", "PowerPointラベル設定が保存されました。")

        except ValueError as e:
            if "invalid literal for int()" in str(e):
                messagebox.showerror("設定エラー", "フォントサイズは数値で入力してください。")
            else:
                messagebox.showerror("設定エラー", f"設定の保存に失敗しました: {e}")
        except UserFriendlyError as e:
            messagebox.showerror("設定エラー", str(e))
        except Exception as e:
            messagebox.showerror("設定エラー", f"予期しないエラーが発生しました: {e}")

    def _create_menu_bar(self) -> None:
        """Create the application menu bar with interface options."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # View menu for interface options
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="表示", menu=view_menu)

        # Interface submenu
        interface_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="インターフェース", menu=interface_menu)

        self.theme_var = tk.StringVar(value=self.theme_manager.current_theme.value)

        for theme_mode, display_name in self.theme_manager.get_available_themes().items():
            interface_menu.add_radiobutton(
                label=display_name,
                variable=self.theme_var,
                value=theme_mode.value,
                command=lambda mode=theme_mode: self._change_theme(mode)
            )

        # Add separator and toggle option
        interface_menu.add_separator()
        interface_menu.add_command(
            label="スタイル切り替え (Ctrl+T)",
            command=self._toggle_theme,
            accelerator="Ctrl+T"
        )

        # Bind keyboard shortcut
        self.root.bind('<Control-t>', lambda e: self._toggle_theme())
        self.root.bind('<Control-T>', lambda e: self._toggle_theme())

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ヘルプ", menu=help_menu)
        help_menu.add_command(label="PDF2PPTX について", command=self._show_about)

    def _change_theme(self, theme_mode: ThemeMode) -> None:
        """Change the application theme."""
        self.theme_manager.set_theme(theme_mode)
        self.theme_var.set(theme_mode.value)

    def _toggle_theme(self) -> None:
        """Toggle between light and deep blue themes."""
        self.theme_manager.toggle_theme()
        self.theme_var.set(self.theme_manager.current_theme.value)

    def _setup_theme_support(self) -> None:
        """Setup theme change callback and initial styling."""
        self.theme_manager.register_theme_callback(
            "main_window",
            self._on_theme_changed
        )

    def _on_theme_changed(self, theme: ThemeStyle) -> None:
        """Called when theme changes to update all UI elements."""
        self._apply_current_theme()

    def _apply_current_theme(self) -> None:
        """Apply the current theme to all UI elements."""
        theme = self.theme_manager.get_current_theme()

        # Apply to root window
        self.root.configure(bg=theme.colors.bg_primary)

        # Update all themed widgets
        self._update_widget_themes(self.root, theme)

    def _update_widget_themes(self, parent: tk.Widget, theme: ThemeStyle) -> None:
        """Recursively update themes for all child widgets."""
        for child in parent.winfo_children():
            self.theme_manager.apply_theme_to_widget(child)
            if hasattr(child, 'winfo_children'):
                self._update_widget_themes(child, theme)

    def _show_about(self) -> None:
        """Show about dialog."""
        about_text = (
            "PDF2PPTX Converter v3.0\n\n"
            "PDFファイルをPNG画像やPowerPointプレゼンテーションに\n"
            "変換するアプリケーションです。\n\n"
            "主な機能:\n"
            "• PDF → PNG変換 (スケール調整可能)\n"
            "• PDF → PPTX変換 (A3横向きレイアウト)\n"
            "• 自動回転機能\n"
            "• 深い青色のモダンインターフェース\n"
            "• 設定の永続化\n\n"
            "© 2025 PDF2PPTX Project"
        )
        messagebox.showinfo("PDF2PPTX について", about_text)

    def _show_error(self, error: UserFriendlyError) -> None:
        """Display error message to user."""
        if error.severity == ErrorSeverity.WARNING:
            messagebox.showwarning("警告", str(error))
        else:
            messagebox.showerror("エラー", str(error))

    def run(self) -> None:
        """Start the application main loop."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            self.root.destroy()
        except Exception as e:
            self.logger.error(f"Application crashed: {e}", exc_info=True)
            messagebox.showerror(
                "アプリケーションエラー",
                f"アプリケーションでエラーが発生しました:\n\n{format_exception_for_user(e)}"
            )


def main() -> None:
    """Application entry point."""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()