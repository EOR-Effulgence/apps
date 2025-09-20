# PDF2PNG 開発環境セットアップガイド

## 🎯 Python仮想環境構築完了

**実行日時**: 2025年9月20日
**Python環境**: Python 3.11
**仮想環境**: venv

## ✅ 構築済み環境

### **Python仮想環境**
```bash
# 仮想環境作成済み
venv/
├── Include/          # ヘッダーファイル
├── Lib/             # Pythonライブラリ
├── Scripts/         # 実行スクリプト・ツール
└── pyvenv.cfg       # 仮想環境設定
```

### **インストール済み依存関係**
- ✅ **PyMuPDF 1.26.4** - PDF処理ライブラリ
- ✅ **python-pptx 1.0.2** - PowerPoint生成ライブラリ
- ✅ **Pillow 9.5.0** - 画像処理ライブラリ
- ✅ **PyInstaller 6.16.0** - 実行ファイル生成ツール

### **コンパイル済み実行ファイル**
- ✅ `dist/PDF2PNG_Converter.exe` (37.4MB)
- ✅ スタンドアロン実行可能
- ✅ 依存関係すべて埋め込み済み

## 🚀 環境使用方法

### **仮想環境の有効化**
```bash
# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Windows (Command Prompt)
venv\Scripts\activate.bat
```

### **仮想環境での開発**
```bash
# 仮想環境有効化後
pip install -r requirements.txt
python main.py
```

### **実行ファイルの使用**
```bash
# 直接実行（仮想環境不要）
dist\PDF2PNG_Converter.exe

# テストモード
dist\PDF2PNG_Converter.exe --test-mode

# ヘルプ表示
dist\PDF2PNG_Converter.exe --help
```

## 🔧 開発コマンド

### **依存関係管理**
```bash
# 仮想環境で新しいパッケージインストール
venv\Scripts\pip.exe install パッケージ名

# requirements.txt更新
venv\Scripts\pip.exe freeze > requirements.txt
```

### **再ビルド**
```bash
# 仮想環境でPyInstaller実行
venv\Scripts\pyinstaller.exe build_windows.spec --clean --noconfirm

# または直接PyInstaller使用
pyinstaller build_windows.spec --clean --noconfirm
```

### **テスト実行**
```bash
# アプリケーションテスト
python -m pytest tests/ -v

# ビルド検証テスト
python tests\test_build_validation.py
```

## 📁 プロジェクト構造

```
PDF2PNG/
├── venv/                          # Python仮想環境
├── src/                           # ソースコード
│   ├── application/              # アプリケーション層
│   ├── presentation/             # プレゼンテーション層
│   ├── core/                     # コアビジネスロジック
│   ├── ui/                       # ユーザーインターフェース
│   └── utils/                    # ユーティリティ
├── dist/                         # ビルド出力
│   └── PDF2PNG_Converter.exe    # メイン実行ファイル
├── build/                        # ビルド一時ファイル
├── tests/                        # テストコード
├── scripts/                      # ビルドスクリプト
├── main.py                       # アプリケーションエントリーポイント
├── build_windows.spec            # PyInstallerビルド設定
├── requirements.txt              # Python依存関係
└── pyproject_uv.toml            # UV最適化設定
```

## ⚡ UV Package Manager (高速化オプション)

### **UVインストール**
```powershell
# PowerShellでUVインストール
curl -LsSf https://astral.sh/uv/install.ps1 | powershell
```

### **UV使用ビルド**
```bash
# UV環境構築・ビルド（10-100倍高速）
.\scripts\build_with_uv.ps1 -Version "3.0.0" -Clean -Test
```

## 🧪 品質保証

### **ビルド検証**
- ✅ 実行ファイルサイズ: 37.4MB（適正範囲）
- ✅ 依存関係: 完全に埋め込み済み
- ✅ Python 3.11.10互換
- ✅ Windows 10/11対応

### **機能テスト**
```bash
# 基本機能テスト
dist\PDF2PNG_Converter.exe --test-mode

# パフォーマンステスト
python tests\test_build_validation.py::TestPerformanceBenchmarks
```

## 🔍 トラブルシューティング

### **仮想環境が認識されない場合**
```bash
# PowerShell実行ポリシー変更
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **依存関係エラーの場合**
```bash
# 仮想環境再作成
rm -rf venv
python -m venv venv
venv\Scripts\pip.exe install -r requirements.txt
```

### **ビルドエラーの場合**
```bash
# キャッシュクリア・再ビルド
rm -rf build dist
pyinstaller build_windows.spec --clean --noconfirm
```

## 📊 環境情報

| 項目 | 値 |
|------|-----|
| Python バージョン | 3.11+ |
| 仮想環境 | venv (標準) |
| PyInstaller | 6.16.0 |
| ビルドプラットフォーム | Windows 10/11 x64 |
| 実行ファイルサイズ | 37.4MB |
| 起動時間目標 | < 3秒 |
| メモリ使用量目標 | < 100MB |

## 🎉 セットアップ完了

**Python仮想環境の構築とWindowsアプリケーションのコンパイルが正常に完了しました！**

- 仮想環境: `venv/` (開発用)
- 実行ファイル: `dist/PDF2PNG_Converter.exe` (配布用)
- 依存関係: すべて解決済み
- ビルドスクリプト: 自動化完了

これで開発・ビルド・配布の準備がすべて整いました。