"""
PowerPoint変換のデバッグテスト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPATHに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from core.pptx_generator import PPTXGenerator, LabelStyle, LabelPosition
from core.pdf_processor import PDFProcessor
from utils.config import ConfigManager
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def debug_conversion():
    """デバッグ用変換処理"""
    print("=== PowerPoint変換デバッグテスト ===")

    try:
        # 設定を読み込み
        config = ConfigManager()

        # PDFファイルパス
        pdf_path = Path('Input/大漢和辞典序文.pdf')
        if not pdf_path.exists():
            print(f"PDFファイルが見つかりません: {pdf_path}")
            return

        print(f"PDFファイル: {pdf_path}")

        # 一時ディレクトリを作成
        temp_dir = Path('temp')
        temp_dir.mkdir(exist_ok=True)

        # PDFを処理
        print("PDFを画像に変換中...")
        pdf_processor = PDFProcessor()
        images = pdf_processor.process_pdf(pdf_path, temp_dir)
        print(f'PDF処理完了: {len(images)}ページ')

        # ラベルスタイルを設定（TOP_LEFT座標0,0配置）
        label_style = LabelStyle(
            position=LabelPosition.TOP_LEFT,
            font_name="メイリオ",
            font_size=14,
            text_color="#FFFFFF",
            background_color="#1976D2",
            add_filename=True,
            add_page_numbers=True,
            margin_mm=5
        )

        # PowerPoint生成
        print("PowerPoint生成中...")
        pptx_gen = PPTXGenerator()
        output_path = Path('Output/debug_test.pptx')
        output_path.parent.mkdir(exist_ok=True)

        pptx_gen.create_presentation(
            image_paths=images,
            output_path=output_path,
            label_style=label_style
        )

        print(f'PowerPoint生成完了: {output_path}')

        # 出力ファイルのサイズ確認
        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f'ファイルサイズ: {file_size:,} bytes')

    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_conversion()