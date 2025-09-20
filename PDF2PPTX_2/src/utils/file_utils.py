"""
ファイルユーティリティ
ファイル操作、パス検証、一時ファイル管理、Windows 11対応機能
"""

import os
import re
import shutil
import tempfile
import hashlib
from pathlib import Path, WindowsPath
from typing import List, Optional, Tuple, Union, Dict, Any
from datetime import datetime
import platform
from loguru import logger

from .error_handler import ErrorHandler, ErrorType


class FileValidator:
    """ファイル検証クラス"""

    # サポートされているファイル拡張子
    SUPPORTED_PDF_EXTENSIONS = {'.pdf'}
    SUPPORTED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}
    SUPPORTED_PPTX_EXTENSIONS = {'.pptx', '.ppt'}

    # Windows 11 予約語
    WINDOWS_RESERVED_NAMES = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }

    # Windows 11 無効文字
    WINDOWS_INVALID_CHARS = {'<', '>', ':', '"', '|', '?', '*', '/'}

    @classmethod
    def validate_pdf_file(cls, file_path: Path) -> bool:
        """
        PDFファイルの検証

        Args:
            file_path: ファイルパス

        Returns:
            検証成功時True
        """
        try:
            if not file_path.exists():
                logger.warning(f"ファイルが存在しません: {file_path}")
                return False

            if not file_path.is_file():
                logger.warning(f"ディレクトリまたは特殊ファイルです: {file_path}")
                return False

            if file_path.suffix.lower() not in cls.SUPPORTED_PDF_EXTENSIONS:
                logger.warning(f"サポートされていないファイル形式: {file_path.suffix}")
                return False

            # ファイルサイズチェック（最大500MB）
            file_size = file_path.stat().st_size
            if file_size > 500 * 1024 * 1024:
                logger.warning(f"ファイルサイズが大きすぎます: {file_size / (1024*1024):.1f}MB")
                return False

            if file_size == 0:
                logger.warning(f"空のファイルです: {file_path}")
                return False

            logger.debug(f"PDFファイル検証OK: {file_path}")
            return True

        except Exception as e:
            logger.error(f"PDFファイル検証エラー: {e}")
            return False

    @classmethod
    def validate_image_file(cls, file_path: Path) -> bool:
        """
        画像ファイルの検証

        Args:
            file_path: ファイルパス

        Returns:
            検証成功時True
        """
        try:
            if not file_path.exists():
                return False

            if not file_path.is_file():
                return False

            if file_path.suffix.lower() not in cls.SUPPORTED_IMAGE_EXTENSIONS:
                return False

            # ファイルサイズチェック（最大100MB）
            file_size = file_path.stat().st_size
            if file_size > 100 * 1024 * 1024:
                logger.warning(f"画像ファイルサイズが大きすぎます: {file_size / (1024*1024):.1f}MB")
                return False

            if file_size == 0:
                return False

            # PIL で画像を開けるかテスト
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    img.verify()
                return True
            except Exception:
                logger.warning(f"画像ファイルの読み込みに失敗: {file_path}")
                return False

        except Exception as e:
            logger.error(f"画像ファイル検証エラー: {e}")
            return False

    @classmethod
    def validate_filename(cls, filename: str) -> bool:
        """
        Windows 11 対応ファイル名検証

        Args:
            filename: ファイル名

        Returns:
            検証成功時True
        """
        try:
            if not filename or len(filename.strip()) == 0:
                return False

            # Windows パス長制限（260文字）
            if len(filename) > 200:  # 余裕を持って200文字
                return False

            # 無効文字チェック
            if any(char in filename for char in cls.WINDOWS_INVALID_CHARS):
                return False

            # 先頭・末尾の空白とピリオドチェック
            if filename.startswith(' ') or filename.endswith(' '):
                return False

            if filename.endswith('.'):
                return False

            # 予約語チェック
            base_name = filename.split('.')[0].upper()
            if base_name in cls.WINDOWS_RESERVED_NAMES:
                return False

            return True

        except Exception as e:
            logger.error(f"ファイル名検証エラー: {e}")
            return False

    @classmethod
    def validate_directory_path(cls, dir_path: Path) -> bool:
        """
        ディレクトリパス検証

        Args:
            dir_path: ディレクトリパス

        Returns:
            検証成功時True
        """
        try:
            # パス長チェック（Windows 260文字制限）
            if len(str(dir_path)) > 250:
                logger.warning(f"パスが長すぎます: {len(str(dir_path))} 文字")
                return False

            # ディレクトリ名の各部分をチェック
            for part in dir_path.parts:
                if not cls.validate_filename(part):
                    logger.warning(f"無効なディレクトリ名: {part}")
                    return False

            return True

        except Exception as e:
            logger.error(f"ディレクトリパス検証エラー: {e}")
            return False


class SafeFilename:
    """安全なファイル名生成クラス"""

    @staticmethod
    def sanitize_filename(filename: str, replacement: str = "_") -> str:
        """
        ファイル名をWindows 11対応で安全に変換

        Args:
            filename: 元のファイル名
            replacement: 無効文字の置換文字

        Returns:
            安全なファイル名
        """
        try:
            if not filename:
                return "untitled"

            # 無効文字を置換
            safe_name = filename
            for char in FileValidator.WINDOWS_INVALID_CHARS:
                safe_name = safe_name.replace(char, replacement)

            # 改行文字やタブも置換
            safe_name = re.sub(r'[\r\n\t]', replacement, safe_name)

            # 先頭・末尾の空白を削除
            safe_name = safe_name.strip()

            # 末尾のピリオドを削除
            safe_name = safe_name.rstrip('.')

            # 予約語チェック
            name_parts = safe_name.split('.')
            if name_parts[0].upper() in FileValidator.WINDOWS_RESERVED_NAMES:
                name_parts[0] = f"{name_parts[0]}_safe"
                safe_name = '.'.join(name_parts)

            # 長さ制限
            if len(safe_name) > 200:
                name, ext = os.path.splitext(safe_name)
                max_name_length = 200 - len(ext)
                safe_name = name[:max_name_length] + ext

            # 空の場合のフォールバック
            if not safe_name:
                safe_name = "untitled"

            return safe_name

        except Exception as e:
            logger.error(f"ファイル名変換エラー: {e}")
            return f"safe_filename_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    @staticmethod
    def generate_unique_filename(base_path: Path, desired_name: str) -> Path:
        """
        重複しないユニークなファイル名を生成

        Args:
            base_path: ベースディレクトリ
            desired_name: 希望するファイル名

        Returns:
            ユニークなファイルパス
        """
        try:
            # 安全なファイル名に変換
            safe_name = SafeFilename.sanitize_filename(desired_name)

            # 拡張子を分離
            name, ext = os.path.splitext(safe_name)

            # ベースパスを作成
            target_path = base_path / safe_name

            # ファイルが存在しない場合はそのまま返す
            if not target_path.exists():
                return target_path

            # 重複している場合は番号を付加
            counter = 1
            while True:
                new_name = f"{name}_{counter:03d}{ext}"
                new_path = base_path / new_name

                if not new_path.exists():
                    logger.debug(f"ユニークなファイル名を生成: {new_path}")
                    return new_path

                counter += 1

                # 無限ループ防止
                if counter > 999:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    fallback_name = f"{name}_{timestamp}{ext}"
                    return base_path / fallback_name

        except Exception as e:
            logger.error(f"ユニークファイル名生成エラー: {e}")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            return base_path / f"file_{timestamp}.tmp"


class DirectoryManager:
    """ディレクトリ管理クラス"""

    @staticmethod
    def create_output_directory(base_dir: Path,
                              source_file: Path,
                              create_subfolder: bool = True,
                              subfolder_prefix: str = "converted") -> Path:
        """
        出力ディレクトリを作成

        Args:
            base_dir: ベースディレクトリ
            source_file: ソースファイル
            create_subfolder: サブフォルダを作成するか
            subfolder_prefix: サブフォルダのプレフィックス

        Returns:
            作成された出力ディレクトリパス

        Raises:
            OSError: ディレクトリ作成エラー
        """
        try:
            if create_subfolder:
                # ソースファイル名を使ったサブフォルダ名を生成
                source_name = source_file.stem
                safe_name = SafeFilename.sanitize_filename(source_name)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M')

                subfolder_name = f"{subfolder_prefix}_{safe_name}_{timestamp}"
                output_dir = base_dir / subfolder_name
            else:
                output_dir = base_dir

            # ディレクトリ作成
            output_dir.mkdir(parents=True, exist_ok=True)

            # 書き込み権限チェック
            if not os.access(output_dir, os.W_OK):
                raise OSError(f"ディレクトリへの書き込み権限がありません: {output_dir}")

            logger.info(f"出力ディレクトリを作成しました: {output_dir}")
            return output_dir

        except Exception as e:
            logger.error(f"出力ディレクトリ作成エラー: {e}")
            raise

    @staticmethod
    def get_available_space(directory: Path) -> int:
        """
        ディスクの使用可能容量を取得

        Args:
            directory: チェックするディレクトリ

        Returns:
            使用可能容量（バイト）
        """
        try:
            if platform.system() == "Windows":
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(str(directory)),
                    ctypes.pointer(free_bytes),
                    None, None
                )
                return free_bytes.value
            else:
                statvfs = os.statvfs(directory)
                return statvfs.f_frsize * statvfs.f_bavail

        except Exception as e:
            logger.warning(f"ディスク容量取得エラー: {e}")
            return 0

    @staticmethod
    def cleanup_directory(directory: Path,
                         max_age_days: int = 7,
                         pattern: str = "*") -> int:
        """
        ディレクトリのクリーンアップ

        Args:
            directory: クリーンアップ対象ディレクトリ
            max_age_days: 最大保持日数
            pattern: ファイルパターン

        Returns:
            削除されたファイル数
        """
        try:
            if not directory.exists():
                return 0

            now = datetime.now()
            deleted_count = 0

            for file_path in directory.glob(pattern):
                try:
                    if not file_path.is_file():
                        continue

                    # ファイルの更新日時を取得
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    age_days = (now - mtime).days

                    if age_days > max_age_days:
                        file_path.unlink()
                        deleted_count += 1
                        logger.debug(f"古いファイルを削除: {file_path}")

                except Exception as e:
                    logger.warning(f"ファイル削除エラー: {file_path}, {e}")
                    continue

            logger.info(f"ディレクトリクリーンアップ完了: {deleted_count} ファイルを削除")
            return deleted_count

        except Exception as e:
            logger.error(f"ディレクトリクリーンアップエラー: {e}")
            return 0


class TempFileManager:
    """一時ファイル管理クラス"""

    def __init__(self, base_dir: Optional[Path] = None):
        """
        初期化

        Args:
            base_dir: 一時ファイルのベースディレクトリ
        """
        self.base_dir = base_dir or Path(tempfile.gettempdir()) / "pdf2pptx_temp"
        self.temp_files: List[Path] = []
        self.temp_dirs: List[Path] = []

        # ベースディレクトリを作成
        self.base_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"一時ファイル管理を初期化: {self.base_dir}")

    def create_temp_file(self, suffix: str = "", prefix: str = "pdf2pptx_") -> Path:
        """
        一時ファイルを作成

        Args:
            suffix: ファイル拡張子
            prefix: ファイル名プレフィックス

        Returns:
            一時ファイルパス
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            filename = f"{prefix}{timestamp}{suffix}"

            temp_file = self.base_dir / filename

            # ファイルを作成
            temp_file.touch()

            # 管理リストに追加
            self.temp_files.append(temp_file)

            logger.debug(f"一時ファイルを作成: {temp_file}")
            return temp_file

        except Exception as e:
            logger.error(f"一時ファイル作成エラー: {e}")
            raise

    def create_temp_directory(self, prefix: str = "pdf2pptx_dir_") -> Path:
        """
        一時ディレクトリを作成

        Args:
            prefix: ディレクトリ名プレフィックス

        Returns:
            一時ディレクトリパス
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            dirname = f"{prefix}{timestamp}"

            temp_dir = self.base_dir / dirname
            temp_dir.mkdir(parents=True, exist_ok=True)

            # 管理リストに追加
            self.temp_dirs.append(temp_dir)

            logger.debug(f"一時ディレクトリを作成: {temp_dir}")
            return temp_dir

        except Exception as e:
            logger.error(f"一時ディレクトリ作成エラー: {e}")
            raise

    def cleanup_temp_files(self) -> None:
        """一時ファイルとディレクトリをクリーンアップ"""
        try:
            # 一時ファイルを削除
            for temp_file in self.temp_files[:]:
                try:
                    if temp_file.exists():
                        temp_file.unlink()
                        logger.debug(f"一時ファイルを削除: {temp_file}")
                    self.temp_files.remove(temp_file)
                except Exception as e:
                    logger.warning(f"一時ファイル削除エラー: {temp_file}, {e}")

            # 一時ディレクトリを削除
            for temp_dir in self.temp_dirs[:]:
                try:
                    if temp_dir.exists():
                        shutil.rmtree(temp_dir)
                        logger.debug(f"一時ディレクトリを削除: {temp_dir}")
                    self.temp_dirs.remove(temp_dir)
                except Exception as e:
                    logger.warning(f"一時ディレクトリ削除エラー: {temp_dir}, {e}")

            logger.info("一時ファイルクリーンアップ完了")

        except Exception as e:
            logger.error(f"一時ファイルクリーンアップエラー: {e}")

    def get_temp_file_info(self) -> Dict[str, Any]:
        """
        一時ファイルの情報を取得

        Returns:
            一時ファイル情報辞書
        """
        try:
            total_size = 0
            valid_files = []
            valid_dirs = []

            # ファイルサイズ計算
            for temp_file in self.temp_files:
                if temp_file.exists():
                    total_size += temp_file.stat().st_size
                    valid_files.append(temp_file)

            # ディレクトリサイズ計算
            for temp_dir in self.temp_dirs:
                if temp_dir.exists():
                    valid_dirs.append(temp_dir)
                    for file_path in temp_dir.rglob("*"):
                        if file_path.is_file():
                            total_size += file_path.stat().st_size

            return {
                "base_directory": str(self.base_dir),
                "temp_files_count": len(valid_files),
                "temp_dirs_count": len(valid_dirs),
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "temp_files": [str(f) for f in valid_files],
                "temp_dirs": [str(d) for d in valid_dirs]
            }

        except Exception as e:
            logger.error(f"一時ファイル情報取得エラー: {e}")
            return {"error": str(e)}

    def __del__(self):
        """デストラクタ - 一時ファイルクリーンアップ"""
        try:
            self.cleanup_temp_files()
        except:
            pass


class FileUtils:
    """ファイルユーティリティメインクラス"""

    def __init__(self, error_handler: Optional[ErrorHandler] = None):
        """
        初期化

        Args:
            error_handler: エラーハンドラーインスタンス
        """
        self.error_handler = error_handler or ErrorHandler()
        self.temp_manager = TempFileManager()

    def copy_file_safely(self,
                        src: Path,
                        dst: Path,
                        overwrite: bool = False,
                        verify_checksum: bool = True) -> bool:
        """
        ファイルを安全にコピー

        Args:
            src: コピー元ファイル
            dst: コピー先ファイル
            overwrite: 上書きを許可するか
            verify_checksum: チェックサム検証するか

        Returns:
            コピー成功時True

        Raises:
            FileNotFoundError: コピー元ファイルが存在しない
            FileExistsError: コピー先ファイルが既に存在（overwrite=False時）
            OSError: コピーエラー
        """
        try:
            if not src.exists():
                raise FileNotFoundError(f"コピー元ファイルが存在しません: {src}")

            if dst.exists() and not overwrite:
                raise FileExistsError(f"コピー先ファイルが既に存在します: {dst}")

            # コピー先ディレクトリを作成
            dst.parent.mkdir(parents=True, exist_ok=True)

            # コピー元のチェックサムを計算
            src_checksum = None
            if verify_checksum:
                src_checksum = self._calculate_file_checksum(src)

            # ファイルコピー実行
            shutil.copy2(src, dst)

            # チェックサム検証
            if verify_checksum and src_checksum:
                dst_checksum = self._calculate_file_checksum(dst)
                if src_checksum != dst_checksum:
                    # コピーしたファイルを削除
                    dst.unlink()
                    raise OSError("ファイルコピー後のチェックサム検証に失敗")

            logger.info(f"ファイルコピー完了: {src} -> {dst}")
            return True

        except Exception as e:
            self.error_handler.handle_error(
                error_type=ErrorType.FILE_ACCESS,
                error=e,
                details={"src": str(src), "dst": str(dst)}
            )
            raise

    def move_file_safely(self, src: Path, dst: Path, overwrite: bool = False) -> bool:
        """
        ファイルを安全に移動

        Args:
            src: 移動元ファイル
            dst: 移動先ファイル
            overwrite: 上書きを許可するか

        Returns:
            移動成功時True
        """
        try:
            if not src.exists():
                raise FileNotFoundError(f"移動元ファイルが存在しません: {src}")

            if dst.exists() and not overwrite:
                raise FileExistsError(f"移動先ファイルが既に存在します: {dst}")

            # 移動先ディレクトリを作成
            dst.parent.mkdir(parents=True, exist_ok=True)

            # ファイル移動実行
            shutil.move(str(src), str(dst))

            logger.info(f"ファイル移動完了: {src} -> {dst}")
            return True

        except Exception as e:
            self.error_handler.handle_error(
                error_type=ErrorType.FILE_ACCESS,
                error=e,
                details={"src": str(src), "dst": str(dst)}
            )
            raise

    def _calculate_file_checksum(self, file_path: Path) -> str:
        """
        ファイルのMD5チェックサムを計算

        Args:
            file_path: ファイルパス

        Returns:
            MD5ハッシュ値
        """
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()

        except Exception as e:
            logger.warning(f"チェックサム計算エラー: {e}")
            return ""

    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        ファイル情報を取得

        Args:
            file_path: ファイルパス

        Returns:
            ファイル情報辞書
        """
        try:
            if not file_path.exists():
                return {"error": "ファイルが存在しません"}

            stat = file_path.stat()

            return {
                "path": str(file_path),
                "name": file_path.name,
                "stem": file_path.stem,
                "suffix": file_path.suffix,
                "size_bytes": stat.st_size,
                "size_mb": stat.st_size / (1024 * 1024),
                "creation_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modification_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "access_time": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "is_file": file_path.is_file(),
                "is_directory": file_path.is_dir(),
                "is_readable": os.access(file_path, os.R_OK),
                "is_writable": os.access(file_path, os.W_OK),
                "parent_directory": str(file_path.parent)
            }

        except Exception as e:
            logger.error(f"ファイル情報取得エラー: {e}")
            return {"error": str(e)}

    def batch_validate_files(self, file_paths: List[Path], file_type: str) -> Dict[str, List[Path]]:
        """
        複数ファイルの一括検証

        Args:
            file_paths: ファイルパスのリスト
            file_type: ファイルタイプ ("pdf", "image", "pptx")

        Returns:
            検証結果辞書 {"valid": [Path], "invalid": [Path]}
        """
        try:
            valid_files = []
            invalid_files = []

            for file_path in file_paths:
                try:
                    if file_type.lower() == "pdf":
                        is_valid = FileValidator.validate_pdf_file(file_path)
                    elif file_type.lower() == "image":
                        is_valid = FileValidator.validate_image_file(file_path)
                    elif file_type.lower() == "pptx":
                        is_valid = file_path.suffix.lower() in FileValidator.SUPPORTED_PPTX_EXTENSIONS
                    else:
                        is_valid = file_path.exists() and file_path.is_file()

                    if is_valid:
                        valid_files.append(file_path)
                    else:
                        invalid_files.append(file_path)

                except Exception as e:
                    logger.warning(f"ファイル検証エラー: {file_path}, {e}")
                    invalid_files.append(file_path)

            logger.info(f"一括ファイル検証完了: {len(valid_files)} 有効, {len(invalid_files)} 無効")

            return {
                "valid": valid_files,
                "invalid": invalid_files,
                "total": len(file_paths),
                "valid_count": len(valid_files),
                "invalid_count": len(invalid_files)
            }

        except Exception as e:
            logger.error(f"一括ファイル検証エラー: {e}")
            return {"valid": [], "invalid": file_paths, "error": str(e)}

    def cleanup_all_temp_files(self) -> None:
        """すべての一時ファイルをクリーンアップ"""
        try:
            self.temp_manager.cleanup_temp_files()
        except Exception as e:
            logger.error(f"一時ファイル総合クリーンアップエラー: {e}")

    def __del__(self):
        """デストラクタ - 一時ファイルクリーンアップ"""
        try:
            self.cleanup_all_temp_files()
        except:
            pass


# シングルトンインスタンス
_file_utils_instance: Optional[FileUtils] = None

def get_file_utils(error_handler: Optional[ErrorHandler] = None) -> FileUtils:
    """
    FileUtilsのシングルトンインスタンスを取得

    Args:
        error_handler: エラーハンドラーインスタンス

    Returns:
        FileUtilsインスタンス
    """
    global _file_utils_instance

    if _file_utils_instance is None:
        _file_utils_instance = FileUtils(error_handler)

    return _file_utils_instance