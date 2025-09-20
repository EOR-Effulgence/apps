"""
コア機能の動作確認テストスクリプト
"""

import sys
import os
# UTF-8出力設定
os.environ['PYTHONIOENCODING'] = 'utf-8'
from pathlib import Path
from loguru import logger

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import ConfigManager
from src.utils.error_handler import ErrorHandler, ErrorType
from src.core.pdf_processor import PDFProcessor, ConversionSettings
from src.utils.file_utils import FileUtils


def test_config_manager():
    """設定管理システムのテスト"""
    print("\n=== 設定管理システムのテスト ===")
    try:
        config = ConfigManager()
        print("[OK] ConfigManager初期化成功")

        # デフォルト設定取得
        default_config = config.get_default_config()
        print(f"[OK] デフォルト設定取得: {len(default_config)} 項目")

        # 設定値の取得テスト
        dpi = config.get_config("conversion.pdf_to_png.dpi")
        print(f"[OK] DPI設定値: {dpi}")

        # 設定の検証
        if config.validate_config():
            print("[OK] 設定検証成功")

        return True

    except Exception as e:
        print(f"[ERROR] エラー: {e}")
        return False


def test_error_handler():
    """エラーハンドリングシステムのテスト"""
    print("\n=== エラーハンドリングシステムのテスト ===")
    try:
        error_handler = ErrorHandler()
        print("[OK] ErrorHandler初期化成功")

        # テストエラーを処理（UIは表示しない）
        error_handler.handle_error(
            error_type=ErrorType.PDF_PROCESSING,
            error=ValueError("テストエラー"),
            details={"test": "データ"},
            show_ui=False
        )
        print("[OK] エラー処理成功")

        # エラー統計取得
        stats = error_handler.get_error_statistics()
        print(f"[OK] エラー統計取得: PDF処理エラー {stats[ErrorType.PDF_PROCESSING]} 件")

        return True

    except Exception as e:
        print(f"[ERROR] エラー: {e}")
        return False


def test_file_utils():
    """ファイルユーティリティのテスト"""
    print("\n=== ファイルユーティリティのテスト ===")
    try:
        file_utils = FileUtils()
        print("[OK] FileUtils初期化成功")

        # テストパス
        test_path = Path("test_file.pdf")

        # ファイル名の安全性チェック
        safe_name = file_utils.get_safe_filename("test:file<>.pdf")
        print(f"[OK] 安全なファイル名生成: {safe_name}")

        # Windows予約語チェック
        safe_name2 = file_utils.get_safe_filename("CON.pdf")
        print(f"[OK] Windows予約語回避: {safe_name2}")

        # 出力ディレクトリ作成テスト
        output_dir = Path("test_output")
        created_dir = file_utils.create_output_directory(output_dir, exist_ok=True)
        print(f"[OK] 出力ディレクトリ作成: {created_dir}")

        # クリーンアップ
        if output_dir.exists():
            output_dir.rmdir()

        return True

    except Exception as e:
        print(f"[ERROR] エラー: {e}")
        return False


def test_pdf_processor():
    """PDF処理エンジンのテスト（PDFファイルが必要）"""
    print("\n=== PDF処理エンジンのテスト ===")
    try:
        config = ConfigManager()
        processor = PDFProcessor(config)
        print("[OK] PDFProcessor初期化成功")

        # デフォルト設定確認
        settings = processor.default_settings
        print(f"[OK] デフォルト設定: DPI={settings.dpi}, Scale={settings.scale}")

        # テストPDFファイルが存在する場合のみ実行
        test_pdf = Path("test.pdf")
        if test_pdf.exists():
            # PDF検証
            is_valid = processor.validate_pdf(test_pdf)
            print(f"[OK] PDF検証: {is_valid}")

            # PDF情報取得
            pdf_info = processor.get_pdf_info(test_pdf)
            if pdf_info:
                print(f"[OK] PDF情報取得: {pdf_info['page_count']} ページ")
        else:
            print("[WARN] test.pdf が見つかりません - スキップ")

        return True

    except Exception as e:
        print(f"[ERROR] エラー: {e}")
        return False


def test_imports():
    """必要なモジュールのインポートテスト"""
    print("\n=== インポートテスト ===")
    try:
        # PowerPoint生成
        from src.core.pptx_generator import PPTXGenerator
        print("[OK] PPTXGeneratorインポート成功")

        # 変換サービス
        from src.core.conversion_service import ConversionService
        print("[OK] ConversionServiceインポート成功")

        return True

    except ImportError as e:
        print(f"[ERROR] インポートエラー: {e}")
        return False


def main():
    """メインテスト実行"""
    print("=" * 50)
    print("PDF2PPTX v3.0 コア機能テスト")
    print("=" * 50)

    results = []

    # 各テストを実行
    results.append(("インポート", test_imports()))
    results.append(("設定管理", test_config_manager()))
    results.append(("エラーハンドリング", test_error_handler()))
    results.append(("ファイルユーティリティ", test_file_utils()))
    results.append(("PDF処理エンジン", test_pdf_processor()))

    # 結果サマリー
    print("\n" + "=" * 50)
    print("テスト結果サマリー")
    print("=" * 50)

    success_count = sum(1 for _, success in results if success)
    total_count = len(results)

    for test_name, success in results:
        status = "[OK] 成功" if success else "[ERROR] 失敗"
        print(f"{test_name}: {status}")

    print(f"\n結果: {success_count}/{total_count} テスト成功")

    if success_count == total_count:
        print("\n[SUCCESS] すべてのテストが成功しました！")
        return 0
    else:
        print(f"\n[WARNING] {total_count - success_count} 個のテストが失敗しました")
        return 1


if __name__ == "__main__":
    sys.exit(main())