# PDF2PNG/PDF2PPTX Converter v3.0

**次世代PDFコンバーター - MVP アーキテクチャ & Material Design 3**

PDFドキュメントをPNG画像またはPowerPointプレゼンテーションに変換する、モダンなGUIアプリケーションです。クリーンアーキテクチャとユーザビリティを重視した設計で、プロフェッショナルな変換体験を提供します。

## 🚀 プロジェクト概要

PDF2PPTX_2は、従来のTkinterベースのアプリケーションを完全に刷新し、現代的なQt6/PySide6とMaterial Design 3を採用した次世代コンバーターです。MVP（Model-View-Presenter）アーキテクチャにより、保守性とテスト性を大幅に向上させています。

### 主な特徴

- **🎨 Material Design 3**: 美しく直感的なユーザーインターフェース
- **⚡ 高速変換**: A4ページを0.5秒以内で処理
- **🔄 非同期処理**: UIをブロックしない変換処理
- **📱 レスポンシブ設計**: ウィンドウサイズに適応するレイアウト
- **🌓 ダークモード**: 動的テーマ切り替え対応
- **🎯 バッチ処理**: フォルダ単位での一括変換
- **📊 リアルタイム進捗**: 詳細な処理状況表示

## 📋 変換機能

### PDF → PNG 変換
- **高解像度出力**: 最大300DPI対応
- **自動回転**: 縦長ページの横向き変換
- **カスタムスケール**: 0.5倍〜3.0倍の倍率調整
- **品質設定**: 低・中・高の3段階品質選択

### PDF → PowerPoint 変換
- **A3横サイズ**: 420×297mm スライド
- **カスタムラベル**: フォント・色・位置の自由設定
- **テンプレート**: 複数のレイアウトパターン
- **プロフェッショナル仕上げ**: 企業プレゼン品質

## 🛠️ 技術スタック

### コアテクノロジー
- **Python**: 3.8+ （推奨: 3.11+）
- **GUI**: PySide6/Qt6
- **PDF処理**: PyMuPDF (fitz)
- **PowerPoint生成**: python-pptx
- **画像処理**: Pillow

### 開発ツール
- **型チェック**: MyPy
- **コードフォーマット**: Black
- **リンター**: Ruff
- **テストフレームワーク**: pytest
- **セキュリティスキャン**: Bandit

## 📁 プロジェクト構造

```
PDF2PPTX_2/
├── src/
│   ├── presentation/
│   │   └── presenters/          # MVP - Presenter層
│   ├── ui/
│   │   ├── main_window.py       # メインウィンドウ
│   │   ├── components/          # Material Design 3 コンポーネント
│   │   └── themes/              # テーマシステム
│   ├── application/
│   │   └── services/            # アプリケーションサービス
│   ├── core/
│   │   └── pdf_processor.py     # PDF処理エンジン
│   └── utils/                   # ユーティリティ
├── tests/                       # テストスイート
├── requirements.txt             # 依存関係
├── requirements_dev.txt         # 開発用依存関係
├── build_*.spec                 # PyInstaller設定
└── PDF2PPTX_統合仕様書.md        # 詳細仕様書（1000行+）
```

## 🚀 クイックスタート

### 1. 環境セットアップ

#### uvを使用した環境構築（推奨）

```bash
# uvのインストール（初回のみ）
# Windows: winget install astral-sh.uv
# または: pip install uv

# 仮想環境作成
uv venv

# 仮想環境有効化（Windows）
.venv\Scripts\activate

# 依存関係インストール
uv pip install -r requirements.txt
```

#### 従来のpip環境

```bash
# 仮想環境作成（必須）
python -m venv venv

# 仮想環境有効化（Windows）
venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# 開発用依存関係インストール
pip install -r requirements_dev.txt
```

### 2. アプリケーション実行

```bash
# メインGUIアプリケーション
python main.py

# 開発モード
python -m src.ui.main_window
```

## 🧪 開発・テスト

### コード品質管理

```bash
# コードフォーマット
black src tests

# 型チェック
mypy src

# リンティング
ruff src tests

# セキュリティスキャン
bandit -r src/
```

### テスト実行

```bash
# 全テスト実行
pytest

# カバレッジ付きテスト
pytest --cov=src tests/

# セキュリティテスト
pytest -m security

# 統合テスト
pytest -m integration
```

## 📦 ビルド・配布

### 実行ファイル生成

```bash
# Windows GUI版
pyinstaller build_windows.spec --clean --noconfirm

# コンソール版
pyinstaller build_console.spec --clean --noconfirm
```

## 🎯 パフォーマンス目標

- **変換速度**: A4 1ページ 0.5秒以内
- **メモリ使用量**: 最大1GB以内
- **UI応答性**: 操作から0.1秒以内の反応
- **起動時間**: 3秒以内
- **テストカバレッジ**: 全体80%以上

## 🔒 セキュリティ

- **入力検証**: 全ファイルパス・パラメータの検証
- **サンドボックス処理**: 悪意のあるPDFコンテンツからの保護
- **一時ファイル管理**: 自動クリーンアップ機能
- **依存関係監査**: 定期的な脆弱性スキャン

## 📚 ドキュメント

- **詳細仕様書**: `PDF2PPTX_統合仕様書.md` - 包括的な設計・実装仕様
- **開発ガイド**: `CLAUDE.md` - Claude Code用の開発指針
- **アーキテクチャ**: MVP パターンの実装詳細

## 🎨 UI/UX デザイン

### Material Design 3 準拠
- **デザイントークン**: 一貫性のあるスタイルシステム
- **アニメーション**: スムーズなマイクロインタラクション
- **アクセシビリティ**: WCAG 2.1 AA準拠
- **多言語対応**: 日本語メインUI

### テーマシステム
- **ライト・ダークモード**: 動的切り替え
- **アクセントカラー**: ユーザーカスタマイズ可能
- **レスポンシブレイアウト**: ウィンドウサイズ対応

## 🤝 貢献・開発

### 開発フロー
1. 仕様書 (`PDF2PPTX_統合仕様書.md`) の確認
2. MVP アーキテクチャパターンの遵守
3. Material Design 3 ガイドラインの適用
4. 包括的なテストの作成
5. セキュリティ要件の充足

### コード規約
- **Black**: 88文字行長でのフォーマット
- **型ヒント**: 全関数・クラス属性への型注釈
- **Docstring**: Google スタイルドキュメント
- **PEP 8**: Python命名規則の遵守

## 📄 ライセンス

MIT License - 詳細は LICENSE ファイルを参照

## 🆘 サポート

問題や質問については、以下をご確認ください：
- **仕様書**: `PDF2PPTX_統合仕様書.md` で詳細な実装方針を確認
- **開発ガイド**: `CLAUDE.md` でClaude Code向けの指針を確認
- **アーキテクチャ**: MVP パターンの実装詳細を理解

---

**PDF2PNG/PDF2PPTX Converter v3.0** - Modern, Secure, Professional PDF Conversion Tool

---

## 📝 開発ログ

### 2025-01-20 環境構築完了

#### 実施内容
1. **uv環境のセットアップ**
   - `uv 0.6.14`を使用した仮想環境構築
   - Python 3.13.3環境を`.venv`に作成

2. **依存関係のインストール**
   - 必須パッケージをuvでインストール完了
     - PySide6 6.9.2 (Qt6 GUIフレームワーク)
     - pdf2image 1.17.0 (PDF変換)
     - python-pptx 1.0.2 (PowerPoint生成)
     - Pillow 11.3.0 (画像処理)
     - loguru 0.7.3 (ロギング)
     - python-dotenv 1.1.1 (環境変数)

3. **プロジェクト構造の作成**
   ```
   src/
   ├── main.py         # エントリーポイント作成済み
   ├── core/           # PDF処理エンジン用ディレクトリ
   ├── gui/            # GUI関連（Qt/PySide6）
   ├── utils/          # ユーティリティ
   └── tests/          # テスト用ディレクトリ
   ```

4. **基本ファイルの配置**
   - `requirements.txt`: 依存関係定義
   - `src/main.py`: メインエントリーポイント（ロギング設定付き）
   - 各ディレクトリに`__init__.py`配置

#### 次のステップ
- [ ] UIコンポーネント（Material Design 3）の実装
- [ ] PDF処理コアエンジンの実装
- [ ] 設定管理システムの構築
- [ ] エラーハンドリング機構の実装