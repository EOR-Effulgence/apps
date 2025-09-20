# PDF2PNG/PDF2PPTX 統合仕様書 v3.0
**最新版・統合設計ドキュメント**

---

## 📋 目次

1. [プロジェクト概要](#1-プロジェクト概要)
2. [アーキテクチャ設計](#2-アーキテクチャ設計)
3. [UI/UX設計仕様](#3-uiux設計仕様)
4. [モダンUIデザインシステム](#4-モダンuiデザインシステム)
5. [機能仕様](#5-機能仕様)
6. [技術仕様](#6-技術仕様)
7. [実装ガイド](#7-実装ガイド)
8. [運用・メンテナンス](#8-運用メンテナンス)
9. [今後の展開](#9-今後の展開)

---

## 1. プロジェクト概要

### 1.1 ソフトウェア名称
**PDF2PNG/PDF2PPTX Converter v3.0**

### 1.2 プロジェクトミッション
PDFファイルをPNG画像またはPowerPointプレゼンテーション（PPTX）形式に変換するモダンGUIツール。ユーザビリティとアクセシビリティを重視し、プロフェッショナルかつ直感的な操作体験を提供する。

### 1.3 対象ユーザー

#### プライマリユーザー
- **ビジネスプロフェッショナル**: プレゼンテーション資料作成者
- **教育関係者**: 授業資料・研修資料作成者
- **デザイナー・クリエイター**: 画像素材活用者

#### セカンダリユーザー
- **事務作業者**: 大量文書処理担当者
- **研究者**: 論文・資料作成者
- **一般ユーザー**: 個人的な文書変換ニーズ

### 1.4 価値提案
- **効率性**: バッチ処理による高速変換
- **品質**: 高解像度出力対応
- **使いやすさ**: 直感的なモダンUI
- **プロフェッショナル**: カスタマイズ可能な出力設定
- **アクセシビリティ**: 多様なユーザーに配慮した設計

---

## 2. アーキテクチャ設計

### 2.1 MVP アーキテクチャ

```
┌─────────────────────────┐
│        Presenter        │  ←─ UI イベント処理・ビジネスロジック
│   (MainPresenter)       │
└─────────────────────────┘
            ↕
┌─────────────────────────┐
│          View           │  ←─ UI 表示・ユーザー操作
│     (MainWindow)        │
└─────────────────────────┘
            ↕
┌─────────────────────────┐
│         Model           │  ←─ データ処理・ビジネスロジック
│  (ConversionService,    │
│   PDFProcessor)         │
└─────────────────────────┘
```

### 2.2 モジュール構成

```
src/
├── presentation/
│   └── presenters/
│       └── main_presenter.py      # MVP - Presenter層
├── ui/
│   ├── main_window.py             # MVP - View層
│   ├── components/
│   │   ├── modern_widgets.py      # モダンUI コンポーネント
│   │   ├── progress_components.py # プログレス表示系
│   │   └── settings_panel.py      # 設定パネル
│   └── themes/
│       ├── material_theme.py      # Material Design 3 テーマ
│       └── color_schemes.py       # カラースキーム定義
├── application/
│   └── services/
│       └── conversion_service.py  # MVP - Model層（アプリケーションサービス）
├── core/
│   └── pdf_processor.py           # MVP - Model層（ドメインロジック）
├── utils/
│   ├── error_handling.py          # エラーハンドリング
│   ├── path_utils.py              # パス管理
│   └── animation_utils.py         # アニメーションユーティリティ
└── config.py                      # 設定管理
```

### 2.3 コンポーネント間通信

#### データフロー
1. **View → Presenter**: ユーザーアクション（ボタンクリック、ファイル選択）
2. **Presenter → Model**: ビジネスロジック実行依頼
3. **Model → Presenter**: 処理結果・進捗情報
4. **Presenter → View**: UI更新指示

#### 非同期処理
- **メインスレッド**: UI操作・表示更新
- **ワーカースレッド**: PDF変換処理
- **プログレスコールバック**: リアルタイム進捗更新

---

## 3. UI/UX設計仕様

### 3.1 UX設計原則

#### 3.1.1 ユーザビリティ原則
- **直感性**: 初見でも操作方法が理解できる
- **効率性**: 最小限のクリックで目的達成
- **一貫性**: アプリケーション全体で統一されたUI
- **フィードバック**: 操作結果の明確な視覚的反応
- **エラー回避**: ミス防止機能と明確なエラーメッセージ

#### 3.1.2 アクセシビリティ
- **キーボードナビゲーション**: 全機能キーボードのみで操作可能
- **スクリーンリーダー対応**: 音声読み上げソフト対応
- **色覚サポート**: 色に依存しない情報表示
- **フォントサイズ**: 拡大縮小対応
- **高コントラスト**: 視認性の高い配色

### 3.2 情報アーキテクチャ

#### 3.2.1 画面構成階層
```
メイン画面
├── ヘッダー部
│   ├── アプリタイトル
│   └── メニューボタン
├── コンテンツ部
│   ├── ファイル操作エリア
│   ├── 設定パネル
│   ├── 変換ボタン群
│   └── プログレス表示
└── フッター部
    ├── ステータス表示
    └── ヘルプボタン
```

#### 3.2.2 操作フロー
1. **ファイル選択**: ドラッグ&ドロップ or フォルダ選択
2. **設定調整**: 変換設定・出力設定
3. **変換実行**: ワンクリック変換開始
4. **進捗確認**: リアルタイム進捗表示
5. **結果確認**: 完了通知・結果フォルダ表示

### 3.3 インタラクション設計

#### 3.3.1 マイクロインタラクション
- **ボタンホバー**: 0.2秒のスムーズな色変化
- **クリックフィードバック**: 0.1秒の軽快な押下感
- **フォーカス表示**: 明確なフォーカスリング
- **ドラッグ&ドロップ**: リアルタイムプレビュー

#### 3.3.2 フィードバックシステム
- **即座のフィードバック**: 操作時の即座の視覚反応
- **進捗フィードバック**: 処理進行状況の詳細表示
- **完了フィードバック**: 成功・失敗の明確な通知
- **エラーフィードバック**: 問題解決に導くエラーメッセージ

---

## 4. モダンUIデザインシステム

### 4.1 Material Design 3 適用

#### 4.1.1 デザイントークン
```python
# カラーシステム
PRIMARY_COLORS = {
    'light': {
        'primary': '#1976D2',      # ブルー系メイン
        'on_primary': '#FFFFFF',   # プライマリ上のテキスト
        'primary_container': '#E3F2FD',
        'on_primary_container': '#0D47A1'
    },
    'dark': {
        'primary': '#90CAF9',      # ダークモード対応
        'on_primary': '#1A1A1A',
        'primary_container': '#1565C0',
        'on_primary_container': '#E3F2FD'
    }
}

# タイポグラフィ
TYPOGRAPHY = {
    'headline_large': ('Noto Sans CJK JP', 32, 'normal'),
    'headline_medium': ('Noto Sans CJK JP', 28, 'normal'),
    'title_large': ('Noto Sans CJK JP', 22, 'medium'),
    'title_medium': ('Noto Sans CJK JP', 16, 'medium'),
    'body_large': ('Noto Sans CJK JP', 16, 'normal'),
    'body_medium': ('Noto Sans CJK JP', 14, 'normal'),
    'label_large': ('Noto Sans CJK JP', 14, 'medium')
}
```

#### 4.1.2 レイアウトシステム
- **グリッドシステム**: 8dpベースグリッド
- **余白**: 8dp, 16dp, 24dp, 32dpの倍数
- **コンポーネント間隔**: 最小8dp間隔
- **レスポンシブ**: ウィンドウサイズ対応

### 4.2 コンポーネントライブラリ

#### 4.2.1 基本コンポーネント

**ModernButton**
```python
class ModernButton(CTkButton):
    """Material Design 3準拠のボタンコンポーネント"""

    def __init__(self, master, variant="filled", **kwargs):
        # filled, outlined, text の3バリエーション
        # ホバー・フォーカス・アクティブ状態対応
        # アクセシビリティ対応（キーボードナビゲーション）
```

**ModernCard**
```python
class ModernCard(CTkFrame):
    """カード型コンテナコンポーネント"""

    # エレベーション効果
    # 角丸・シャドウ・ボーダー制御
    # コンテンツ配置管理
```

**ModernProgressBar**
```python
class ModernProgressBar(CTkProgressBar):
    """アニメーション対応プログレスバー"""

    # 円形・線形プログレス
    # パーセント表示
    # カラーカスタマイズ
    # スムーズアニメーション
```

#### 4.2.2 複合コンポーネント

**FileDropZone**
```python
class FileDropZone(ModernCard):
    """ドラッグ&ドロップ対応ファイル選択エリア"""

    # ドラッグホバー状態の視覚フィードバック
    # ファイル形式バリデーション
    # プレビュー機能
```

**SettingsPanel**
```python
class SettingsPanel(ModernCard):
    """設定項目統合パネル"""

    # 設定値のリアルタイムプレビュー
    # バリデーション機能
    # 設定保存・復元
```

### 4.3 テーマシステム

#### 4.3.1 ライト・ダークモード
```python
class ThemeManager:
    """動的テーマ切り替え管理"""

    def __init__(self):
        self.current_theme = self.detect_system_theme()

    def apply_theme(self, theme_name: str):
        """テーマ適用（アニメーション付き）"""

    def toggle_theme(self):
        """ライト⇔ダーク切り替え"""
```

#### 4.3.2 カスタマイズ対応
- **アクセントカラー**: ユーザー選択可能
- **フォントサイズ**: 3段階調整
- **アニメーション**: ON/OFF切り替え
- **高コントラスト**: アクセシビリティモード

---

## 5. 機能仕様

### 5.1 主要機能

#### 5.1.1 PDF → PNG変換
```python
class PDFtoPNGConverter:
    """PDF to PNG conversion with advanced options"""

    def convert(self,
               pdf_path: Path,
               output_dir: Path,
               scale_factor: float = 1.5,
               auto_rotate: bool = True,
               quality: str = 'high') -> List[Path]:
        """
        PDFファイルをPNG画像に変換

        Args:
            pdf_path: 変換対象PDFファイルパス
            output_dir: 出力ディレクトリ
            scale_factor: 拡大倍率 (1.0-3.0)
            auto_rotate: 縦長ページの自動横向き回転
            quality: 出力品質 ('low', 'medium', 'high')

        Returns:
            作成されたPNGファイルパスのリスト
        """
```

**特徴**:
- **高解像度出力**: 最大300DPI対応
- **バッチ処理**: フォルダ内全PDFファイル一括変換
- **自動回転**: 縦長ページの横向き変換
- **プログレス表示**: ページ別進捗表示
- **カスタム命名**: `{ファイル名}_{ページ番号}.png`

#### 5.1.2 PDF → PPTX変換（A3横サイズ）
```python
class PDFtoPPTXConverter:
    """PDF to PowerPoint conversion with professional layouts"""

    def convert(self,
               pdf_paths: List[Path],
               output_path: Path,
               slide_size: tuple = (420, 297),  # A3横 mm
               label_config: LabelConfig = None,
               template: str = 'professional') -> Path:
        """
        PDFファイルをPowerPointプレゼンテーションに変換

        Args:
            pdf_paths: 変換対象PDFファイルパスリスト
            output_path: 出力PPTXファイルパス
            slide_size: スライドサイズ (幅, 高さ) mm
            label_config: ラベル設定
            template: テンプレート種類

        Returns:
            作成されたPPTXファイルパス
        """
```

**特徴**:
- **A3横サイズ**: 420×297mm スライド
- **中央配置**: 画像のスライド中央配置
- **カスタムラベル**: フォント・色・位置設定可能
- **テンプレート**: 複数レイアウトテンプレート
- **メタデータ**: ファイル名・ページ番号自動挿入

#### 5.1.3 ファイル操作
```python
class FileManager:
    """Advanced file management with safety features"""

    def select_folder(self) -> Optional[Path]:
        """フォルダ選択ダイアログ"""

    def validate_permissions(self, path: Path) -> bool:
        """読み書き権限チェック"""

    def backup_existing(self, path: Path) -> Path:
        """既存ファイルバックアップ"""

    def cleanup_temp(self):
        """一時ファイルクリーンアップ"""
```

### 5.2 ユーザーインターフェース

#### 5.2.1 メイン画面レイアウト
```
┌─────────────────────────────────────────────────┐
│  📄 PDF2PNG/PDF2PPTX Converter v3.0     [🌙]   │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │        📁 ファイル・フォルダ選択           │    │
│  │                                         │    │
│  │   ドラッグ&ドロップでファイルを追加      │    │
│  │         または                          │    │
│  │   [📁 フォルダ選択] [📄 ファイル選択]    │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  ┌───── 変換設定 ─────┬──── 出力設定 ────┐      │
│  │ 🔧 拡大倍率: [1.5] │ 📁 出力先:        │      │
│  │ 🔄 自動回転: ☑     │   同じフォルダ     │      │
│  │ 🎨 品質: [高]      │ 📝 命名規則:      │      │
│  │                   │   自動             │      │
│  └───────────────────┴─────────────────┘      │
│                                                 │
│  ┌──────── 変換実行 ────────┐                   │
│  │ [📄 PNG変換] [📈 PPTX変換] │                   │
│  └─────────────────────────┘                   │
│                                                 │
│  ┌────── プログレス表示 ──────┐                  │
│  │ ████████████░░░░░░ 67%     │                  │
│  │ 処理中: sample.pdf (3/5)   │                  │
│  └─────────────────────────┘                  │
│                                                 │
├─────────────────────────────────────────────────┤
│ 📊 待機中 | 📁 出力先: 未選択 | ⚙️ 設定  | ❓ ヘルプ │
└─────────────────────────────────────────────────┘
```

#### 5.2.2 設定パネル
```python
class SettingsPanel(ModernCard):
    """統合設定パネル"""

    def __init__(self, master):
        super().__init__(master)

        # 変換設定
        self.scale_setting = ScaleSlider(min=1.0, max=3.0, default=1.5)
        self.quality_setting = OptionMenu(['低', '中', '高'])
        self.rotation_setting = Switch(default=True)

        # PowerPoint設定
        self.font_setting = FontSelector()
        self.color_setting = ColorPicker()
        self.template_setting = TemplateSelector()

        # 出力設定
        self.output_dir_setting = DirectorySelector()
        self.naming_setting = NamingPatternSelector()
```

### 5.3 設定管理

#### 5.3.1 設定項目
```json
{
  "conversion": {
    "default_scale": 1.5,
    "auto_rotate": true,
    "quality": "high",
    "output_format": "png"
  },
  "powerpoint": {
    "slide_size": [420, 297],
    "font_name": "Noto Sans CJK JP",
    "font_size": 18,
    "text_color": "#FFFFFF",
    "background_color": "#1976D2",
    "border_color": "#FF0000",
    "label_position": "top-left"
  },
  "ui": {
    "theme": "auto",
    "language": "ja",
    "animation_enabled": true,
    "auto_open_result": true
  },
  "advanced": {
    "memory_limit": 1024,
    "temp_dir": "auto",
    "backup_enabled": true,
    "log_level": "INFO"
  }
}
```

---

## 6. 技術仕様

### 6.1 開発環境・要件

#### 6.1.1 言語・フレームワーク
- **Python**: 3.8+ (推奨: 3.11+)
- **GUI**: CustomTkinter + tkinterdnd2
- **型チェック**: mypy
- **フォーマッタ**: black
- **リンター**: ruff

#### 6.1.2 主要依存関係
```txt
# 必須依存関係
PyMuPDF>=1.26.0           # PDF処理エンジン
python-pptx>=1.0.0        # PowerPoint生成
Pillow>=11.0.0           # 画像処理
customtkinter>=5.2.0     # モダンGUI
tkinterdnd2>=0.4.0       # ドラッグ&ドロップ

# 開発依存関係
mypy>=1.18.0             # 型チェック
black>=25.0.0            # コードフォーマッタ
pytest>=8.4.0           # テストフレームワーク
pytest-cov>=7.0.0       # カバレッジ
```

#### 6.1.3 プラットフォーム対応
- **Windows**: 10/11 (プライマリサポート)
- **macOS**: 10.15+ (セカンダリサポート)
- **Linux**: Ubuntu 20.04+ (ベストエフォート)

### 6.2 パフォーマンス仕様

#### 6.2.1 処理性能目標
- **変換速度**: A4 1ページ 0.5秒以内
- **メモリ使用量**: 最大1GB以内
- **UI応答性**: 操作から0.1秒以内の反応
- **起動時間**: 3秒以内

#### 6.2.2 スケーラビリティ
- **同時処理**: 最大10ファイル並列処理
- **最大ページ数**: 1000ページ/ファイル
- **ファイルサイズ**: 最大500MB/ファイル

### 6.3 セキュリティ・品質

#### 6.3.1 セキュリティ要件
- **ファイルアクセス**: ユーザー選択ディレクトリのみ
- **一時ファイル**: 処理完了後自動削除
- **エラーログ**: 個人情報除外
- **依存関係**: 定期的脆弱性スキャン

#### 6.3.2 品質管理
```python
# テストカバレッジ目標
COVERAGE_TARGETS = {
    'core': 90,      # コア変換ロジック
    'ui': 70,        # UI コンポーネント
    'utils': 85,     # ユーティリティ
    'overall': 80    # 全体
}

# パフォーマンステスト
PERFORMANCE_TESTS = {
    'conversion_speed': '< 0.5s per page',
    'memory_usage': '< 1GB peak',
    'ui_response': '< 0.1s',
    'startup_time': '< 3s'
}
```

---

## 7. 実装ガイド

### 7.1 開発環境セットアップ

#### 7.1.1 仮想環境構築
```bash
# 1. プロジェクトクローン
git clone <repository_url>
cd PDF2PPTX

# 2. 仮想環境作成・有効化
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 3. 依存関係インストール
pip install -r requirements.txt
pip install -r requirements_dev.txt  # 開発用

# 4. アプリケーション実行
python main.py
```

#### 7.1.2 IDE設定（VSCode推奨）
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.testing.pytestEnabled": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/.pytest_cache": true,
        "**/build": true,
        "**/dist": true
    }
}
```

### 7.2 コード規約

#### 7.2.1 Python規約
```python
"""モジュールドキュメント例"""

from typing import Optional, List, Dict, Any
from pathlib import Path
import asyncio

class ExampleClass:
    """クラスドキュメント

    Attributes:
        public_attr: パブリック属性の説明
        _private_attr: プライベート属性の説明
    """

    def __init__(self, param: str) -> None:
        self.public_attr = param
        self._private_attr = self._initialize_private()

    def public_method(self,
                     input_param: Path,
                     optional_param: Optional[str] = None) -> List[str]:
        """パブリックメソッドドキュメント

        Args:
            input_param: 入力パラメータの説明
            optional_param: オプショナルパラメータの説明

        Returns:
            戻り値の説明

        Raises:
            ValueError: エラー条件の説明
        """
        if not input_param.exists():
            raise ValueError(f"File not found: {input_param}")

        return self._process_file(input_param, optional_param)

    def _private_method(self) -> Any:
        """プライベートメソッドは簡潔なドキュメント"""
        pass
```

#### 7.2.2 UI コンポーネント規約
```python
class ModernWidget(CTkFrame):
    """モダンUIウィジェット基底クラス"""

    def __init__(self,
                 master,
                 theme: str = 'auto',
                 **kwargs):
        super().__init__(master, **kwargs)

        self.theme = theme
        self._setup_ui()
        self._bind_events()

    def _setup_ui(self) -> None:
        """UI 初期化（サブクラスでオーバーライド）"""
        raise NotImplementedError

    def _bind_events(self) -> None:
        """イベントバインド（サブクラスでオーバーライド）"""
        pass

    def update_theme(self, theme: str) -> None:
        """テーマ更新"""
        self.theme = theme
        self._apply_theme()

    def _apply_theme(self) -> None:
        """テーマ適用（サブクラスでオーバーライド）"""
        pass
```

### 7.3 テスト戦略

#### 7.3.1 単体テスト
```python
# tests/test_pdf_processor.py
import pytest
from pathlib import Path
from src.core.pdf_processor import PDFProcessor

class TestPDFProcessor:
    """PDF処理コア機能のテスト"""

    @pytest.fixture
    def processor(self):
        return PDFProcessor()

    @pytest.fixture
    def sample_pdf(self):
        return Path('tests/data/sample.pdf')

    def test_pdf_to_images_basic(self, processor, sample_pdf):
        """基本的なPDF→画像変換テスト"""
        images = processor.pdf_to_images(sample_pdf)

        assert len(images) > 0
        assert all(img.suffix == '.png' for img in images)

    def test_pdf_to_images_with_scale(self, processor, sample_pdf):
        """スケール指定変換テスト"""
        images = processor.pdf_to_images(sample_pdf, scale=2.0)

        # 2倍スケールでの画像サイズ検証
        assert len(images) > 0

    @pytest.mark.parametrize("scale", [0.5, 1.0, 1.5, 2.0, 3.0])
    def test_various_scales(self, processor, sample_pdf, scale):
        """様々なスケールでのテスト"""
        images = processor.pdf_to_images(sample_pdf, scale=scale)
        assert len(images) > 0
```

#### 7.3.2 統合テスト
```python
# tests/test_integration.py
import pytest
from pathlib import Path
from src.application.services.conversion_service import ConversionService

class TestConversionIntegration:
    """変換サービス統合テスト"""

    @pytest.fixture
    def service(self):
        return ConversionService()

    def test_end_to_end_png_conversion(self, service, tmp_path):
        """PNG変換エンドツーエンドテスト"""
        # テストデータ準備
        input_pdf = tmp_path / "test.pdf"
        # ... PDF作成

        # 変換実行
        results = service.convert_to_png(input_pdf, tmp_path)

        # 結果検証
        assert len(results) > 0
        assert all(result.exists() for result in results)
```

### 7.4 ビルド・デプロイ

#### 7.4.1 実行ファイル生成
```bash
# PyInstaller設定ファイル使用
pyinstaller build_windows.spec --clean --noconfirm

# 生成されるファイル
dist/
├── PDF2PNG_Converter.exe     # GUI版
└── PDF2PNG_Console.exe       # コンソール版
```

#### 7.4.2 配布パッケージ
```python
# build.py - 自動ビルドスクリプト
import subprocess
import zipfile
from pathlib import Path

def build_distribution():
    """配布用パッケージ作成"""

    # 1. 実行ファイル生成
    subprocess.run(['pyinstaller', 'build_windows.spec', '--clean'])

    # 2. 配布ファイル準備
    dist_files = [
        'dist/PDF2PNG_Converter.exe',
        'README.md',
        'LICENSE',
        'sample_outputs/'
    ]

    # 3. ZIP パッケージ作成
    with zipfile.ZipFile('PDF2PNG_v3.0_Windows.zip', 'w') as zf:
        for file_path in dist_files:
            if Path(file_path).exists():
                zf.write(file_path)
```

---

## 8. 運用・メンテナンス

### 8.1 ログ・監視

#### 8.1.1 ログ設定
```python
# src/utils/logging_config.py
import logging
from pathlib import Path

def setup_logging(log_file: Path, level: str = 'INFO'):
    """ロギング設定"""

    logger = logging.getLogger('PDF2PNG')
    logger.setLevel(getattr(logging, level))

    # ファイルハンドラ
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # コンソールハンドラ（開発時のみ）
    if level == 'DEBUG':
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    logger.addHandler(file_handler)
    return logger
```

#### 8.1.2 エラー追跡
```python
# src/utils/error_tracking.py
import traceback
from typing import Optional
from pathlib import Path

class ErrorTracker:
    """エラー追跡・レポート機能"""

    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.error_log = log_dir / 'errors.log'

    def log_error(self,
                  error: Exception,
                  context: dict,
                  user_action: Optional[str] = None):
        """エラーログ記録"""

        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context,
            'user_action': user_action
        }

        # 個人情報を除外してログ記録
        safe_info = self._sanitize_error_info(error_info)

        with open(self.error_log, 'a', encoding='utf-8') as f:
            json.dump(safe_info, f, ensure_ascii=False, indent=2)
            f.write('\n')
```

### 8.2 更新・メンテナンス

#### 8.2.1 自動更新チェック
```python
# src/utils/update_checker.py
import requests
from packaging import version

class UpdateChecker:
    """アプリケーション更新チェック"""

    def __init__(self, current_version: str):
        self.current_version = current_version
        self.update_url = "https://api.github.com/repos/user/pdf2png/releases/latest"

    async def check_for_updates(self) -> Optional[dict]:
        """最新バージョンチェック"""
        try:
            response = requests.get(self.update_url, timeout=5)
            latest_release = response.json()

            latest_version = latest_release['tag_name'].lstrip('v')

            if version.parse(latest_version) > version.parse(self.current_version):
                return {
                    'available': True,
                    'version': latest_version,
                    'download_url': latest_release['assets'][0]['browser_download_url'],
                    'release_notes': latest_release['body']
                }

            return {'available': False}

        except Exception as e:
            logger.warning(f"Update check failed: {e}")
            return None
```

#### 8.2.2 データ移行
```python
# src/utils/migration.py
class ConfigMigrator:
    """設定ファイル移行機能"""

    def migrate_config(self, old_config: dict, target_version: str) -> dict:
        """設定ファイル移行"""

        migrations = {
            '2.0': self._migrate_to_v2,
            '3.0': self._migrate_to_v3
        }

        current_config = old_config.copy()

        for version, migration_func in migrations.items():
            if version <= target_version:
                current_config = migration_func(current_config)

        return current_config

    def _migrate_to_v3(self, config: dict) -> dict:
        """v3.0 移行処理"""
        # 新しい設定項目追加
        config.setdefault('ui', {})
        config['ui'].setdefault('theme', 'auto')
        config['ui'].setdefault('animation_enabled', True)

        return config
```

### 8.3 パフォーマンス監視

#### 8.3.1 処理性能測定
```python
# src/utils/performance_monitor.py
import time
import psutil
from contextlib import contextmanager

class PerformanceMonitor:
    """パフォーマンス監視"""

    @contextmanager
    def measure_operation(self, operation_name: str):
        """処理時間・リソース使用量測定"""

        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss

        try:
            yield
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss

            metrics = {
                'operation': operation_name,
                'duration': end_time - start_time,
                'memory_delta': end_memory - start_memory,
                'timestamp': start_time
            }

            self._log_metrics(metrics)

    def _log_metrics(self, metrics: dict):
        """メトリクス記録"""
        # パフォーマンスログ出力
        logger.info(f"Performance: {metrics}")
```

---

## 9. 今後の展開

### 9.1 短期計画（3-6ヶ月）

#### 9.1.1 機能追加
- **OCR機能**: PDF内テキスト抽出・検索
- **バッチ設定**: 変換設定プロファイル保存
- **プレビュー機能**: 変換前ページプレビュー
- **出力形式拡張**: JPEG, TIFF, WebP対応

#### 9.1.2 UX改善
- **ドラッグ&ドロップ拡張**: ファイル・フォルダ対応
- **キーボードショートカット**: 全機能キーボード操作
- **コンテキストメニュー**: 右クリックメニュー
- **多言語対応**: 英語・中国語対応

### 9.2 中期計画（6-12ヶ月）

#### 9.2.1 プラットフォーム拡張
- **Web版**: ブラウザベース変換ツール
- **モバイル版**: iOS/Android アプリ
- **クラウド連携**: Google Drive, OneDrive 対応
- **API提供**: 他アプリケーション連携

#### 9.2.2 高度機能
- **AI活用**: 自動レイアウト最適化
- **フォーマット認識**: 表・図表自動検出
- **テンプレートエンジン**: カスタムPPTXテンプレート
- **ワークフロー自動化**: 定期実行・監視フォルダ

### 9.3 長期ビジョン（1-2年）

#### 9.3.1 プロダクトエコシステム
- **統合オフィススイート**: PDF, Office, 画像変換統合
- **プラグインシステム**: サードパーティ拡張対応
- **エンタープライズ版**: 大企業向け機能拡張
- **教育版**: 教育機関向け特別機能

#### 9.3.2 技術革新
- **機械学習**: 変換品質自動最適化
- **クラウドネイティブ**: フルクラウドアーキテクチャ
- **リアルタイム協業**: 複数ユーザー同時編集
- **VR/AR対応**: 次世代インターフェース

---

## 📚 付録

### A. 設定ファイル詳細

#### A.1 config.json スキーマ
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "conversion": {
      "type": "object",
      "properties": {
        "default_scale": {"type": "number", "minimum": 0.1, "maximum": 5.0},
        "auto_rotate": {"type": "boolean"},
        "quality": {"type": "string", "enum": ["low", "medium", "high"]},
        "output_format": {"type": "string", "enum": ["png", "jpg", "tiff"]}
      }
    },
    "powerpoint": {
      "type": "object",
      "properties": {
        "slide_size": {
          "type": "array",
          "items": {"type": "number"},
          "minItems": 2,
          "maxItems": 2
        },
        "font_name": {"type": "string"},
        "font_size": {"type": "integer", "minimum": 8, "maximum": 72},
        "text_color": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
        "background_color": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
        "border_color": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"}
      }
    }
  }
}
```

### B. API リファレンス

#### B.1 PDFProcessor クラス
```python
class PDFProcessor:
    """PDF処理コアエンジン"""

    def __init__(self,
                 temp_dir: Optional[Path] = None,
                 memory_limit: int = 1024) -> None:
        """初期化"""

    def get_pdf_info(self, pdf_path: Path) -> PDFInfo:
        """PDF情報取得"""

    def pdf_to_images(self,
                     pdf_path: Path,
                     output_dir: Path,
                     scale: float = 1.5,
                     format: str = 'PNG',
                     auto_rotate: bool = True,
                     progress_callback: Optional[Callable] = None) -> List[Path]:
        """PDF→画像変換"""

    def pdf_to_pptx(self,
                   pdf_paths: List[Path],
                   output_path: Path,
                   slide_config: SlideConfig,
                   progress_callback: Optional[Callable] = None) -> Path:
        """PDF→PPTX変換"""
```

### C. トラブルシューティング

#### C.1 よくあるエラーと対処法

**ImportError: No module named 'fitz'**
```bash
# 解決方法
pip install PyMuPDF
```

**tkinter.TclError: couldn't open library**
```bash
# 仮想環境を使用
venv\Scripts\activate
python main.py
```

**MemoryError during conversion**
```python
# 設定で対処
config['conversion']['default_scale'] = 1.0  # スケール下げる
config['advanced']['memory_limit'] = 512    # メモリ制限
```

---

**文書情報**
- **バージョン**: 3.0
- **作成日**: 2025年9月20日
- **最終更新**: 2025年9月20日
- **対象システム**: PDF2PNG/PDF2PPTX Converter v3.0

**統合元文書**
- PDF2PNG_UX改善仕様書.md
- PDF2PNG_モダンUIデザイン仕様書.md
- PDF2PNG_仕様書.md

---

*このドキュメントは、PDF2PNG/PDF2PPTX Converter v3.0の包括的な設計・実装仕様書です。全ての開発者・利用者が参照すべき最新版として機能します。*