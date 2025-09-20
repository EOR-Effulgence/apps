"""
エラーハンドリングシステム
統一的なエラー処理とユーザー向けメッセージ表示
"""

import sys
import traceback
from typing import Optional, Dict, Any, Callable
from enum import Enum
from pathlib import Path
from datetime import datetime
from loguru import logger

class ErrorLevel(Enum):
    """エラーレベル定義"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorType(Enum):
    """エラータイプ定義"""
    FILE_NOT_FOUND = "file_not_found"
    FILE_ACCESS = "file_access"
    PDF_PROCESSING = "pdf_processing"
    PPTX_GENERATION = "pptx_generation"
    INVALID_INPUT = "invalid_input"
    MEMORY_ERROR = "memory_error"
    CONVERSION_ERROR = "conversion_error"
    CONFIG_ERROR = "config_error"
    NETWORK_ERROR = "network_error"
    UNKNOWN = "unknown"

class ErrorHandler:
    """エラーハンドリングクラス"""

    # エラーメッセージテンプレート（日本語）
    ERROR_MESSAGES = {
        ErrorType.FILE_NOT_FOUND: {
            "title": "ファイルが見つかりません",
            "message": "指定されたファイル '{file}' が見つかりません。",
            "suggestion": "ファイルパスを確認してください。"
        },
        ErrorType.FILE_ACCESS: {
            "title": "ファイルアクセスエラー",
            "message": "ファイル '{file}' にアクセスできません。",
            "suggestion": "ファイルが使用中でないか、アクセス権限を確認してください。"
        },
        ErrorType.PDF_PROCESSING: {
            "title": "PDF処理エラー",
            "message": "PDFファイルの処理中にエラーが発生しました。",
            "suggestion": "PDFファイルが破損していないか確認してください。"
        },
        ErrorType.PPTX_GENERATION: {
            "title": "PowerPoint生成エラー",
            "message": "PowerPointファイルの生成中にエラーが発生しました。",
            "suggestion": "出力先ディレクトリの空き容量を確認してください。"
        },
        ErrorType.INVALID_INPUT: {
            "title": "入力エラー",
            "message": "入力値が正しくありません: {details}",
            "suggestion": "入力内容を確認して再度お試しください。"
        },
        ErrorType.MEMORY_ERROR: {
            "title": "メモリ不足",
            "message": "処理に必要なメモリが不足しています。",
            "suggestion": "他のアプリケーションを終了するか、処理するファイル数を減らしてください。"
        },
        ErrorType.CONVERSION_ERROR: {
            "title": "変換エラー",
            "message": "ファイルの変換中にエラーが発生しました。",
            "suggestion": "ファイル形式を確認するか、設定を見直してください。"
        },
        ErrorType.CONFIG_ERROR: {
            "title": "設定エラー",
            "message": "設定ファイルの読み込みまたは保存に失敗しました。",
            "suggestion": "設定をリセットするか、管理者に連絡してください。"
        },
        ErrorType.NETWORK_ERROR: {
            "title": "ネットワークエラー",
            "message": "ネットワーク接続に問題があります。",
            "suggestion": "インターネット接続を確認してください。"
        },
        ErrorType.UNKNOWN: {
            "title": "予期しないエラー",
            "message": "予期しないエラーが発生しました。",
            "suggestion": "アプリケーションを再起動してください。問題が続く場合は管理者に連絡してください。"
        }
    }

    def __init__(self, ui_callback: Optional[Callable] = None):
        """
        初期化

        Args:
            ui_callback: UI表示用のコールバック関数
        """
        self.ui_callback = ui_callback
        self.error_log_path = Path("logs") / "errors.log"
        self.error_count = {error_type: 0 for error_type in ErrorType}
        self._ensure_log_directory()

    def _ensure_log_directory(self):
        """ログディレクトリを確認・作成"""
        self.error_log_path.parent.mkdir(parents=True, exist_ok=True)

    def handle_error(self,
                    error_type: ErrorType,
                    error: Optional[Exception] = None,
                    details: Optional[Dict[str, Any]] = None,
                    show_ui: bool = True) -> None:
        """
        エラーを処理

        Args:
            error_type: エラータイプ
            error: 例外オブジェクト
            details: 追加詳細情報
            show_ui: UIにメッセージを表示するか
        """
        # エラーカウントを更新
        self.error_count[error_type] += 1

        # エラー情報を構築
        error_info = self._build_error_info(error_type, error, details)

        # ログに記録
        self.log_error(error_info, error)

        # UIに表示
        if show_ui:
            self.show_user_message(error_info, ErrorLevel.ERROR)

    def _build_error_info(self,
                         error_type: ErrorType,
                         error: Optional[Exception],
                         details: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """
        エラー情報を構築

        Args:
            error_type: エラータイプ
            error: 例外オブジェクト
            details: 追加詳細情報

        Returns:
            エラー情報辞書
        """
        template = self.ERROR_MESSAGES.get(error_type, self.ERROR_MESSAGES[ErrorType.UNKNOWN])

        # デフォルト値
        error_info = {
            "title": template["title"],
            "message": template["message"],
            "suggestion": template["suggestion"],
            "timestamp": datetime.now().isoformat()
        }

        # 詳細情報で置換
        if details:
            for key, value in details.items():
                error_info["message"] = error_info["message"].replace(f"{{{key}}}", str(value))

        # エラーオブジェクトから追加情報
        if error:
            error_info["error_class"] = error.__class__.__name__
            error_info["error_message"] = str(error)

        return error_info

    def log_error(self, error_info: Dict[str, str], error: Optional[Exception] = None) -> None:
        """
        エラーをログに記録

        Args:
            error_info: エラー情報
            error: 例外オブジェクト
        """
        log_message = f"[{error_info['timestamp']}] {error_info['title']}: {error_info['message']}"

        if error:
            # 詳細なエラー情報をログに記録
            logger.error(log_message)
            logger.debug(f"Error class: {error.__class__.__name__}")
            logger.debug(f"Error details: {str(error)}")

            # トレースバック情報も記録
            tb_str = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
            logger.debug(f"Traceback:\n{tb_str}")
        else:
            logger.error(log_message)

        # ファイルにも記録
        try:
            with open(self.error_log_path, 'a', encoding='utf-8') as f:
                f.write(f"{log_message}\n")
                if error:
                    f.write(f"Details: {str(error)}\n")
                f.write("-" * 80 + "\n")
        except Exception as e:
            logger.warning(f"エラーログファイルへの書き込み失敗: {e}")

    def show_user_message(self,
                         message_info: Dict[str, str],
                         level: ErrorLevel = ErrorLevel.INFO) -> None:
        """
        ユーザー向けメッセージを表示

        Args:
            message_info: メッセージ情報
            level: メッセージレベル
        """
        if self.ui_callback:
            # UIコールバックが設定されている場合
            try:
                self.ui_callback(message_info, level)
            except Exception as e:
                logger.error(f"UIコールバックの実行に失敗: {e}")
                self._show_console_message(message_info, level)
        else:
            # コンソールに表示
            self._show_console_message(message_info, level)

    def _show_console_message(self,
                             message_info: Dict[str, str],
                             level: ErrorLevel) -> None:
        """
        コンソールにメッセージを表示

        Args:
            message_info: メッセージ情報
            level: メッセージレベル
        """
        level_symbols = {
            ErrorLevel.DEBUG: "[DEBUG]",
            ErrorLevel.INFO: "[INFO]",
            ErrorLevel.WARNING: "[警告]",
            ErrorLevel.ERROR: "[エラー]",
            ErrorLevel.CRITICAL: "[重大]"
        }

        symbol = level_symbols.get(level, "[INFO]")
        print(f"\n{symbol} {message_info['title']}")
        print(f"  {message_info['message']}")
        if 'suggestion' in message_info:
            print(f"  💡 {message_info['suggestion']}")
        print()

    def handle_exception(self, exc_type, exc_value, exc_traceback) -> None:
        """
        未処理の例外をキャッチして処理

        Args:
            exc_type: 例外タイプ
            exc_value: 例外値
            exc_traceback: トレースバック
        """
        # KeyboardInterruptは通常通り処理
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # エラータイプを判定
        error_type = self._determine_error_type(exc_value)

        # エラー処理
        self.handle_error(
            error_type=error_type,
            error=exc_value,
            show_ui=True
        )

    def _determine_error_type(self, error: Exception) -> ErrorType:
        """
        例外からエラータイプを判定

        Args:
            error: 例外オブジェクト

        Returns:
            エラータイプ
        """
        error_class_name = error.__class__.__name__
        error_message = str(error).lower()

        # ファイル関連エラー
        if isinstance(error, FileNotFoundError):
            return ErrorType.FILE_NOT_FOUND
        elif isinstance(error, PermissionError):
            return ErrorType.FILE_ACCESS
        elif isinstance(error, IOError):
            return ErrorType.FILE_ACCESS

        # メモリエラー
        elif isinstance(error, MemoryError):
            return ErrorType.MEMORY_ERROR

        # メッセージベースの判定
        elif "pdf" in error_message:
            return ErrorType.PDF_PROCESSING
        elif "pptx" in error_message or "powerpoint" in error_message:
            return ErrorType.PPTX_GENERATION
        elif "config" in error_message:
            return ErrorType.CONFIG_ERROR
        elif "network" in error_message or "connection" in error_message:
            return ErrorType.NETWORK_ERROR
        elif "invalid" in error_message or "validation" in error_message:
            return ErrorType.INVALID_INPUT

        # その他
        else:
            return ErrorType.UNKNOWN

    def get_error_statistics(self) -> Dict[ErrorType, int]:
        """
        エラー統計を取得

        Returns:
            エラータイプごとの発生回数
        """
        return self.error_count.copy()

    def reset_error_statistics(self) -> None:
        """エラー統計をリセット"""
        self.error_count = {error_type: 0 for error_type in ErrorType}

    def install_global_handler(self) -> None:
        """グローバル例外ハンドラーをインストール"""
        sys.excepthook = self.handle_exception
        logger.info("グローバルエラーハンドラーをインストールしました")


# シングルトンインスタンス
_error_handler_instance: Optional[ErrorHandler] = None

def get_error_handler(ui_callback: Optional[Callable] = None) -> ErrorHandler:
    """
    エラーハンドラーのシングルトンインスタンスを取得

    Args:
        ui_callback: UI表示用のコールバック関数

    Returns:
        ErrorHandlerインスタンス
    """
    global _error_handler_instance

    if _error_handler_instance is None:
        _error_handler_instance = ErrorHandler(ui_callback)
        _error_handler_instance.install_global_handler()
    elif ui_callback:
        # UIコールバックを更新
        _error_handler_instance.ui_callback = ui_callback

    return _error_handler_instance