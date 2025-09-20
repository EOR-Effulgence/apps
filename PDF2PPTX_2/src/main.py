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
    logger.add("logs/app.log", rotation="10 MB", level="DEBUG")

def main():
    """アプリケーションのメインエントリーポイント"""
    setup_logging()
    logger.info("PDF2PPTX v3.0 起動")

    try:
        from PySide6.QtWidgets import QApplication
        from src.ui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setApplicationName("PDF2PPTX")
        app.setOrganizationName("PDF2PPTX")

        window = MainWindow()
        window.show()

        sys.exit(app.exec())

    except ImportError as e:
        logger.error(f"必要なモジュールのインポートに失敗: {e}")
        logger.info("GUI開発モード - UIコンポーネントは作成中です")
        return 1
    except Exception as e:
        logger.exception(f"予期しないエラー: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())