"""
変換サービス統合
PDF処理とPowerPoint生成を統合し、バッチ変換、進捗管理、キャンセル機能を提供
"""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import time
from loguru import logger

from .pdf_processor import PDFProcessor, ConversionSettings as PDFSettings, RotationMode, ImageFormat
from .pptx_generator import PPTXGenerator, SlideSettings, LabelStyle, ImageSettings, SlideSize, LabelPosition
from ..utils.config import ConfigManager
from ..utils.error_handler import ErrorHandler, ErrorType
from ..utils.file_utils import FileUtils, FileValidator, DirectoryManager


class ConversionType(Enum):
    """変換タイプ"""
    PDF_TO_PNG = "pdf_to_png"
    PDF_TO_PPTX = "pdf_to_pptx"
    IMAGES_TO_PPTX = "images_to_pptx"


class ConversionStatus(Enum):
    """変換ステータス"""
    PENDING = "pending"
    PREPARING = "preparing"
    PROCESSING = "processing"
    COMPLETING = "completing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ConversionProgress:
    """変換進捗情報"""
    current_file: int = 0
    total_files: int = 0
    current_page: int = 0
    total_pages: int = 0
    status: ConversionStatus = ConversionStatus.PENDING
    status_message: str = ""
    start_time: Optional[datetime] = None
    estimated_end_time: Optional[datetime] = None
    elapsed_seconds: float = 0.0
    remaining_seconds: float = 0.0
    current_filename: str = ""
    error_message: str = ""


@dataclass
class ConversionResult:
    """変換結果"""
    success: bool = False
    conversion_type: ConversionType = ConversionType.PDF_TO_PNG
    input_files: List[Path] = field(default_factory=list)
    output_files: List[Path] = field(default_factory=list)
    output_directory: Optional[Path] = None
    total_pages_processed: int = 0
    processing_time_seconds: float = 0.0
    file_size_mb: float = 0.0
    error_message: str = ""
    warnings: List[str] = field(default_factory=list)


class ConversionService:
    """変換サービス統合クラス"""

    def __init__(self,
                 config_manager: Optional[ConfigManager] = None,
                 error_handler: Optional[ErrorHandler] = None,
                 file_utils: Optional[FileUtils] = None):
        """
        初期化

        Args:
            config_manager: 設定管理インスタンス
            error_handler: エラーハンドラーインスタンス
            file_utils: ファイルユーティリティインスタンス
        """
        self.config_manager = config_manager or ConfigManager()
        self.error_handler = error_handler or ErrorHandler()
        self.file_utils = file_utils or FileUtils(self.error_handler)

        # PDF処理エンジン
        self.pdf_processor = PDFProcessor(self.config_manager, self.error_handler)

        # PowerPoint生成エンジン
        self.pptx_generator = PPTXGenerator(self.config_manager, self.error_handler)

        # 変換状態管理
        self._is_cancelled = False
        self._current_conversion = None
        self._conversion_lock = threading.Lock()

        # 進捗コールバック
        self.progress_callback: Optional[Callable[[ConversionProgress], None]] = None

        # パフォーマンス設定
        self.max_workers = min(4, self.config_manager.get_config("performance.max_concurrent_conversions") or 3)

        logger.info("変換サービスを初期化しました")

    def set_progress_callback(self, callback: Callable[[ConversionProgress], None]) -> None:
        """
        進捗コールバック関数を設定

        Args:
            callback: 進捗通知用コールバック関数
        """
        self.progress_callback = callback
        logger.debug("進捗コールバックを設定しました")

    def cancel_conversion(self) -> None:
        """現在の変換処理をキャンセル"""
        with self._conversion_lock:
            self._is_cancelled = True
            logger.info("変換処理のキャンセルが要求されました")

    def is_conversion_cancelled(self) -> bool:
        """変換がキャンセルされているかチェック"""
        return self._is_cancelled

    def _update_progress(self, progress: ConversionProgress) -> None:
        """
        進捗情報を更新

        Args:
            progress: 進捗情報
        """
        try:
            # 経過時間計算
            if progress.start_time:
                progress.elapsed_seconds = (datetime.now() - progress.start_time).total_seconds()

                # 残り時間推定
                if progress.total_files > 0 and progress.current_file > 0:
                    completion_ratio = progress.current_file / progress.total_files
                    if completion_ratio > 0:
                        estimated_total_time = progress.elapsed_seconds / completion_ratio
                        progress.remaining_seconds = max(0, estimated_total_time - progress.elapsed_seconds)
                        progress.estimated_end_time = datetime.now().timestamp() + progress.remaining_seconds

            # コールバック呼び出し
            if self.progress_callback:
                self.progress_callback(progress)

        except Exception as e:
            logger.warning(f"進捗更新エラー: {e}")

    def convert_pdf_to_images(self,
                            pdf_path: Path,
                            output_dir: Path,
                            pdf_settings: Optional[PDFSettings] = None,
                            page_range: Optional[Tuple[int, int]] = None) -> ConversionResult:
        """
        PDFファイルを画像ファイルに変換

        Args:
            pdf_path: PDFファイルパス
            output_dir: 出力ディレクトリ
            pdf_settings: PDF変換設定
            page_range: ページ範囲 (start, end)

        Returns:
            変換結果

        Raises:
            FileNotFoundError: 入力ファイルが存在しない
            ValueError: 無効な設定
            RuntimeError: 変換エラー
        """
        start_time = datetime.now()
        progress = ConversionProgress(
            total_files=1,
            status=ConversionStatus.PREPARING,
            status_message="PDF変換を準備中...",
            start_time=start_time,
            current_filename=pdf_path.name
        )

        try:
            # キャンセルフラグをリセット
            with self._conversion_lock:
                self._is_cancelled = False

            self._update_progress(progress)

            # ファイル検証
            if not FileValidator.validate_pdf_file(pdf_path):
                raise ValueError(f"無効なPDFファイル: {pdf_path}")

            # 出力ディレクトリ作成
            output_directory = DirectoryManager.create_output_directory(
                output_dir, pdf_path,
                self.config_manager.get_config("conversion.output.create_subfolder"),
                self.config_manager.get_config("conversion.output.subfolder_prefix")
            )

            # PDF情報取得
            pdf_info = self.pdf_processor.get_pdf_info(pdf_path)
            total_pages = pdf_info["page_count"]

            # ページ範囲設定
            if page_range:
                start_page, end_page = page_range
                total_pages = end_page - start_page + 1
            else:
                start_page, end_page = 1, total_pages

            progress.total_pages = total_pages
            progress.status = ConversionStatus.PROCESSING
            progress.status_message = f"PDF変換中... (1/{total_pages} ページ)"
            self._update_progress(progress)

            # 変換実行
            output_files = []

            for page_num in range(start_page, end_page + 1):
                # キャンセルチェック
                if self.is_conversion_cancelled():
                    progress.status = ConversionStatus.CANCELLED
                    progress.status_message = "変換がキャンセルされました"
                    self._update_progress(progress)
                    raise RuntimeError("変換がキャンセルされました")

                try:
                    # ページを画像に変換
                    image = self.pdf_processor.convert_page_to_image(
                        pdf_path, page_num, pdf_settings
                    )

                    # ファイル名生成
                    filename = f"{pdf_path.stem}_page_{page_num:03d}.{pdf_settings.output_format.value if pdf_settings else 'png'}"
                    output_path = output_directory / filename

                    # 画像保存
                    image.save(output_path)
                    output_files.append(output_path)

                    # 進捗更新
                    progress.current_page = page_num - start_page + 1
                    progress.status_message = f"PDF変換中... ({progress.current_page}/{total_pages} ページ)"
                    self._update_progress(progress)

                except Exception as e:
                    logger.error(f"ページ {page_num} の変換に失敗: {e}")
                    continue

            # 完了処理
            progress.status = ConversionStatus.COMPLETED
            progress.status_message = "PDF変換が完了しました"
            progress.current_file = 1
            self._update_progress(progress)

            # 結果作成
            processing_time = (datetime.now() - start_time).total_seconds()
            total_size = sum(f.stat().st_size for f in output_files if f.exists())

            result = ConversionResult(
                success=True,
                conversion_type=ConversionType.PDF_TO_PNG,
                input_files=[pdf_path],
                output_files=output_files,
                output_directory=output_directory,
                total_pages_processed=len(output_files),
                processing_time_seconds=processing_time,
                file_size_mb=total_size / (1024 * 1024)
            )

            logger.info(f"PDF→画像変換完了: {len(output_files)} ページ, {processing_time:.1f}秒")
            return result

        except Exception as e:
            progress.status = ConversionStatus.FAILED
            progress.error_message = str(e)
            progress.status_message = f"変換エラー: {str(e)[:100]}"
            self._update_progress(progress)

            self.error_handler.handle_error(
                error_type=ErrorType.CONVERSION_ERROR,
                error=e,
                details={"file": str(pdf_path)}
            )

            return ConversionResult(
                success=False,
                conversion_type=ConversionType.PDF_TO_PNG,
                input_files=[pdf_path],
                error_message=str(e),
                processing_time_seconds=(datetime.now() - start_time).total_seconds()
            )

    def convert_pdf_to_pptx(self,
                          pdf_path: Path,
                          output_path: Path,
                          pdf_settings: Optional[PDFSettings] = None,
                          slide_settings: Optional[SlideSettings] = None,
                          label_style: Optional[LabelStyle] = None,
                          image_settings: Optional[ImageSettings] = None,
                          page_range: Optional[Tuple[int, int]] = None) -> ConversionResult:
        """
        PDFファイルをPowerPointファイルに変換

        Args:
            pdf_path: PDFファイルパス
            output_path: 出力PowerPointファイルパス
            pdf_settings: PDF変換設定
            slide_settings: スライド設定
            label_style: ラベルスタイル
            image_settings: 画像配置設定
            page_range: ページ範囲

        Returns:
            変換結果
        """
        start_time = datetime.now()
        progress = ConversionProgress(
            total_files=1,
            status=ConversionStatus.PREPARING,
            status_message="PDF→PowerPoint変換を準備中...",
            start_time=start_time,
            current_filename=pdf_path.name
        )

        temp_images = []

        try:
            # キャンセルフラグをリセット
            with self._conversion_lock:
                self._is_cancelled = False

            self._update_progress(progress)

            # ファイル検証
            if not FileValidator.validate_pdf_file(pdf_path):
                raise ValueError(f"無効なPDFファイル: {pdf_path}")

            # 出力ディレクトリ作成
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 一時ディレクトリ作成
            temp_dir = self.file_utils.temp_manager.create_temp_directory("pdf2pptx_images_")

            # PDF→画像変換
            progress.status = ConversionStatus.PROCESSING
            progress.status_message = "PDFを画像に変換中..."
            self._update_progress(progress)

            # PDF変換設定（PowerPoint用に最適化）
            if not pdf_settings:
                pdf_settings = PDFSettings(
                    dpi=150,
                    scale=1.0,
                    rotation_mode=RotationMode.AUTO,
                    output_format=ImageFormat.PNG,
                    transparent_background=False
                )

            # 変換実行
            temp_images = self.pdf_processor.convert_pdf_to_images(
                pdf_path, temp_dir, pdf_settings, page_range
            )

            if not temp_images:
                raise RuntimeError("PDFから画像への変換に失敗しました")

            # キャンセルチェック
            if self.is_conversion_cancelled():
                raise RuntimeError("変換がキャンセルされました")

            # PowerPoint作成
            progress.status_message = "PowerPointファイルを作成中..."
            progress.total_pages = len(temp_images)
            self._update_progress(progress)

            success = self.pptx_generator.convert_images_to_pptx(
                temp_images,
                output_path,
                title=pdf_path.stem,
                slide_settings=slide_settings,
                image_settings=image_settings,
                label_style=label_style,
                progress_callback=lambda c, t, s: self._update_pptx_progress(progress, c, t, s)
            )

            if not success:
                raise RuntimeError("PowerPointファイルの作成に失敗しました")

            # 完了処理
            progress.status = ConversionStatus.COMPLETED
            progress.status_message = "PDF→PowerPoint変換が完了しました"
            progress.current_file = 1
            self._update_progress(progress)

            # 結果作成
            processing_time = (datetime.now() - start_time).total_seconds()
            output_size = output_path.stat().st_size if output_path.exists() else 0

            result = ConversionResult(
                success=True,
                conversion_type=ConversionType.PDF_TO_PPTX,
                input_files=[pdf_path],
                output_files=[output_path],
                output_directory=output_path.parent,
                total_pages_processed=len(temp_images),
                processing_time_seconds=processing_time,
                file_size_mb=output_size / (1024 * 1024)
            )

            logger.info(f"PDF→PowerPoint変換完了: {len(temp_images)} ページ, {processing_time:.1f}秒")
            return result

        except Exception as e:
            progress.status = ConversionStatus.FAILED
            progress.error_message = str(e)
            progress.status_message = f"変換エラー: {str(e)[:100]}"
            self._update_progress(progress)

            self.error_handler.handle_error(
                error_type=ErrorType.CONVERSION_ERROR,
                error=e,
                details={"file": str(pdf_path)}
            )

            return ConversionResult(
                success=False,
                conversion_type=ConversionType.PDF_TO_PPTX,
                input_files=[pdf_path],
                error_message=str(e),
                processing_time_seconds=(datetime.now() - start_time).total_seconds()
            )

        finally:
            # 一時ファイルクリーンアップ
            try:
                self.file_utils.temp_manager.cleanup_temp_files()
            except Exception as e:
                logger.warning(f"一時ファイルクリーンアップエラー: {e}")

    def _update_pptx_progress(self, progress: ConversionProgress, current: int, total: int, status: str) -> None:
        """PowerPoint変換進捗を更新"""
        progress.current_page = current
        progress.total_pages = total
        progress.status_message = status
        self._update_progress(progress)

    def convert_images_to_pptx(self,
                             image_paths: List[Path],
                             output_path: Path,
                             title: Optional[str] = None,
                             slide_settings: Optional[SlideSettings] = None,
                             label_style: Optional[LabelStyle] = None,
                             image_settings: Optional[ImageSettings] = None) -> ConversionResult:
        """
        画像ファイル群をPowerPointファイルに変換

        Args:
            image_paths: 画像ファイルパスのリスト
            output_path: 出力PowerPointファイルパス
            title: プレゼンテーションタイトル
            slide_settings: スライド設定
            label_style: ラベルスタイル
            image_settings: 画像配置設定

        Returns:
            変換結果
        """
        start_time = datetime.now()
        progress = ConversionProgress(
            total_files=len(image_paths),
            status=ConversionStatus.PREPARING,
            status_message="画像→PowerPoint変換を準備中...",
            start_time=start_time
        )

        try:
            # キャンセルフラグをリセット
            with self._conversion_lock:
                self._is_cancelled = False

            self._update_progress(progress)

            # 画像ファイル検証
            validation_result = self.file_utils.batch_validate_files(image_paths, "image")
            valid_images = validation_result["valid"]

            if not valid_images:
                raise ValueError("有効な画像ファイルが見つかりません")

            if len(valid_images) != len(image_paths):
                logger.warning(f"一部の画像ファイルが無効です: {len(image_paths) - len(valid_images)} ファイル")

            # 出力ディレクトリ作成
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # PowerPoint変換
            progress.status = ConversionStatus.PROCESSING
            progress.total_pages = len(valid_images)
            self._update_progress(progress)

            success = self.pptx_generator.convert_images_to_pptx(
                valid_images,
                output_path,
                title=title or "画像プレゼンテーション",
                slide_settings=slide_settings,
                image_settings=image_settings,
                label_style=label_style,
                progress_callback=lambda c, t, s: self._update_pptx_progress(progress, c, t, s)
            )

            if not success:
                raise RuntimeError("PowerPointファイルの作成に失敗しました")

            # 完了処理
            progress.status = ConversionStatus.COMPLETED
            progress.status_message = "画像→PowerPoint変換が完了しました"
            progress.current_file = len(valid_images)
            self._update_progress(progress)

            # 結果作成
            processing_time = (datetime.now() - start_time).total_seconds()
            output_size = output_path.stat().st_size if output_path.exists() else 0

            result = ConversionResult(
                success=True,
                conversion_type=ConversionType.IMAGES_TO_PPTX,
                input_files=valid_images,
                output_files=[output_path],
                output_directory=output_path.parent,
                total_pages_processed=len(valid_images),
                processing_time_seconds=processing_time,
                file_size_mb=output_size / (1024 * 1024),
                warnings=[f"無効な画像ファイル: {len(image_paths) - len(valid_images)} 個"] if len(valid_images) != len(image_paths) else []
            )

            logger.info(f"画像→PowerPoint変換完了: {len(valid_images)} 画像, {processing_time:.1f}秒")
            return result

        except Exception as e:
            progress.status = ConversionStatus.FAILED
            progress.error_message = str(e)
            progress.status_message = f"変換エラー: {str(e)[:100]}"
            self._update_progress(progress)

            self.error_handler.handle_error(
                error_type=ErrorType.CONVERSION_ERROR,
                error=e,
                details={"image_count": len(image_paths)}
            )

            return ConversionResult(
                success=False,
                conversion_type=ConversionType.IMAGES_TO_PPTX,
                input_files=image_paths,
                error_message=str(e),
                processing_time_seconds=(datetime.now() - start_time).total_seconds()
            )

    def batch_convert_pdfs(self,
                         pdf_paths: List[Path],
                         output_dir: Path,
                         conversion_type: ConversionType,
                         pdf_settings: Optional[PDFSettings] = None,
                         slide_settings: Optional[SlideSettings] = None,
                         label_style: Optional[LabelStyle] = None,
                         image_settings: Optional[ImageSettings] = None) -> List[ConversionResult]:
        """
        複数PDFファイルの一括変換

        Args:
            pdf_paths: PDFファイルパスのリスト
            output_dir: 出力ディレクトリ
            conversion_type: 変換タイプ
            pdf_settings: PDF変換設定
            slide_settings: スライド設定
            label_style: ラベルスタイル
            image_settings: 画像配置設定

        Returns:
            変換結果のリスト
        """
        start_time = datetime.now()
        progress = ConversionProgress(
            total_files=len(pdf_paths),
            status=ConversionStatus.PREPARING,
            status_message="一括変換を準備中...",
            start_time=start_time
        )

        results = []

        try:
            # キャンセルフラグをリセット
            with self._conversion_lock:
                self._is_cancelled = False

            self._update_progress(progress)

            # PDF ファイル検証
            validation_result = self.file_utils.batch_validate_files(pdf_paths, "pdf")
            valid_pdfs = validation_result["valid"]

            if not valid_pdfs:
                raise ValueError("有効なPDFファイルが見つかりません")

            progress.total_files = len(valid_pdfs)
            progress.status = ConversionStatus.PROCESSING
            self._update_progress(progress)

            # 並列変換実行
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 変換タスクを作成
                future_to_pdf = {}

                for i, pdf_path in enumerate(valid_pdfs):
                    if conversion_type == ConversionType.PDF_TO_PNG:
                        future = executor.submit(
                            self._single_pdf_to_images,
                            pdf_path, output_dir, pdf_settings, i + 1, len(valid_pdfs)
                        )
                    elif conversion_type == ConversionType.PDF_TO_PPTX:
                        # 出力ファイル名生成
                        output_file = output_dir / f"{pdf_path.stem}.pptx"
                        future = executor.submit(
                            self._single_pdf_to_pptx,
                            pdf_path, output_file, pdf_settings, slide_settings,
                            label_style, image_settings, i + 1, len(valid_pdfs)
                        )
                    else:
                        continue

                    future_to_pdf[future] = pdf_path

                # 結果収集
                for future in as_completed(future_to_pdf):
                    pdf_path = future_to_pdf[future]

                    # キャンセルチェック
                    if self.is_conversion_cancelled():
                        progress.status = ConversionStatus.CANCELLED
                        progress.status_message = "一括変換がキャンセルされました"
                        self._update_progress(progress)
                        break

                    try:
                        result = future.result()
                        results.append(result)

                        # 進捗更新
                        progress.current_file = len(results)
                        progress.current_filename = pdf_path.name
                        progress.status_message = f"一括変換中... ({len(results)}/{len(valid_pdfs)})"
                        self._update_progress(progress)

                    except Exception as e:
                        logger.error(f"PDF変換エラー: {pdf_path}, {e}")
                        error_result = ConversionResult(
                            success=False,
                            conversion_type=conversion_type,
                            input_files=[pdf_path],
                            error_message=str(e)
                        )
                        results.append(error_result)

            # 完了処理
            if not self.is_conversion_cancelled():
                progress.status = ConversionStatus.COMPLETED
                success_count = sum(1 for r in results if r.success)
                progress.status_message = f"一括変換完了: {success_count}/{len(results)} 成功"
                self._update_progress(progress)

            logger.info(f"一括変換完了: {len(results)} ファイル処理")
            return results

        except Exception as e:
            progress.status = ConversionStatus.FAILED
            progress.error_message = str(e)
            progress.status_message = f"一括変換エラー: {str(e)[:100]}"
            self._update_progress(progress)

            self.error_handler.handle_error(
                error_type=ErrorType.CONVERSION_ERROR,
                error=e,
                details={"pdf_count": len(pdf_paths)}
            )

            return results

    def _single_pdf_to_images(self,
                            pdf_path: Path,
                            output_dir: Path,
                            pdf_settings: Optional[PDFSettings],
                            file_index: int,
                            total_files: int) -> ConversionResult:
        """単一PDF→画像変換（並列処理用）"""
        try:
            logger.debug(f"PDF→画像変換開始: {pdf_path} ({file_index}/{total_files})")
            return self.convert_pdf_to_images(pdf_path, output_dir, pdf_settings)
        except Exception as e:
            logger.error(f"PDF→画像変換エラー: {pdf_path}, {e}")
            return ConversionResult(
                success=False,
                conversion_type=ConversionType.PDF_TO_PNG,
                input_files=[pdf_path],
                error_message=str(e)
            )

    def _single_pdf_to_pptx(self,
                          pdf_path: Path,
                          output_path: Path,
                          pdf_settings: Optional[PDFSettings],
                          slide_settings: Optional[SlideSettings],
                          label_style: Optional[LabelStyle],
                          image_settings: Optional[ImageSettings],
                          file_index: int,
                          total_files: int) -> ConversionResult:
        """単一PDF→PowerPoint変換（並列処理用）"""
        try:
            logger.debug(f"PDF→PowerPoint変換開始: {pdf_path} ({file_index}/{total_files})")
            return self.convert_pdf_to_pptx(
                pdf_path, output_path, pdf_settings, slide_settings,
                label_style, image_settings
            )
        except Exception as e:
            logger.error(f"PDF→PowerPoint変換エラー: {pdf_path}, {e}")
            return ConversionResult(
                success=False,
                conversion_type=ConversionType.PDF_TO_PPTX,
                input_files=[pdf_path],
                error_message=str(e)
            )

    def get_conversion_statistics(self, results: List[ConversionResult]) -> Dict[str, Any]:
        """
        変換統計情報を取得

        Args:
            results: 変換結果のリスト

        Returns:
            統計情報辞書
        """
        try:
            if not results:
                return {"error": "変換結果がありません"}

            total_files = len(results)
            successful_files = sum(1 for r in results if r.success)
            failed_files = total_files - successful_files

            total_pages = sum(r.total_pages_processed for r in results)
            total_time = sum(r.processing_time_seconds for r in results)
            total_size_mb = sum(r.file_size_mb for r in results)

            average_time_per_file = total_time / total_files if total_files > 0 else 0
            average_pages_per_file = total_pages / total_files if total_files > 0 else 0

            return {
                "total_files": total_files,
                "successful_files": successful_files,
                "failed_files": failed_files,
                "success_rate": (successful_files / total_files * 100) if total_files > 0 else 0,
                "total_pages_processed": total_pages,
                "total_processing_time_seconds": total_time,
                "total_output_size_mb": total_size_mb,
                "average_time_per_file": average_time_per_file,
                "average_pages_per_file": average_pages_per_file,
                "conversion_types": list(set(r.conversion_type.value for r in results)),
                "errors": [r.error_message for r in results if not r.success and r.error_message],
                "warnings": [w for r in results for w in r.warnings]
            }

        except Exception as e:
            logger.error(f"統計情報取得エラー: {e}")
            return {"error": str(e)}

    def cleanup_resources(self) -> None:
        """リソースクリーンアップ"""
        try:
            # PDF処理エンジンクリーンアップ
            if hasattr(self.pdf_processor, 'cleanup_temp_files'):
                self.pdf_processor.cleanup_temp_files()

            # ファイルユーティリティクリーンアップ
            self.file_utils.cleanup_all_temp_files()

            logger.info("変換サービスリソースをクリーンアップしました")

        except Exception as e:
            logger.error(f"リソースクリーンアップエラー: {e}")

    def __del__(self):
        """デストラクタ - リソースクリーンアップ"""
        try:
            self.cleanup_resources()
        except:
            pass


# 便利関数
def create_optimized_pdf_settings(target_use: str = "presentation") -> PDFSettings:
    """
    用途に最適化されたPDF変換設定を作成

    Args:
        target_use: 用途 ("presentation", "print", "web", "archive")

    Returns:
        最適化されたPDF変換設定
    """
    if target_use == "presentation":
        return PDFSettings(
            dpi=150,
            scale=1.0,
            rotation_mode=RotationMode.AUTO,
            output_format=ImageFormat.PNG,
            transparent_background=False,
            anti_aliasing=True
        )
    elif target_use == "print":
        return PDFSettings(
            dpi=300,
            scale=1.0,
            rotation_mode=RotationMode.NONE,
            output_format=ImageFormat.PNG,
            transparent_background=True,
            anti_aliasing=True
        )
    elif target_use == "web":
        return PDFSettings(
            dpi=96,
            scale=1.0,
            rotation_mode=RotationMode.AUTO,
            output_format=ImageFormat.JPG,
            quality=85,
            transparent_background=False,
            anti_aliasing=True
        )
    elif target_use == "archive":
        return PDFSettings(
            dpi=200,
            scale=1.0,
            rotation_mode=RotationMode.NONE,
            output_format=ImageFormat.TIFF,
            transparent_background=True,
            anti_aliasing=True
        )
    else:
        return PDFSettings()  # デフォルト設定


def create_standard_pptx_settings() -> Tuple[SlideSettings, LabelStyle, ImageSettings]:
    """
    標準的なPowerPoint設定を作成

    Returns:
        (スライド設定, ラベルスタイル, 画像設定) のタプル
    """
    slide_settings = SlideSettings(
        size=SlideSize.A3_LANDSCAPE,
        width_mm=420.0,
        height_mm=297.0
    )

    label_style = LabelStyle(
        font_name="メイリオ",
        font_size=18,
        font_color="#FFFFFF",
        background_color="#1976D2",
        position=LabelPosition.BOTTOM_CENTER,
        add_page_numbers=True,
        add_filename=True
    )

    image_settings = ImageSettings(
        maintain_aspect_ratio=True,
        center_horizontally=True,
        center_vertically=True,
        max_width_percent=90.0,
        max_height_percent=80.0
    )

    return slide_settings, label_style, image_settings