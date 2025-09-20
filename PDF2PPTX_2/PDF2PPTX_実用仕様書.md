# PDF2PNG/PDF2PPTX Converter v3.0 - 実用仕様書

**Windows 11標準環境での確実動作を重視した実用的な設計**

---

## 📋 目次

1. [プロジェクト概要](#1-プロジェクト概要)
2. [技術仕様（Windows 11最適化）](#2-技術仕様windows-11最適化)
3. [アーキテクチャ設計](#3-アーキテクチャ設計)
4. [UI設計（実用重視）](#4-ui設計実用重視)
5. [機能仕様](#5-機能仕様)
6. [開発・運用ガイド](#6-開発運用ガイド)
7. [パフォーマンス要件](#7-パフォーマンス要件)

---

## 1. プロジェクト概要

### 1.1 ソフトウェア目的
PDFファイルをPNG画像またはPowerPointプレゼンテーション（PPTX）に変換する、Windows 11環境で確実に動作するデスクトップアプリケーション。

### 1.2 設計方針
- **安定性最優先**: Windows 11標準環境での確実な動作
- **シンプル操作**: 複雑な機能よりも確実性と使いやすさ
- **軽量設計**: 最小限の依存関係で最大の効果
- **保守性**: メンテナンスしやすいコード構造

### 1.3 対象ユーザー
- ビジネスユーザー（資料作成）
- 教育関係者（授業資料）
- 個人ユーザー（文書変換）

---

## 2. 技術仕様（Windows 11最適化）

### 2.1 コア技術スタック

#### 推奨構成（安定性重視）
```yaml
言語: Python 3.11+ (Windows Store版対応)
GUI: tkinter + customtkinter (標準ライブラリ + 安定ライブラリ)
PDF処理: PyMuPDF (fitz) - 最新安定版
PowerPoint: python-pptx - 実績のある安定版
画像処理: Pillow - Windows 11完全対応版
```

#### 依存関係（最小限構成）
```txt
# 必須ライブラリ（最小限）
PyMuPDF>=1.23.0,<1.24.0      # PDF処理（安定版範囲指定）
python-pptx>=0.6.21,<0.7.0   # PowerPoint生成（安定版）
Pillow>=10.0.0,<11.0.0        # 画像処理（Windows 11対応）
customtkinter>=5.0.0,<6.0.0   # モダンtkinter（安定版）

# 開発ツール
pytest>=7.0.0               # テスト
black>=22.0.0               # フォーマッタ
mypy>=1.0.0                # 型チェック
```

### 2.2 Windows 11 特化対応

#### システム統合
- **Windows 11 テーマ対応**: システムの明/暗テーマ自動切替
- **DPI スケーリング対応**: 高解像度ディスプレイ完全サポート
- **ファイル関連付け**: PDF右クリックメニューからの起動
- **通知システム**: Windows 11通知での処理完了報告

#### パフォーマンス最適化
```python
# Windows 11最適化設定
WINDOWS_11_CONFIG = {
    'dpi_awareness': 'system_aware',
    'theme_follow': True,
    'file_dialog': 'native_windows',
    'threading': 'windows_optimized',
    'memory_management': 'conservative'
}
```

---

## 3. アーキテクチャ設計

### 3.1 シンプルMVP構成

```
src/
├── main.py                 # アプリケーション起動点
├── core/
│   ├── pdf_processor.py    # PDF処理コア
│   └── pptx_generator.py   # PowerPoint生成
├── gui/
│   ├── main_window.py      # メインウィンドウ
│   ├── components.py       # UI部品
│   └── theme.py           # テーマ管理
├── utils/
│   ├── config.py          # 設定管理
│   ├── file_utils.py      # ファイル操作
│   └── error_handler.py   # エラー処理
└── tests/                 # テストコード
```

### 3.2 処理フロー（簡潔化）

```
1. ファイル選択 → 2. 設定確認 → 3. 変換実行 → 4. 結果表示
```

---

## 4. UI設計（実用重視）

### 4.1 メインウィンドウレイアウト

```
┌──────────────────────────────────────────────┐
│ PDF2PNG/PDF2PPTX Converter v3.0    [設定] │ ← シンプルヘッダー
├──────────────────────────────────────────────┤
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │     📁 PDFファイルをドロップ        │   │ ← 大きなドロップゾーン
│  │     または [ファイル選択] ボタン     │   │
│  └─────────────────────────────────────┘   │
│                                              │
│  ┌── 変換設定 ────────────────────────┐   │
│  │ 形式: ◉ PNG画像  ○ PowerPoint      │   │ ← 明確な選択肢
│  │ 品質: [高品質 ▼]                   │   │
│  │ 出力先: [元ファイルと同じ場所 ▼]    │   │
│  └──────────────────────────────────┘   │
│                                              │
│     [🔄 変換開始]    [📁 出力フォルダを開く] │ ← 大きなボタン
│                                              │
│  ┌─ 進捗 ──────────────────────────┐     │
│  │ ████████████░░░░ 75% (3/4)        │     │ ← シンプル進捗表示
│  └────────────────────────────────┘     │
├──────────────────────────────────────────────┤
│ 状態: 待機中 | 最終更新: なし | v3.0      │ ← ステータスバー
└──────────────────────────────────────────────┘
```

### 4.2 Windows 11 デザイン準拠

#### カラーテーマ
```python
# Windows 11 テーマ対応
THEME_COLORS = {
    'light': {
        'background': '#F3F3F3',    # Windows 11 Light
        'surface': '#FFFFFF',
        'primary': '#0078D4',       # Windows Blue
        'text': '#323130'
    },
    'dark': {
        'background': '#202020',    # Windows 11 Dark
        'surface': '#2D2D2D',
        'primary': '#60A5FA',       # Bright Blue
        'text': '#FFFFFF'
    }
}
```

#### UI コンポーネント
- **角丸デザイン**: Windows 11の Fluent Design準拠
- **明確なボタン**: 操作がわかりやすい大きめサイズ
- **ネイティブダイアログ**: Windowsファイルダイアログ使用
- **システム統合**: タスクバー進捗表示

---

## 5. 機能仕様

### 5.1 PDF → PNG 変換

#### 基本機能
```python
class PDFtoPNG:
    def convert(self, pdf_path: Path, output_dir: Path,
                dpi: int = 150, quality: str = 'high') -> List[Path]:
        """シンプルで確実なPDF→PNG変換"""

        # 基本設定のみ提供
        settings = {
            'dpi': dpi,              # 150/300 DPI選択
            'format': 'PNG',
            'auto_rotate': True,     # A4縦→横自動回転
            'quality': quality       # 高/中/低
        }

        return self._process_pdf(pdf_path, settings)
```

#### 出力仕様
- **ファイル名**: `元ファイル名_ページ番号.png`
- **DPI**: 150（標準）/ 300（高品質）
- **形式**: PNG（最も互換性が高い）

### 5.2 PDF → PowerPoint 変換

#### 基本機能
```python
class PDFtoPPTX:
    def convert(self, pdf_path: Path, output_path: Path) -> Path:
        """A3横スライドのシンプル生成"""

        pptx_config = {
            'slide_size': (297, 420),  # A3横（mm）
            'layout': 'image_only',    # 画像のみレイアウト
            'image_fit': 'contain',    # 画像を枠内に収める
            'background': 'white'      # 白背景
        }

        return self._generate_pptx(pdf_path, pptx_config)
```

#### 出力仕様
- **スライドサイズ**: A3横（420×297mm）
- **レイアウト**: 各ページを1スライドに配置
- **ファイル名**: `元ファイル名_slides.pptx`

### 5.3 バッチ処理

- **複数PDF**: フォルダ内のPDFファイル一括処理
- **進捗表示**: リアルタイム進捗とキャンセル機能
- **エラー処理**: 失敗ファイルをスキップして継続

---

## 6. 開発・運用ガイド

### 6.1 開発環境セットアップ

#### Windows 11での環境構築
```bash
# 1. Python 3.11+ インストール（Microsoft Store推奨）
# Microsoft Store → Python 3.11

# 2. プロジェクトセットアップ
git clone <repository>
cd PDF2PPTX_2

# 3. 仮想環境（Windows 11最適化）
python -m venv venv
venv\Scripts\activate

# 4. 依存関係インストール
pip install -r requirements.txt

# 5. 開発ツール
pip install -r requirements-dev.txt
```

### 6.2 ビルド・配布

#### EXE作成（PyInstaller）
```bash
# Windows 11用最適化ビルド
pyinstaller --onefile --windowed ^
  --add-data "assets;assets" ^
  --icon="icon.ico" ^
  --name="PDF2PPTX_Converter" ^
  main.py

# 出力: dist/PDF2PPTX_Converter.exe
```

#### Windows 11配布パッケージ
```
PDF2PNG_PPTX_v3.0_Windows11/
├── PDF2PPTX_Converter.exe     # メイン実行ファイル
├── README.txt                 # 使い方説明
├── samples/                   # サンプルファイル
└── uninstall.bat             # アンインストール
```

### 6.3 テスト戦略

#### 重要テスト項目
```python
# Windows 11環境テスト
def test_windows11_compatibility():
    """Windows 11特有機能のテスト"""
    # DPIスケーリング
    # ダークモード切替
    # ファイル関連付け
    # 通知システム
    pass

def test_core_conversion():
    """基本変換機能テスト"""
    # PDF→PNG変換
    # PDF→PPTX変換
    # エラーハンドリング
    pass
```

---

## 7. パフォーマンス要件

### 7.1 性能目標（Windows 11基準）

#### 処理性能
- **変換速度**: A4ページを1秒以内
- **メモリ使用量**: 500MB以下（通常使用）
- **起動時間**: 2秒以内
- **ファイルサイズ**: 500MB PDFまで対応

#### UI応答性
- **操作反応**: 100ms以内
- **進捗更新**: 250ms間隔
- **ファイルドロップ**: 即座の視覚フィードバック

### 7.2 リソース管理

#### メモリ効率化
```python
def efficient_processing():
    """メモリ効率的な処理"""
    # ページ単位処理（一度に全ページ読み込まない）
    # 一時ファイル管理
    # ガベージコレクション制御
    pass
```

#### Windows 11最適化
- **ネイティブAPI活用**: Windows API使用でパフォーマンス向上
- **GPU活用**: Windows 11のハードウェア加速活用
- **バックグラウンド処理**: Windows タスクスケジューラ統合

---

## 8. 設定・カスタマイズ

### 8.1 基本設定

#### 設定ファイル（JSON）
```json
{
  "app": {
    "theme": "auto",
    "language": "ja",
    "auto_open_result": true
  },
  "conversion": {
    "default_dpi": 150,
    "default_quality": "high",
    "auto_rotate": true,
    "batch_processing": true
  },
  "output": {
    "same_directory": true,
    "create_subfolder": false,
    "overwrite_existing": "ask"
  }
}
```

### 8.2 Windows 11統合

#### システム設定
- **ファイル関連付け**: PDF右クリック → PDF2PPTX で変換
- **送る】メニュー**: PDF選択 → 送る → PDF2PPTX
- **通知設定**: 変換完了をWindows通知で表示

---

## 9. エラー処理・サポート

### 9.1 エラーハンドリング

#### 一般的なエラー対応
```python
class ErrorHandler:
    """Windows 11環境でのエラー処理"""

    COMMON_ERRORS = {
        'pdf_corrupt': 'PDFファイルが破損しています',
        'memory_insufficient': 'メモリが不足しています',
        'permission_denied': 'ファイルアクセス権限がありません',
        'disk_full': 'ディスク容量が不足しています'
    }

    def handle_error(self, error_type: str, details: str):
        """わかりやすいエラーメッセージ表示"""
        pass
```

### 9.2 ログ・診断

#### ログ出力
- **場所**: `%APPDATA%/PDF2PPTX/logs/`
- **レベル**: INFO（通常）/ DEBUG（詳細）
- **ローテーション**: 10MB×5ファイル
- **プライバシー**: 個人情報は記録しない

---

## 10. まとめ

この実用仕様書は、以下の原則に基づいて統合・簡略化されました：

### 10.1 削減された機能
- **AI機能**: 実装複雑度が高く、基本機能で十分
- **高度なアニメーション**: パフォーマンス影響とメンテナンス負荷
- **多言語UI**: 日本語・英語のみに集約
- **高度なカスタマイズ**: 設定項目を必要最小限に

### 10.2 重視した点
- **Windows 11完全対応**: ネイティブな動作感
- **安定性**: 確実に動作する技術選択
- **シンプルさ**: 直感的で迷わない操作
- **保守性**: メンテナンスしやすいコード

### 10.3 次のステップ
1. **プロトタイプ開発**: 基本機能の動作確認
2. **Windows 11テスト**: 各環境での動作検証
3. **ユーザーテスト**: 実際の使用感確認
4. **パフォーマンス最適化**: 実測値に基づく改善

この仕様により、理想と現実のバランスを保った、実用的で保守しやすいアプリケーションを構築できます。