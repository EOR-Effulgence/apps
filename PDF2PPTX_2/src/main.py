"""
PDF2PPTX v3.0 - メインエントリーポイント
PDF→PNG変換およびPowerPoint生成ツール
"""

import sys
import os
from pathlib import Path
from loguru import logger

def setup_logging():
    """ロギングの設定"""
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")

    # ログディレクトリ作成
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    logger.add(log_dir / "app.log", rotation="10 MB", level="DEBUG")

def main():
    """アプリケーションのメインエントリーポイント"""
    setup_logging()
    logger.info("PDF2PPTX v3.0 起動")

    try:
        import tkinter as tk
        import customtkinter as ctk
        from src.gui.main_window import MainWindow

        # CustomTkinter設定
        ctk.set_appearance_mode("system")  # システムテーマ追従
        ctk.set_default_color_theme("blue")  # デフォルトカラーテーマ

        # アプリケーション起動
        app = MainWindow()
        app.mainloop()

    except ImportError as e:
        logger.error(f"必要なモジュールのインポートに失敗: {e}")
        logger.info("GUI開発モード - UIコンポーネントは作成中です")
        return 1
    except Exception as e:
        logger.exception(f"予期しないエラー: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())