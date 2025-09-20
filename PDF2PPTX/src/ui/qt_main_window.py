"""
PySide6-based main GUI application for PDF2PNG/PDF2PPTX converter.
Modern Qt interface without TCL dependencies.
"""

from __future__ import annotations

import sys
import asyncio
from pathlib import Path
from typing import Optional, Callable

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QPushButton, QLabel, QLineEdit, QCheckBox,
    QProgressBar, QMessageBox, QGroupBox, QComboBox, QMenuBar,
    QStatusBar, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QAction

from ..core.pdf_processor import ConversionConfig
from ..utils.error_handling import (
    UserFriendlyError,
    ErrorSeverity,
    format_exception_for_user,
    setup_logging
)
from ..utils.path_utils import PathManager
from ..config import get_app_config, save_app_config
from ..application.services.conversion_service import ConversionService


class ConversionWorker(QThread):
    """Background thread for PDF conversion operations."""

    progress_updated = Signal(int, str)  # progress percentage, status message
    conversion_completed = Signal(bool, str, list)  # success, message, result_files

    def __init__(self, service: ConversionService, config: ConversionConfig, conversion_type: str):
        super().__init__()
        self.service = service
        self.config = config
        self.conversion_type = conversion_type  # "png" or "pptx"
        self.is_cancelled = False

    def run(self):
        """Execute conversion in background thread."""
        try:
            if self.conversion_type == "png":
                result_files = self.service.convert_to_images(self.config)
                if result_files:
                    self.conversion_completed.emit(
                        True,
                        f"PNG変換完了: {len(result_files)}個のファイルが生成されました",
                        result_files
                    )
                else:
                    self.conversion_completed.emit(False, "変換するPDFファイルが見つかりませんでした", [])

            elif self.conversion_type == "pptx":
                result_file = self.service.convert_to_powerpoint(self.config)
                if result_file:
                    self.conversion_completed.emit(
                        True,
                        "PowerPoint変換完了",
                        [result_file]
                    )
                else:
                    self.conversion_completed.emit(False, "変換するPDFファイルが見つかりませんでした", [])

        except UserFriendlyError as e:
            self.conversion_completed.emit(False, str(e), [])
        except Exception as e:
            error_msg = f"変換中にエラーが発生しました: {format_exception_for_user(e)}"
            self.conversion_completed.emit(False, error_msg, [])

    def cancel(self):
        """Cancel the conversion operation."""
        self.is_cancelled = True
        self.terminate()


class QtMainWindow(QMainWindow):
    """Main application window using PySide6."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF2PPTX Converter v3.0 (Qt Edition)")
        self.setMinimumSize(600, 450)
        self.resize(650, 500)

        # Initialize components
        self.path_manager = PathManager()
        self.conversion_service = ConversionService(self.path_manager)
        self.conversion_worker: Optional[ConversionWorker] = None

        # Setup logging
        log_file = self.path_manager.base_path / "logs" / "qt_conversion.log"
        self.logger = setup_logging(log_file)

        # Create UI
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_status_bar()

        # Validate environment
        self._validate_environment()

    def _setup_ui(self):
        """Create and setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Configuration group
        config_group = QGroupBox("変換設定")
        config_group.setFont(QFont("Yu Gothic UI", 10))
        config_layout = QGridLayout(config_group)

        # Scale factor
        config_layout.addWidget(QLabel("スケール倍率:"), 0, 0)
        self.scale_edit = QLineEdit("1.5")
        self.scale_edit.setMaximumWidth(80)
        config_layout.addWidget(self.scale_edit, 0, 1)
        config_layout.addWidget(QLabel("(推奨: 1.0-3.0)"), 0, 2)

        # Auto rotation
        self.auto_rotate_check = QCheckBox("縦長ページを横向きに自動回転")
        self.auto_rotate_check.setChecked(True)
        config_layout.addWidget(self.auto_rotate_check, 1, 0, 1, 3)

        main_layout.addWidget(config_group)

        # PowerPoint settings group
        pptx_group = QGroupBox("PowerPoint ラベル設定")
        pptx_group.setFont(QFont("Yu Gothic UI", 10))
        pptx_layout = QGridLayout(pptx_group)

        self._setup_powerpoint_settings(pptx_layout)
        main_layout.addWidget(pptx_group)

        # Action buttons
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(8)

        # PNG conversion button
        self.btn_png = QPushButton("🖼️ PDF → PNG 変換")
        self.btn_png.setMinimumHeight(40)
        self.btn_png.setFont(QFont("Yu Gothic UI", 10))
        self.btn_png.clicked.connect(self._convert_to_png)
        buttons_layout.addWidget(self.btn_png)

        # PPTX conversion button
        self.btn_pptx = QPushButton("📊 PDF → PPTX 変換 (A3横)")
        self.btn_pptx.setMinimumHeight(40)
        self.btn_pptx.setFont(QFont("Yu Gothic UI", 10))
        self.btn_pptx.clicked.connect(self._convert_to_pptx)
        buttons_layout.addWidget(self.btn_pptx)

        # Reset button
        self.btn_reset = QPushButton("🗂️ Input/Output フォルダ初期化")
        self.btn_reset.setMinimumHeight(40)
        self.btn_reset.setFont(QFont("Yu Gothic UI", 10))
        self.btn_reset.clicked.connect(self._reset_folders)
        buttons_layout.addWidget(self.btn_reset)

        main_layout.addLayout(buttons_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel(f"作業ディレクトリ: {self.path_manager.get_relative_path(self.path_manager.base_path)}")
        self.status_label.setFont(QFont("Yu Gothic UI", 8))
        self.status_label.setStyleSheet("color: gray;")
        main_layout.addWidget(self.status_label)

    def _setup_powerpoint_settings(self, layout: QGridLayout):
        """Setup PowerPoint configuration UI."""
        config = get_app_config()
        label_config = config.powerpoint_label

        # Store settings widgets
        self.pptx_widgets = {}

        # Text color
        layout.addWidget(QLabel("文字色:"), 0, 0)
        self.pptx_widgets['text_color'] = QLineEdit(label_config.text_color)
        self.pptx_widgets['text_color'].setMaximumWidth(80)
        layout.addWidget(self.pptx_widgets['text_color'], 0, 1)

        # Background color
        layout.addWidget(QLabel("背景色:"), 0, 2)
        self.pptx_widgets['background_color'] = QLineEdit(label_config.background_color)
        self.pptx_widgets['background_color'].setMaximumWidth(80)
        layout.addWidget(self.pptx_widgets['background_color'], 0, 3)

        # Border color
        layout.addWidget(QLabel("枠線色:"), 1, 0)
        self.pptx_widgets['border_color'] = QLineEdit("#FF0000")
        self.pptx_widgets['border_color'].setMaximumWidth(80)
        layout.addWidget(self.pptx_widgets['border_color'], 1, 1)

        # Font name
        layout.addWidget(QLabel("フォント:"), 1, 2)
        self.pptx_widgets['font_name'] = QLineEdit(label_config.font_name)
        self.pptx_widgets['font_name'].setMaximumWidth(100)
        layout.addWidget(self.pptx_widgets['font_name'], 1, 3)

        # Font size
        layout.addWidget(QLabel("サイズ:"), 2, 0)
        self.pptx_widgets['font_size'] = QLineEdit(str(label_config.font_size))
        self.pptx_widgets['font_size'].setMaximumWidth(50)
        layout.addWidget(self.pptx_widgets['font_size'], 2, 1)

        # Position
        layout.addWidget(QLabel("位置:"), 2, 2)
        self.pptx_widgets['position'] = QComboBox()
        self.pptx_widgets['position'].addItems([
            "top-left", "top-right", "bottom-left", "bottom-right"
        ])
        self.pptx_widgets['position'].setCurrentText(label_config.position)
        layout.addWidget(self.pptx_widgets['position'], 2, 3)

        # Save button
        save_btn = QPushButton("💾 設定を保存")
        save_btn.clicked.connect(self._save_powerpoint_settings)
        layout.addWidget(save_btn, 3, 0, 1, 4)

    def _setup_menu_bar(self):
        """Setup application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("ファイル(&F)")

        exit_action = QAction("終了(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("ヘルプ(&H)")

        about_action = QAction("PDF2PPTX について(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_status_bar(self):
        """Setup status bar."""
        self.statusBar().showMessage("準備完了")

    def _validate_environment(self):
        """Validate application environment."""
        try:
            self.path_manager.validate_working_directory()
        except Exception as e:
            QMessageBox.critical(
                self,
                "初期化エラー",
                f"アプリケーションの初期化に失敗しました:\n\n{format_exception_for_user(e)}"
            )

    def _get_conversion_config(self) -> ConversionConfig:
        """Get conversion configuration from UI inputs."""
        try:
            scale_factor = float(self.scale_edit.text())
        except ValueError:
            raise UserFriendlyError(
                message="スケール倍率は数値で入力してください",
                suggestion="例: 1.5 または 2.0"
            )

        return ConversionConfig(
            scale_factor=scale_factor,
            auto_rotate=self.auto_rotate_check.isChecked()
        )

    def _convert_to_png(self):
        """Handle PNG conversion."""
        try:
            config = self._get_conversion_config()
            self._start_conversion(config, "png")
        except UserFriendlyError as e:
            self._show_error(str(e))

    def _convert_to_pptx(self):
        """Handle PPTX conversion."""
        try:
            config = self._get_conversion_config()
            self._start_conversion(config, "pptx")
        except UserFriendlyError as e:
            self._show_error(str(e))

    def _start_conversion(self, config: ConversionConfig, conversion_type: str):
        """Start conversion in background thread."""
        if self.conversion_worker and self.conversion_worker.isRunning():
            QMessageBox.warning(self, "警告", "変換が実行中です。完了してから再度お試しください。")
            return

        # Disable buttons and show progress
        self._set_buttons_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.statusBar().showMessage(f"{'PNG' if conversion_type == 'png' else 'PPTX'}変換中...")

        # Start conversion worker
        self.conversion_worker = ConversionWorker(self.conversion_service, config, conversion_type)
        self.conversion_worker.conversion_completed.connect(self._on_conversion_completed)
        self.conversion_worker.start()

    def _on_conversion_completed(self, success: bool, message: str, result_files: list):
        """Handle conversion completion."""
        # Hide progress and re-enable buttons
        self.progress_bar.setVisible(False)
        self._set_buttons_enabled(True)
        self.statusBar().showMessage("準備完了")

        if success:
            QMessageBox.information(self, "変換完了", message)
            if result_files:
                # Try to open output directory
                import webbrowser
                try:
                    webbrowser.open(str(result_files[0].parent))
                except Exception:
                    pass
        else:
            self._show_error(message)

    def _reset_folders(self):
        """Reset input and output folders."""
        reply = QMessageBox.question(
            self,
            "確認",
            "Input/Outputフォルダの全ファイルが削除されます。\n\n続行しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                total_deleted = self.conversion_service.reset_folders()
                QMessageBox.information(
                    self,
                    "フォルダ初期化完了",
                    f"Input/Outputフォルダを初期化しました。\n削除されたアイテム数: {total_deleted}"
                )
            except Exception as e:
                self._show_error(f"フォルダの初期化に失敗しました: {e}")

    def _save_powerpoint_settings(self):
        """Save PowerPoint label configuration."""
        try:
            config = get_app_config()

            # Update settings from UI
            config.powerpoint_label.text_color = self.pptx_widgets['text_color'].text()
            config.powerpoint_label.background_color = self.pptx_widgets['background_color'].text()
            config.powerpoint_label.border_color = self.pptx_widgets['border_color'].text()
            config.powerpoint_label.font_name = self.pptx_widgets['font_name'].text()
            config.powerpoint_label.font_size = int(self.pptx_widgets['font_size'].text())
            config.powerpoint_label.position = self.pptx_widgets['position'].currentText()

            # Validate and save
            config.powerpoint_label.validate()
            save_app_config(config)

            QMessageBox.information(self, "設定保存", "PowerPointラベル設定が保存されました。")

        except ValueError as e:
            if "invalid literal for int()" in str(e):
                self._show_error("フォントサイズは数値で入力してください。")
            else:
                self._show_error(f"設定の保存に失敗しました: {e}")
        except UserFriendlyError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(f"予期しないエラーが発生しました: {e}")

    def _show_about(self):
        """Show about dialog."""
        about_text = (
            "PDF2PPTX Converter v3.0 (Qt Edition)\n\n"
            "PDFファイルをPNG画像やPowerPointプレゼンテーションに\n"
            "変換するアプリケーションです。\n\n"
            "主な機能:\n"
            "• PDF → PNG変換 (スケール調整可能)\n"
            "• PDF → PPTX変換 (A3横向きレイアウト)\n"
            "• 自動回転機能\n"
            "• モダンなQtインターフェース\n"
            "• TCL/Tkinter非依存\n"
            "• 設定の永続化\n\n"
            "© 2025 PDF2PPTX Project"
        )
        QMessageBox.about(self, "PDF2PPTX について", about_text)

    def _show_error(self, message: str):
        """Show error message."""
        QMessageBox.critical(self, "エラー", message)

    def _set_buttons_enabled(self, enabled: bool):
        """Enable or disable operation buttons."""
        self.btn_png.setEnabled(enabled)
        self.btn_pptx.setEnabled(enabled)
        self.btn_reset.setEnabled(enabled)

    def closeEvent(self, event):
        """Handle application close event."""
        if self.conversion_worker and self.conversion_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "確認",
                "変換処理が実行中です。アプリケーションを終了しますか？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.conversion_worker.cancel()
                self.conversion_worker.wait(3000)  # Wait up to 3 seconds
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Qt application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("PDF2PPTX Converter")
    app.setApplicationVersion("3.0.0")
    app.setOrganizationName("PDF2PPTX Project")

    # Set application style
    app.setStyle('Fusion')  # Modern cross-platform style

    window = QtMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()