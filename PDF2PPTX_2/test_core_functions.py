"""
コア機能のテストスクリプト
実装されたPDF処理エンジン、PowerPoint生成エンジン、ファイルユーティリティの動作確認
"""

import sys
import os
from pathlib import Path

# プロジェクトのsrcディレクトリをPythonパスに追加
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from loguru import logger
from src.utils.config import ConfigManager
from src.utils.error_handler import ErrorHandler, get_error_handler
from src.utils.file_utils import FileValidator, SafeFilename, DirectoryManager, get_file_utils
from src.core.pdf_processor import PDFProcessor, ConversionSettings, RotationMode, ImageFormat
from src.core.pptx_generator import PPTXGenerator, SlideSettings, LabelStyle, ImageSettings
from src.core.conversion_service import ConversionService, ConversionType, create_optimized_pdf_settings, create_standard_pptx_settings


def test_config_manager():
    """設定管理システムのテスト"""
    print("=" * 60)
    print("設定管理システムのテスト")
    print("=" * 60)

    try:
        config = ConfigManager()

        # デフォルト設定の表示
        print("✓ ConfigManager初期化成功")

        # PDF変換設定の取得
        pdf_config = config.get_config("conversion.pdf_to_png")
        print(f"✓ PDF変換設定: DPI={pdf_config.get('dpi')}, スケール={pdf_config.get('scale')}")

        # PowerPoint設定の取得
        pptx_config = config.get_config("conversion.pdf_to_pptx")
        print(f"✓ PowerPoint設定: スライドサイズ={pptx_config.get('slide_size')}")

        # 設定値の更新テスト
        config.set_config("test.value", "テスト値", save=False)
        test_value = config.get_config("test.value")
        print(f"✓ 設定値更新テスト: {test_value}")

        return True

    except Exception as e:
        print(f"✗ 設定管理システムエラー: {e}")
        return False


def test_error_handler():
    """エラーハンドリングシステムのテスト"""
    print("\n" + "=" * 60)
    print("エラーハンドリングシステムのテスト")
    print("=" * 60)

    try:
        error_handler = get_error_handler()
        print("✓ ErrorHandler初期化成功")

        # エラー統計をリセット
        error_handler.reset_error_statistics()

        # テスト用エラーの発生
        from src.utils.error_handler import ErrorType
        error_handler.handle_error(
            error_type=ErrorType.PDF_PROCESSING,
            details={"file": "test.pdf"},
            show_ui=False
        )

        # エラー統計の確認
        stats = error_handler.get_error_statistics()
        print(f"✓ エラー統計取得: PDF処理エラー {stats[ErrorType.PDF_PROCESSING]} 件")

        return True

    except Exception as e:
        print(f"✗ エラーハンドリングシステムエラー: {e}")
        return False


def test_file_utils():
    """ファイルユーティリティのテスト"""
    print("\n" + "=" * 60)
    print("ファイルユーティリティのテスト")
    print("=" * 60)

    try:
        # ファイル名検証テスト
        test_filenames = [
            "正常なファイル名.pdf",
            "con.pdf",  # Windows予約語
            "ファイル名<>無効文字.pdf",  # 無効文字
            "a" * 300 + ".pdf",  # 長すぎるファイル名
            "normal_file.pdf"
        ]

        print("ファイル名検証テスト:")
        for filename in test_filenames:
            is_valid = FileValidator.validate_filename(filename)
            status = "✓" if is_valid else "✗"
            print(f"  {status} {filename[:50]}{'...' if len(filename) > 50 else ''}: {is_valid}")

        # 安全なファイル名生成テスト
        print("\n安全なファイル名生成テスト:")
        unsafe_names = ["con.pdf", "file<>name.pdf", "  spaced  .pdf"]
        for unsafe_name in unsafe_names:
            safe_name = SafeFilename.sanitize_filename(unsafe_name)
            print(f"  ✓ '{unsafe_name}' → '{safe_name}'")

        # ディレクトリ管理テスト
        test_dir = project_root / "test_output"
        source_file = project_root / "test.pdf"

        output_dir = DirectoryManager.create_output_directory(
            test_dir, source_file, create_subfolder=True
        )
        print(f"✓ 出力ディレクトリ作成: {output_dir}")

        # 使用可能容量チェック
        available_space = DirectoryManager.get_available_space(project_root)
        available_gb = available_space / (1024**3)
        print(f"✓ 使用可能容量: {available_gb:.1f} GB")

        return True

    except Exception as e:
        print(f"✗ ファイルユーティリティエラー: {e}")
        return False


def test_pdf_processor():
    """PDF処理エンジンのテスト"""
    print("\n" + "=" * 60)
    print("PDF処理エンジンのテスト")
    print("=" * 60)

    try:
        config = ConfigManager()
        error_handler = get_error_handler()
        pdf_processor = PDFProcessor(config, error_handler)
        print("✓ PDFProcessor初期化成功")

        # 変換設定のテスト
        settings = ConversionSettings(
            dpi=150,
            scale=1.5,
            rotation_mode=RotationMode.AUTO,
            output_format=ImageFormat.PNG
        )
        print(f"✓ 変換設定作成: DPI={settings.dpi}, スケール={settings.scale}")

        # ファイル検証テスト（実際のPDFファイルがない場合）
        test_pdf = project_root / "sample.pdf"
        if test_pdf.exists():
            is_valid = pdf_processor.validate_pdf_file(test_pdf)
            print(f"✓ PDFファイル検証: {test_pdf} - {is_valid}")

            if is_valid:
                pdf_info = pdf_processor.get_pdf_info(test_pdf)
                print(f"✓ PDF情報取得: {pdf_info['page_count']} ページ")
        else:
            print("⚠ テスト用PDFファイルが見つかりません (sample.pdf)")

        # 最適化設定のテスト
        optimized_settings = create_optimized_pdf_settings("presentation")
        print(f"✓ 最適化設定（プレゼンテーション用）: DPI={optimized_settings.dpi}")

        return True

    except Exception as e:
        print(f"✗ PDF処理エンジンエラー: {e}")
        return False


def test_pptx_generator():
    """PowerPoint生成エンジンのテスト"""
    print("\n" + "=" * 60)
    print("PowerPoint生成エンジンのテスト")
    print("=" * 60)

    try:
        config = ConfigManager()
        error_handler = get_error_handler()
        pptx_generator = PPTXGenerator(config, error_handler)
        print("✓ PPTXGenerator初期化成功")

        # 標準設定のテスト
        slide_settings, label_style, image_settings = create_standard_pptx_settings()
        print(f"✓ スライド設定: {slide_settings.width_mm}×{slide_settings.height_mm}mm")
        print(f"✓ ラベル設定: フォント={label_style.font_name}, サイズ={label_style.font_size}")
        print(f"✓ 画像設定: 最大幅={image_settings.max_width_percent}%")

        # プレゼンテーション作成テスト
        prs = pptx_generator.create_presentation(slide_settings)
        print(f"✓ プレゼンテーション作成: スライドサイズ {prs.slide_width/36000:.0f}×{prs.slide_height/36000:.0f}mm")

        # テスト用PowerPointファイル保存
        test_output = project_root / "test_presentation.pptx"
        success = pptx_generator.save_presentation(prs, test_output, overwrite=True)
        if success:
            print(f"✓ テストプレゼンテーション保存: {test_output}")

            # ファイル情報取得
            pptx_info = pptx_generator.get_presentation_info(test_output)
            print(f"✓ PowerPoint情報: {pptx_info['slide_count']} スライド, {pptx_info['file_size_mb']:.1f}MB")

        return True

    except Exception as e:
        print(f"✗ PowerPoint生成エンジンエラー: {e}")
        return False


def test_conversion_service():
    """変換サービス統合のテスト"""
    print("\n" + "=" * 60)
    print("変換サービス統合のテスト")
    print("=" * 60)

    try:
        config = ConfigManager()
        error_handler = get_error_handler()
        file_utils = get_file_utils(error_handler)

        conversion_service = ConversionService(config, error_handler, file_utils)
        print("✓ ConversionService初期化成功")

        # 進捗コールバックのテスト
        def progress_callback(progress):
            print(f"  進捗: {progress.status.value} - {progress.status_message}")

        conversion_service.set_progress_callback(progress_callback)
        print("✓ 進捗コールバック設定")

        # テスト用画像ファイルのPowerPoint変換（画像ファイルがある場合）
        test_images_dir = project_root / "test_images"
        if test_images_dir.exists():
            image_files = list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg"))
            if image_files:
                output_path = project_root / "test_images_to_pptx.pptx"

                result = conversion_service.convert_images_to_pptx(
                    image_files, output_path, title="テスト画像プレゼンテーション"
                )

                if result.success:
                    print(f"✓ 画像→PowerPoint変換成功: {result.total_pages_processed} ページ")
                    print(f"  処理時間: {result.processing_time_seconds:.1f}秒")
                    print(f"  出力サイズ: {result.file_size_mb:.1f}MB")
                else:
                    print(f"✗ 画像→PowerPoint変換失敗: {result.error_message}")
            else:
                print("⚠ テスト用画像ファイルが見つかりません")
        else:
            print("⚠ テスト用画像ディレクトリが見つかりません (test_images/)")

        # 統計情報のテスト
        dummy_results = []
        stats = conversion_service.get_conversion_statistics(dummy_results)
        print(f"✓ 統計情報取得機能: {type(stats)}")

        return True

    except Exception as e:
        print(f"✗ 変換サービス統合エラー: {e}")
        return False


def create_test_environment():
    """テスト環境の準備"""
    print("=" * 60)
    print("テスト環境の準備")
    print("=" * 60)

    # ログ設定
    logger.remove()  # デフォルトハンドラーを削除
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )

    # テストディレクトリ作成
    test_dirs = ["test_output", "test_images", "logs"]
    for dir_name in test_dirs:
        test_dir = project_root / dir_name
        test_dir.mkdir(exist_ok=True)

    print("✓ テスト環境準備完了")


def main():
    """メインテスト実行"""
    print("PDF2PPTX v3.0 コア機能テスト")
    print(f"プロジェクトディレクトリ: {project_root}")

    # テスト環境準備
    create_test_environment()

    # 各機能のテスト実行
    test_results = []

    test_functions = [
        ("設定管理システム", test_config_manager),
        ("エラーハンドリングシステム", test_error_handler),
        ("ファイルユーティリティ", test_file_utils),
        ("PDF処理エンジン", test_pdf_processor),
        ("PowerPoint生成エンジン", test_pptx_generator),
        ("変換サービス統合", test_conversion_service),
    ]

    for test_name, test_func in test_functions:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name}で予期しないエラー: {e}")
            test_results.append((test_name, False))

    # テスト結果サマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\n合計: {passed + failed} テスト")
    print(f"成功: {passed}")
    print(f"失敗: {failed}")

    if failed == 0:
        print("\n🎉 全てのテストが成功しました！")
        print("PDF2PPTX v3.0のコア機能が正常に実装されています。")
    else:
        print(f"\n⚠ {failed} 個のテストが失敗しました。")
        print("詳細なエラー情報を確認して修正してください。")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)