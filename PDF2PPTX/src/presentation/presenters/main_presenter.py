"""
Main presenter for the PDF2PNG/PDF2PPTX application.

Implements the MVP (Model-View-Presenter) pattern to handle UI logic
and coordinate between the view and application services.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import List, Optional, Protocol, Callable
from dataclasses import dataclass

from ...application.services.conversion_service import ConversionService, ConversionJob, ConversionStatus
from ...core.pdf_processor import ConversionConfig
from ...config import get_app_config, save_app_config, ApplicationConfig
from ...utils.error_handling import UserFriendlyError, setup_logging
from ...utils.path_utils import PathManager


class MainViewInterface(Protocol):
    """Interface that the main view must implement."""

    def show_progress(self, percentage: int, message: str, current_file: str = None) -> None:
        """Show conversion progress."""
        ...

    def show_error(self, error_message: str, suggestion: str = None) -> None:
        """Show error message to user."""
        ...

    def show_success(self, message: str, details: str = None) -> None:
        """Show success message to user."""
        ...

    def show_warning(self, message: str, suggestion: str = None) -> None:
        """Show warning message to user."""
        ...

    def update_file_list(self, files: List[FileInfo]) -> None:
        """Update the file list display."""
        ...

    def update_conversion_settings(self, config: ConversionConfig) -> None:
        """Update conversion settings display."""
        ...

    def set_ui_enabled(self, enabled: bool) -> None:
        """Enable or disable UI controls."""
        ...

    def ask_confirmation(self, message: str, title: str = "確認") -> bool:
        """Ask user for confirmation."""
        ...

    def open_output_folder(self, folder_path: Path) -> None:
        """Open the output folder in file explorer."""
        ...


@dataclass
class FileInfo:
    """Information about a file for display."""
    path: Path
    name: str
    size: int
    page_count: Optional[int] = None
    is_valid: bool = True
    error_message: Optional[str] = None


class MainPresenter:
    """
    Main presenter managing the application's core functionality.

    This presenter:
    - Handles user interactions from the view
    - Coordinates with application services
    - Manages application state
    - Provides data for the view to display
    """

    def __init__(self, view: MainViewInterface, conversion_service: ConversionService):
        self.view = view
        self.conversion_service = conversion_service
        self.path_manager = PathManager()
        self.logger = setup_logging()

        self.selected_files: List[Path] = []
        self.current_config = ConversionConfig()
        self.current_job: Optional[ConversionJob] = None

        # Load application configuration
        self.app_config = get_app_config()

    async def initialize(self) -> None:
        """Initialize the presenter and view."""
        try:
            # Validate environment
            self.path_manager.validate_working_directory()

            # Update view with current configuration
            self.view.update_conversion_settings(self.current_config)

            self.logger.info("Application initialized successfully")

        except Exception as e:
            self.logger.error(f"Initialization failed: {e}", exc_info=True)
            self.view.show_error(
                "アプリケーションの初期化に失敗しました",
                f"詳細: {str(e)}"
            )

    def handle_files_selected(self, file_paths: List[Path]) -> None:
        """Handle file selection from the view."""
        try:
            self.selected_files = file_paths
            file_infos = []

            for file_path in file_paths:
                file_info = self._analyze_file(file_path)
                file_infos.append(file_info)

            self.view.update_file_list(file_infos)
            self.logger.info(f"Selected {len(file_paths)} files")

        except Exception as e:
            self.logger.error(f"Error handling file selection: {e}", exc_info=True)
            self.view.show_error("ファイル選択の処理中にエラーが発生しました", str(e))

    def _analyze_file(self, file_path: Path) -> FileInfo:
        """Analyze a file and return file information."""
        try:
            file_info = FileInfo(
                path=file_path,
                name=file_path.name,
                size=file_path.stat().st_size
            )

            # Check if it's a valid PDF
            if file_path.suffix.lower() != '.pdf':
                file_info.is_valid = False
                file_info.error_message = "PDFファイルではありません"
                return file_info

            # Try to get page count
            try:
                page_count = self.conversion_service.pdf_processor.count_pages(file_path)
                file_info.page_count = page_count
            except Exception as e:
                file_info.is_valid = False
                file_info.error_message = f"PDFファイルの読み込みに失敗: {str(e)}"

            return file_info

        except Exception as e:
            return FileInfo(
                path=file_path,
                name=file_path.name,
                size=0,
                is_valid=False,
                error_message=f"ファイル分析エラー: {str(e)}"
            )

    async def handle_convert_to_images(self) -> None:
        """Handle PNG conversion request."""
        await self._handle_conversion("png")

    async def handle_convert_to_pptx(self) -> None:
        """Handle PPTX conversion request."""
        await self._handle_conversion("pptx")

    async def _handle_conversion(self, output_type: str) -> None:
        """Handle conversion process."""
        try:
            # Validate request
            error_message = self.conversion_service.validate_conversion_request(
                self.selected_files, self.current_config
            )
            if error_message:
                self.view.show_error(error_message)
                return

            # Estimate conversion time
            estimated_time = self.conversion_service.estimate_conversion_time(
                self.selected_files, self.current_config
            )

            # Ask for confirmation if conversion will take long
            if estimated_time > 60:  # More than 1 minute
                minutes = int(estimated_time / 60)
                confirmation_message = f"変換には約{minutes}分かかる見込みです。続行しますか？"
                if not self.view.ask_confirmation(confirmation_message):
                    return

            # Disable UI during conversion
            self.view.set_ui_enabled(False)

            # Start conversion
            if output_type == "png":
                job = await self.conversion_service.convert_to_images_async(
                    self.selected_files,
                    self.current_config,
                    self._on_conversion_progress
                )
            else:  # pptx
                job = await self.conversion_service.convert_to_pptx_async(
                    self.selected_files,
                    self.current_config,
                    self._on_conversion_progress
                )

            self.current_job = job

            # Handle completion
            if job.status == ConversionStatus.COMPLETED:
                await self._handle_conversion_success(job, output_type)
            elif job.status == ConversionStatus.FAILED:
                self._handle_conversion_error(job)
            elif job.status == ConversionStatus.CANCELLED:
                self.view.show_warning("変換がキャンセルされました")

        except Exception as e:
            self.logger.error(f"Conversion error: {e}", exc_info=True)
            self.view.show_error("変換中に予期しないエラーが発生しました", str(e))

        finally:
            # Re-enable UI
            self.view.set_ui_enabled(True)
            self.current_job = None

    def _on_conversion_progress(self, job: ConversionJob) -> None:
        """Handle conversion progress updates."""
        if job.status == ConversionStatus.RUNNING:
            message = f"変換中... ({job.progress}%)"
            current_file = job.current_file or ""
            self.view.show_progress(job.progress, message, current_file)

    async def _handle_conversion_success(self, job: ConversionJob, output_type: str) -> None:
        """Handle successful conversion."""
        file_count = len(job.result_files)

        if output_type == "png":
            message = f"PNG変換が完了しました"
            details = f"{file_count}個のファイルが生成されました"
        else:
            message = f"PowerPoint変換が完了しました"
            details = f"ファイルが生成されました: {job.result_files[0].name if job.result_files else ''}"

        self.view.show_success(message, details)

        # Ask if user wants to open output folder
        if self.view.ask_confirmation("出力フォルダを開きますか？"):
            output_folder = self.path_manager.output_dir
            self.view.open_output_folder(output_folder)

        self.logger.info(f"Conversion completed successfully: {file_count} files generated")

    def _handle_conversion_error(self, job: ConversionJob) -> None:
        """Handle conversion error."""
        error_message = job.error_message or "不明なエラーが発生しました"
        self.view.show_error("変換に失敗しました", error_message)
        self.logger.error(f"Conversion failed: {error_message}")

    def handle_cancel_conversion(self) -> None:
        """Handle conversion cancellation request."""
        if self.current_job and self.current_job.status == ConversionStatus.RUNNING:
            success = self.conversion_service.cancel_job(self.current_job.id)
            if success:
                self.view.show_warning("変換をキャンセルしています...")
                self.logger.info("Conversion cancellation requested")

    def handle_configuration_changed(self, config: ConversionConfig) -> None:
        """Handle configuration changes from the view."""
        self.current_config = config
        self.logger.info("Configuration updated")

    def handle_reset_folders(self) -> None:
        """Handle folder reset request."""
        try:
            if self.view.ask_confirmation(
                "Input/Outputフォルダの内容をすべて削除しますか？\n" +
                "この操作は元に戻せません。",
                "フォルダ初期化の確認"
            ):
                self.path_manager.reset_directories()
                self.view.show_success("フォルダが初期化されました")
                self.logger.info("Folders reset successfully")

        except Exception as e:
            self.logger.error(f"Folder reset failed: {e}", exc_info=True)
            self.view.show_error("フォルダ初期化に失敗しました", str(e))

    def handle_settings_save(self, app_config: ApplicationConfig) -> None:
        """Handle application settings save."""
        try:
            save_app_config(app_config)
            self.app_config = app_config
            self.view.show_success("設定が保存されました")
            self.logger.info("Application settings saved")

        except Exception as e:
            self.logger.error(f"Settings save failed: {e}", exc_info=True)
            self.view.show_error("設定の保存に失敗しました", str(e))

    def get_conversion_presets(self) -> dict:
        """Get available conversion presets."""
        from ...config import ConversionPresets
        return {
            "高品質": ConversionPresets.high_quality(),
            "標準": ConversionPresets.balanced(),
            "高速": ConversionPresets.fast(),
            "プレゼン": ConversionPresets.presentation()
        }

    def apply_preset(self, preset_name: str) -> None:
        """Apply a conversion preset."""
        try:
            presets = self.get_conversion_presets()
            if preset_name in presets:
                preset_config = presets[preset_name]

                # Update current config with preset values
                self.current_config.scale_factor = preset_config.get("scale_factor", self.current_config.scale_factor)
                self.current_config.target_dpi = preset_config.get("target_dpi", self.current_config.target_dpi)
                self.current_config.auto_rotate = preset_config.get("auto_rotate", self.current_config.auto_rotate)

                # Update view
                self.view.update_conversion_settings(self.current_config)

                self.logger.info(f"Applied preset: {preset_name}")

        except Exception as e:
            self.logger.error(f"Error applying preset {preset_name}: {e}", exc_info=True)
            self.view.show_error("プリセットの適用に失敗しました", str(e))

    def get_selected_files_info(self) -> List[FileInfo]:
        """Get information about currently selected files."""
        return [self._analyze_file(file_path) for file_path in self.selected_files]

    def cleanup(self) -> None:
        """Clean up resources when shutting down."""
        try:
            # Cancel any running conversion
            if self.current_job and self.current_job.status == ConversionStatus.RUNNING:
                self.conversion_service.cancel_job(self.current_job.id)

            # Clean up completed jobs
            self.conversion_service.cleanup_completed_jobs()

            self.logger.info("Presenter cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}", exc_info=True)