"""
PDF処理エンジン
PyMuPDF（fitz）を使用したPDF読み込み・変換・画像出力機能
"""

import fitz  # PyMuPDF
import os
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any, Generator
from dataclasses import dataclass
from enum import Enum
from PIL import Image, ImageOps
import asyncio
import concurrent.futures
from loguru import logger

from ..utils.error_handler import ErrorHandler, ErrorType
from ..utils.config import ConfigManager


class RotationMode(Enum):
    """画像回転モード"""
    NONE = "none"           # 回転なし
    AUTO = "auto"           # 自動回転（縦横比に基づく）
    CLOCKWISE_90 = "cw_90"  # 時計回り90度
    CLOCKWISE_180 = "cw_180"  # 時計回り180度
    CLOCKWISE_270 = "cw_270"  # 時計回り270度


class ImageFormat(Enum):
    """出力画像フォーマット"""
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    BMP = "bmp"
    TIFF = "tiff"


@dataclass
class PDFPageInfo:
    """PDFページ情報"""
    page_number: int
    width: float
    height: float
    rotation: int
    is_landscape: bool
    media_box: Tuple[float, float, float, float]


@dataclass
class ConversionSettings:
    """変換設定"""
    dpi: int = 150
    scale: float = 1.5
    rotation_mode: RotationMode = RotationMode.AUTO
    output_format: ImageFormat = ImageFormat.PNG
    quality: int = 95  # JPEG品質（1-100）
    transparent_background: bool = True
    anti_aliasing: bool = True


class PDFProcessor:
    """PDF処理エンジンクラス"""

    def __init__(self,
                 config_manager: Optional[ConfigManager] = None,
                 error_handler: Optional[ErrorHandler] = None):
        """
        初期化

        Args:
            config_manager: 設定管理インスタンス
            error_handler: エラーハンドラーインスタンス
        """
        self.config_manager = config_manager or ConfigManager()
        self.error_handler = error_handler or ErrorHandler()
        self.temp_dir = Path(tempfile.gettempdir()) / "pdf2pptx_temp"
        self.temp_dir.mkdir(exist_ok=True)

        # 変換設定を初期化
        self._load_conversion_settings()

        logger.info("PDF処理エンジンを初期化しました")

    def _load_conversion_settings(self) -> None:
        """設定ファイルから変換設定を読み込み"""
        try:
            config = self.config_manager.get_config("conversion.pdf_to_png")

            self.default_settings = ConversionSettings(
                dpi=config.get("dpi", 150),
                scale=config.get("scale", 1.5),
                rotation_mode=RotationMode(config.get("rotation_mode", "auto")),
                output_format=ImageFormat(config.get("output_format", "png")),
                quality=config.get("quality", 95),
                transparent_background=config.get("transparent_background", True),
                anti_aliasing=config.get("anti_aliasing", True)
            )

            logger.debug(f"変換設定を読み込みました: {self.default_settings}")

        except Exception as e:
            logger.warning(f"設定読み込みエラー、デフォルト設定を使用: {e}")
            self.default_settings = ConversionSettings()

    def validate_pdf_file(self, pdf_path: Path) -> bool:
        """
        PDFファイルの検証

        Args:
            pdf_path: PDFファイルパス

        Returns:
            検証成功時True

        Raises:
            FileNotFoundError: ファイルが存在しない
            ValueError: PDFファイルでない、または破損している
        """
        try:
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")

            if not pdf_path.is_file():
                raise ValueError(f"指定されたパスはファイルではありません: {pdf_path}")

            if pdf_path.suffix.lower() not in ['.pdf']:
                raise ValueError(f"PDFファイルではありません: {pdf_path}")

            # PyMuPDFでPDFファイルを開いて検証
            try:
                doc = fitz.open(str(pdf_path))
                if doc.page_count == 0:
                    raise ValueError("PDFファイルにページが含まれていません")

                # 最初のページが正常に読み込めるかテスト
                doc[0]
                doc.close()

                logger.info(f"PDFファイルの検証が完了しました: {pdf_path}")
                return True

            except Exception as e:
                raise ValueError(f"PDFファイルが破損しているか読み込めません: {e}")

        except Exception as e:
            self.error_handler.handle_error(
                error_type=ErrorType.PDF_PROCESSING,
                error=e,
                details={"file": str(pdf_path)}
            )
            raise

    def get_pdf_info(self, pdf_path: Path) -> Dict[str, Any]:
        """
        PDFファイルの基本情報を取得

        Args:
            pdf_path: PDFファイルパス

        Returns:
            PDF情報辞書

        Raises:
            FileNotFoundError: ファイルが存在しない
            ValueError: PDFファイルでない、または破損している
        """
        try:
            self.validate_pdf_file(pdf_path)

            doc = fitz.open(str(pdf_path))

            # メタデータ取得
            metadata = doc.metadata

            # ページ情報取得
            pages_info = []
            for page_num in range(doc.page_count):
                page = doc[page_num]
                rect = page.rect

                page_info = PDFPageInfo(
                    page_number=page_num + 1,
                    width=rect.width,
                    height=rect.height,
                    rotation=page.rotation,
                    is_landscape=rect.width > rect.height,
                    media_box=(rect.x0, rect.y0, rect.x1, rect.y1)
                )
                pages_info.append(page_info)

            doc.close()

            pdf_info = {
                "file_path": str(pdf_path),
                "file_size": pdf_path.stat().st_size,
                "page_count": len(pages_info),
                "metadata": {
                    "title": metadata.get("title", ""),
                    "author": metadata.get("author", ""),
                    "subject": metadata.get("subject", ""),
                    "creator": metadata.get("creator", ""),
                    "producer": metadata.get("producer", ""),
                    "creation_date": metadata.get("creationDate", ""),
                    "mod_date": metadata.get("modDate", "")
                },
                "pages": [
                    {
                        "page_number": p.page_number,
                        "width": p.width,
                        "height": p.height,
                        "rotation": p.rotation,
                        "is_landscape": p.is_landscape,
                        "media_box": p.media_box
                    }
                    for p in pages_info
                ],
                "security": {
                    "is_encrypted": doc.is_encrypted if hasattr(doc, 'is_encrypted') else False,
                    "needs_password": doc.needs_pass if hasattr(doc, 'needs_pass') else False
                }
            }

            logger.info(f"PDFファイル情報を取得しました: {pdf_path}")
            return pdf_info

        except Exception as e:
            self.error_handler.handle_error(
                error_type=ErrorType.PDF_PROCESSING,
                error=e,
                details={"file": str(pdf_path)}
            )
            raise

    def convert_page_to_image(self,
                            pdf_path: Path,
                            page_number: int,
                            settings: Optional[ConversionSettings] = None) -> Image.Image:
        """
        PDFの指定ページを画像に変換

        Args:
            pdf_path: PDFファイルパス
            page_number: ページ番号（1から開始）
            settings: 変換設定

        Returns:
            PIL Image オブジェクト

        Raises:
            FileNotFoundError: ファイルが存在しない
            ValueError: 無効なページ番号
            RuntimeError: 変換処理エラー
        """
        try:
            settings = settings or self.default_settings

            self.validate_pdf_file(pdf_path)

            doc = fitz.open(str(pdf_path))

            if page_number < 1 or page_number > doc.page_count:
                doc.close()
                raise ValueError(f"無効なページ番号: {page_number} (総ページ数: {doc.page_count})")

            page = doc[page_number - 1]

            # DPIとスケールに基づいてマトリックスを計算
            zoom = settings.dpi / 72.0 * settings.scale
            matrix = fitz.Matrix(zoom, zoom)

            # ページを画像に変換
            if settings.anti_aliasing:
                pix = page.get_pixmap(matrix=matrix, alpha=settings.transparent_background)
            else:
                pix = page.get_pixmap(matrix=matrix, alpha=settings.transparent_background)

            # PIL Imageに変換
            img_data = pix.pil_tobytes(format="PNG")
            image = Image.open(io.BytesIO(img_data))

            # 回転処理
            image = self._apply_rotation(image, page, settings.rotation_mode)

            doc.close()

            logger.debug(f"ページ {page_number} を画像に変換しました: {image.size}")
            return image

        except Exception as e:
            self.error_handler.handle_error(
                error_type=ErrorType.PDF_PROCESSING,
                error=e,
                details={"file": str(pdf_path), "page": page_number}
            )
            raise

    def _apply_rotation(self,
                       image: Image.Image,
                       page: fitz.Page,
                       rotation_mode: RotationMode) -> Image.Image:
        """
        画像に回転を適用

        Args:
            image: PIL Image オブジェクト
            page: PyMuPDF ページオブジェクト
            rotation_mode: 回転モード

        Returns:
            回転適用後のPIL Image
        """
        try:
            if rotation_mode == RotationMode.NONE:
                return image

            elif rotation_mode == RotationMode.AUTO:
                # ページの向きと画像の向きを比較して自動回転
                page_rect = page.rect
                page_is_landscape = page_rect.width > page_rect.height
                image_is_landscape = image.width > image.height

                # 向きが異なる場合は90度回転
                if page_is_landscape != image_is_landscape:
                    return image.rotate(-90, expand=True)
                return image

            elif rotation_mode == RotationMode.CLOCKWISE_90:
                return image.rotate(-90, expand=True)

            elif rotation_mode == RotationMode.CLOCKWISE_180:
                return image.rotate(-180, expand=True)

            elif rotation_mode == RotationMode.CLOCKWISE_270:
                return image.rotate(-270, expand=True)

            else:
                logger.warning(f"未対応の回転モード: {rotation_mode}")
                return image

        except Exception as e:
            logger.warning(f"画像回転エラー: {e}")
            return image

    def convert_pdf_to_images(self,
                            pdf_path: Path,
                            output_dir: Path,
                            settings: Optional[ConversionSettings] = None,
                            page_range: Optional[Tuple[int, int]] = None,
                            name_pattern: str = "{basename}_page_{page:03d}") -> List[Path]:
        """
        PDFファイル全体または指定範囲を画像ファイルに変換

        Args:
            pdf_path: PDFファイルパス
            output_dir: 出力ディレクトリ
            settings: 変換設定
            page_range: ページ範囲 (start, end) 1から開始、Noneで全ページ
            name_pattern: ファイル名パターン

        Returns:
            生成された画像ファイルパスのリスト

        Raises:
            FileNotFoundError: ファイルが存在しない
            ValueError: 無効なページ範囲
            RuntimeError: 変換処理エラー
        """
        try:
            settings = settings or self.default_settings

            self.validate_pdf_file(pdf_path)

            # 出力ディレクトリを作成
            output_dir.mkdir(parents=True, exist_ok=True)

            doc = fitz.open(str(pdf_path))
            total_pages = doc.page_count

            # ページ範囲の設定
            if page_range:
                start_page, end_page = page_range
                if start_page < 1 or end_page > total_pages or start_page > end_page:
                    doc.close()
                    raise ValueError(f"無効なページ範囲: {page_range} (総ページ数: {total_pages})")
            else:
                start_page, end_page = 1, total_pages

            output_files = []
            basename = pdf_path.stem

            for page_num in range(start_page, end_page + 1):
                try:
                    # ページを画像に変換
                    image = self.convert_page_to_image(pdf_path, page_num, settings)

                    # ファイル名生成
                    filename = name_pattern.format(
                        basename=basename,
                        page=page_num,
                        total=total_pages
                    )
                    output_path = output_dir / f"{filename}.{settings.output_format.value}"

                    # 画像保存
                    if settings.output_format in [ImageFormat.JPG, ImageFormat.JPEG]:
                        # JPEG形式の場合はRGBに変換
                        if image.mode in ['RGBA', 'LA']:
                            background = Image.new('RGB', image.size, (255, 255, 255))
                            if image.mode == 'RGBA':
                                background.paste(image, mask=image.split()[-1])
                            else:
                                background.paste(image)
                            image = background
                        image.save(output_path, quality=settings.quality, optimize=True)
                    else:
                        image.save(output_path)

                    output_files.append(output_path)
                    logger.debug(f"ページ {page_num} を保存しました: {output_path}")

                except Exception as e:
                    logger.error(f"ページ {page_num} の変換に失敗: {e}")
                    continue

            doc.close()

            logger.info(f"PDF変換完了: {len(output_files)} ページを変換しました")
            return output_files

        except Exception as e:
            self.error_handler.handle_error(
                error_type=ErrorType.PDF_PROCESSING,
                error=e,
                details={"file": str(pdf_path)}
            )
            raise

    async def convert_pdf_to_images_async(self,
                                        pdf_path: Path,
                                        output_dir: Path,
                                        settings: Optional[ConversionSettings] = None,
                                        page_range: Optional[Tuple[int, int]] = None,
                                        name_pattern: str = "{basename}_page_{page:03d}",
                                        progress_callback: Optional[callable] = None) -> List[Path]:
        """
        PDFファイルを非同期で画像に変換（大きなファイル向け）

        Args:
            pdf_path: PDFファイルパス
            output_dir: 出力ディレクトリ
            settings: 変換設定
            page_range: ページ範囲
            name_pattern: ファイル名パターン
            progress_callback: 進捗コールバック関数 callback(current, total)

        Returns:
            生成された画像ファイルパスのリスト
        """
        try:
            settings = settings or self.default_settings

            self.validate_pdf_file(pdf_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            doc = fitz.open(str(pdf_path))
            total_pages = doc.page_count

            # ページ範囲の設定
            if page_range:
                start_page, end_page = page_range
                if start_page < 1 or end_page > total_pages or start_page > end_page:
                    doc.close()
                    raise ValueError(f"無効なページ範囲: {page_range}")
            else:
                start_page, end_page = 1, total_pages

            doc.close()

            # 並列処理用のタスクを作成
            max_workers = min(4, os.cpu_count() or 1)  # 最大4プロセス

            tasks = []
            for page_num in range(start_page, end_page + 1):
                task = self._convert_single_page_async(
                    pdf_path, page_num, output_dir, settings, name_pattern, total_pages
                )
                tasks.append(task)

            # 並列実行
            output_files = []
            completed = 0

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_page = {
                    executor.submit(self._convert_single_page_sync,
                                  pdf_path, page_num, output_dir, settings, name_pattern, total_pages): page_num
                    for page_num in range(start_page, end_page + 1)
                }

                for future in concurrent.futures.as_completed(future_to_page):
                    page_num = future_to_page[future]
                    try:
                        result = future.result()
                        if result:
                            output_files.append(result)
                        completed += 1

                        if progress_callback:
                            progress_callback(completed, end_page - start_page + 1)

                    except Exception as e:
                        logger.error(f"ページ {page_num} の非同期変換に失敗: {e}")
                        completed += 1

                        if progress_callback:
                            progress_callback(completed, end_page - start_page + 1)

            logger.info(f"非同期PDF変換完了: {len(output_files)} ページを変換しました")
            return sorted(output_files)

        except Exception as e:
            self.error_handler.handle_error(
                error_type=ErrorType.PDF_PROCESSING,
                error=e,
                details={"file": str(pdf_path)}
            )
            raise

    def _convert_single_page_sync(self,
                                pdf_path: Path,
                                page_num: int,
                                output_dir: Path,
                                settings: ConversionSettings,
                                name_pattern: str,
                                total_pages: int) -> Optional[Path]:
        """
        単一ページの同期変換（並列処理用）

        Args:
            pdf_path: PDFファイルパス
            page_num: ページ番号
            output_dir: 出力ディレクトリ
            settings: 変換設定
            name_pattern: ファイル名パターン
            total_pages: 総ページ数

        Returns:
            生成されたファイルパス、失敗時はNone
        """
        try:
            image = self.convert_page_to_image(pdf_path, page_num, settings)

            filename = name_pattern.format(
                basename=pdf_path.stem,
                page=page_num,
                total=total_pages
            )
            output_path = output_dir / f"{filename}.{settings.output_format.value}"

            if settings.output_format in [ImageFormat.JPG, ImageFormat.JPEG]:
                if image.mode in ['RGBA', 'LA']:
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'RGBA':
                        background.paste(image, mask=image.split()[-1])
                    else:
                        background.paste(image)
                    image = background
                image.save(output_path, quality=settings.quality, optimize=True)
            else:
                image.save(output_path)

            return output_path

        except Exception as e:
            logger.error(f"ページ {page_num} の変換に失敗: {e}")
            return None

    def get_page_preview(self,
                        pdf_path: Path,
                        page_number: int,
                        max_size: Tuple[int, int] = (200, 200)) -> Image.Image:
        """
        PDFページのプレビュー画像を生成

        Args:
            pdf_path: PDFファイルパス
            page_number: ページ番号（1から開始）
            max_size: プレビュー最大サイズ

        Returns:
            プレビュー用PIL Image

        Raises:
            FileNotFoundError: ファイルが存在しない
            ValueError: 無効なページ番号
        """
        try:
            preview_settings = ConversionSettings(
                dpi=72,  # 低DPIでプレビュー生成
                scale=0.5,
                output_format=ImageFormat.PNG,
                transparent_background=False
            )

            image = self.convert_page_to_image(pdf_path, page_number, preview_settings)

            # サイズ調整
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            logger.debug(f"プレビュー画像を生成しました: {image.size}")
            return image

        except Exception as e:
            self.error_handler.handle_error(
                error_type=ErrorType.PDF_PROCESSING,
                error=e,
                details={"file": str(pdf_path), "page": page_number}
            )
            raise

    def cleanup_temp_files(self) -> None:
        """一時ファイルのクリーンアップ"""
        try:
            if self.temp_dir.exists():
                for file_path in self.temp_dir.glob("*"):
                    try:
                        if file_path.is_file():
                            file_path.unlink()
                        elif file_path.is_dir():
                            import shutil
                            shutil.rmtree(file_path)
                    except Exception as e:
                        logger.warning(f"一時ファイル削除失敗: {file_path}, {e}")

                logger.info("一時ファイルをクリーンアップしました")

        except Exception as e:
            logger.error(f"一時ファイルクリーンアップエラー: {e}")

    def __del__(self):
        """デストラクタ - 一時ファイルクリーンアップ"""
        try:
            self.cleanup_temp_files()
        except:
            pass


# 必要なインポートを追加
import io


# ユーティリティ関数
def estimate_conversion_time(pdf_path: Path, settings: ConversionSettings) -> float:
    """
    変換処理時間を推定

    Args:
        pdf_path: PDFファイルパス
        settings: 変換設定

    Returns:
        推定時間（秒）
    """
    try:
        # ファイルサイズとページ数から推定
        file_size_mb = pdf_path.stat().st_size / (1024 * 1024)

        doc = fitz.open(str(pdf_path))
        page_count = doc.page_count
        doc.close()

        # 基本時間（秒/ページ）
        base_time_per_page = 0.5

        # DPIとスケールによる補正
        dpi_factor = settings.dpi / 150.0
        scale_factor = settings.scale

        # ファイルサイズによる補正
        size_factor = max(1.0, file_size_mb / 10.0)

        estimated_time = page_count * base_time_per_page * dpi_factor * scale_factor * size_factor

        return max(1.0, estimated_time)  # 最低1秒

    except Exception as e:
        logger.warning(f"変換時間推定エラー: {e}")
        return 30.0  # デフォルト値