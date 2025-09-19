# PDF2PNG/PDF2PPTX リファクタリング・Windows ビルド準備計画

## 🎯 リファクタリング目標

### 1. **Windowsアプリケーション品質向上**
- モダンなWindowsアプリケーション標準への準拠
- PyInstaller最適化によるパフォーマンス向上
- エラーハンドリングとユーザビリティの強化
- 配布パッケージの最適化

### 2. **アーキテクチャ改善**
- コードの保守性向上
- テスタビリティの改善
- モジュール間の依存関係最適化
- 設定管理システムの統一

## 📋 Phase 1: コードベース分析と準備

### ✅ **現状の良い点**
- モジュラーなアーキテクチャ（リファクタリング済み）
- 包括的なエラーハンドリングシステム
- 型ヒント完備
- 設定システムの充実

### 🔧 **改善が必要な領域**

#### A. **UI/UX レイヤー**
- 固定ウィンドウサイズ → レスポンシブデザイン
- 基本的なtkinter → モダンなUIコンポーネント
- 同期処理 → 非同期処理でレスポンシブ性向上

#### B. **設定管理**
- 分散した設定項目の統一
- Windows固有設定の追加
- レジストリ連携の検討

#### C. **ビルド最適化**
- 依存関係の最小化
- スタートアップ時間の短縮
- 実行ファイルサイズの最適化

## 🏗️ Phase 2: アーキテクチャリファクタリング

### 2.1 **MVPパターンの実装**

```python
# 新しいアーキテクチャ構造
src/
├── core/                    # ビジネスロジック（既存・良好）
│   ├── pdf_processor.py
│   └── __init__.py
├── presentation/            # 新規：プレゼンテーション層
│   ├── presenters/
│   │   ├── main_presenter.py
│   │   ├── conversion_presenter.py
│   │   └── settings_presenter.py
│   └── view_models/
│       ├── main_view_model.py
│       └── conversion_view_model.py
├── ui/                      # ビュー層（改良）
│   ├── views/
│   │   ├── main_window.py
│   │   ├── settings_dialog.py
│   │   └── progress_dialog.py
│   ├── components/
│   │   ├── file_selector.py
│   │   ├── preview_panel.py
│   │   └── progress_bar.py
│   └── styles/
│       ├── theme_manager.py
│       └── windows_theme.py
├── infrastructure/          # インフラ層
│   ├── config/
│   │   ├── app_config.py
│   │   ├── user_preferences.py
│   │   └── windows_registry.py
│   ├── logging/
│   │   ├── logger_factory.py
│   │   └── windows_event_log.py
│   └── file_system/
│       ├── path_resolver.py
│       └── temp_file_manager.py
└── application/             # アプリケーション層
    ├── services/
    │   ├── conversion_service.py
    │   ├── validation_service.py
    │   └── notification_service.py
    └── use_cases/
        ├── convert_pdf_to_png.py
        ├── convert_pdf_to_pptx.py
        └── manage_user_settings.py
```

### 2.2 **依存性注入コンテナ**

```python
# src/infrastructure/container.py
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

class ApplicationContainer(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()

    # Infrastructure
    logger = providers.Singleton(LoggerFactory)
    file_manager = providers.Singleton(FileManager)
    config_manager = providers.Singleton(ConfigManager)

    # Core Services
    pdf_processor = providers.Factory(
        PDFProcessor,
        logger=logger,
        file_manager=file_manager
    )

    # Application Services
    conversion_service = providers.Factory(
        ConversionService,
        pdf_processor=pdf_processor,
        logger=logger
    )

    # Presenters
    main_presenter = providers.Factory(
        MainPresenter,
        conversion_service=conversion_service,
        config_manager=config_manager
    )
```

### 2.3 **非同期処理の実装**

```python
# src/presentation/presenters/conversion_presenter.py
import asyncio
from typing import Callable, Optional
from concurrent.futures import ThreadPoolExecutor

class ConversionPresenter:
    def __init__(self, conversion_service, progress_callback: Callable):
        self.conversion_service = conversion_service
        self.progress_callback = progress_callback
        self.executor = ThreadPoolExecutor(max_workers=2)

    async def convert_files_async(self, files: List[Path], config: ConversionConfig):
        """非同期ファイル変換"""
        loop = asyncio.get_event_loop()

        # 重い処理をバックグラウンドで実行
        future = loop.run_in_executor(
            self.executor,
            self._convert_files_sync,
            files,
            config
        )

        # プログレス監視を並行実行
        progress_task = asyncio.create_task(
            self._monitor_progress(future)
        )

        try:
            result = await future
            progress_task.cancel()
            return result
        except Exception as e:
            progress_task.cancel()
            raise e

    async def _monitor_progress(self, future):
        """プログレス監視"""
        while not future.done():
            await asyncio.sleep(0.1)
            # プログレス更新
            self.progress_callback(self.conversion_service.get_progress())
```

## 🎨 Phase 3: UI/UX モダナイゼーション

### 3.1 **レスポンシブUI設計**

```python
# src/ui/views/main_window.py
import tkinter as tk
from tkinter import ttk
from typing import Protocol

class MainViewInterface(Protocol):
    def show_progress(self, percentage: int, message: str): ...
    def show_error(self, error: str): ...
    def update_file_list(self, files: List[FileInfo]): ...

class ModernMainWindow(tk.Tk):
    def __init__(self, presenter):
        super().__init__()
        self.presenter = presenter
        self._setup_window()
        self._create_responsive_layout()
        self._apply_modern_styling()

    def _setup_window(self):
        """ウィンドウ基本設定"""
        self.title("PDF2PNG/PDF2PPTX Converter v3.0")
        self.minsize(800, 600)
        self.geometry("1000x700")

        # Windowsネイティブ外観
        self.configure(bg='#f0f0f0')

        # アイコン設定
        try:
            self.iconbitmap('assets/app_icon.ico')
        except:
            pass  # アイコンファイルがない場合は無視

    def _create_responsive_layout(self):
        """レスポンシブレイアウト作成"""
        # メインコンテナ
        main_container = ttk.Frame(self)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # 3ペイン構成
        # 左：ファイル選択・プレビュー
        # 中央：設定パネル
        # 右：プログレス・ログ

        self._create_file_panel(main_container)
        self._create_settings_panel(main_container)
        self._create_progress_panel(main_container)
```

### 3.2 **Windowsネイティブ体験**

```python
# src/ui/styles/windows_theme.py
import tkinter as tk
from tkinter import ttk
import sys

class WindowsThemeManager:
    def __init__(self):
        self.is_dark_mode = self._detect_windows_dark_mode()
        self.setup_theme()

    def _detect_windows_dark_mode(self) -> bool:
        """Windows ダークモード検出"""
        if sys.platform == "win32":
            try:
                import winreg
                registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(
                    registry,
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                )
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return value == 0  # 0 = dark mode
            except:
                return False
        return False

    def setup_theme(self):
        """テーマ適用"""
        style = ttk.Style()

        if self.is_dark_mode:
            self._apply_dark_theme(style)
        else:
            self._apply_light_theme(style)

    def _apply_dark_theme(self, style):
        style.theme_use('clam')
        style.configure('TLabel', background='#2d2d2d', foreground='#ffffff')
        style.configure('TFrame', background='#2d2d2d')
        style.configure('TButton', background='#404040', foreground='#ffffff')
        # ...他のスタイル設定
```

## 🔧 Phase 4: Windows ビルド最適化

### 4.1 **PyInstaller設定改良**

```python
# build_windows_optimized.spec
# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# プロジェクトルート取得
project_root = Path(__file__).parent
src_path = project_root / "src"

# 隠れたインポートを明示的に指定
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'PIL._tkinter_finder',
    'fitz',
    'pptx',
    'pptx.util',
    'pptx.dml.color',
    'pptx.enum.shapes',
    'dependency_injector',
    'asyncio',
    'concurrent.futures',
    'queue',
    'threading',
    'multiprocessing',
]

# データファイル
datas = [
    (str(src_path / "ui" / "assets"), "assets"),
    (str(project_root / "config"), "config"),
    ("README.md", "."),
]

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[str(project_root), str(src_path)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # 不要な大きなライブラリを除外
        'numpy',
        'scipy',
        'pandas',
        'jupyter',
        'IPython',
        'pytest',
        'mypy',
        'black',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 重複したバイナリを除去
a.binaries = a.binaries - TOC([
    ('mfc140u.dll', None, None),
    ('mfcm140u.dll', None, None),
])

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PDF2PNG_Converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # UPX圧縮有効
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # コンソールウィンドウ非表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app_icon.ico',  # アプリケーションアイコン
    version='version_info.txt',  # バージョン情報
)
```

### 4.2 **バージョン情報ファイル**

```python
# version_info.txt
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(3,0,0,0),
    prodvers=(3,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'041103a4',
        [StringStruct(u'CompanyName', u'PDF2PNG Project'),
        StringStruct(u'FileDescription', u'PDF to PNG/PPTX Converter'),
        StringStruct(u'FileVersion', u'3.0.0.0'),
        StringStruct(u'InternalName', u'PDF2PNG_Converter'),
        StringStruct(u'LegalCopyright', u'© 2025 PDF2PNG Project'),
        StringStruct(u'OriginalFilename', u'PDF2PNG_Converter.exe'),
        StringStruct(u'ProductName', u'PDF2PNG/PDF2PPTX Converter'),
        StringStruct(u'ProductVersion', u'3.0.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1041, 932])])
  ]
)
```

### 4.3 **ビルド自動化スクリプト**

```powershell
# scripts/build_windows_release.ps1
param(
    [string]$Version = "3.0.0",
    [switch]$Clean = $false,
    [switch]$Test = $false
)

Write-Host "🚀 PDF2PNG Windows Build Script v$Version" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

# 環境チェック
Write-Host "📋 環境チェック中..." -ForegroundColor Yellow

# Python バージョン確認
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python が見つかりません"
    exit 1
}
Write-Host "✅ $pythonVersion" -ForegroundColor Green

# 仮想環境の確認
if (-not (Test-Path "venv")) {
    Write-Host "📦 仮想環境を作成中..." -ForegroundColor Yellow
    python -m venv venv
}

# 仮想環境アクティベート
Write-Host "🔧 仮想環境をアクティベート中..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# 依存関係インストール
Write-Host "📥 依存関係をインストール中..." -ForegroundColor Yellow
pip install -r requirements.txt
pip install pyinstaller

if ($Clean) {
    Write-Host "🧹 クリーンビルド実行中..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "build", "dist"
}

# テスト実行（オプション）
if ($Test) {
    Write-Host "🧪 テスト実行中..." -ForegroundColor Yellow
    python -m pytest tests/ -v
    if ($LASTEXITCODE -ne 0) {
        Write-Error "テストが失敗しました"
        exit 1
    }
}

# ビルド実行
Write-Host "🔨 アプリケーションビルド中..." -ForegroundColor Yellow
pyinstaller build_windows_optimized.spec --clean

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ ビルド成功！" -ForegroundColor Green

    # ファイルサイズ確認
    $exePath = "dist\PDF2PNG_Converter.exe"
    if (Test-Path $exePath) {
        $fileSize = (Get-Item $exePath).Length / 1MB
        Write-Host "📊 実行ファイルサイズ: $([math]::Round($fileSize, 1)) MB" -ForegroundColor Cyan
    }

    # 配布パッケージ作成
    Write-Host "📦 配布パッケージ作成中..." -ForegroundColor Yellow
    $releaseDir = "release\PDF2PNG_Windows_v$Version"
    New-Item -ItemType Directory -Force -Path $releaseDir

    Copy-Item "dist\PDF2PNG_Converter.exe" "$releaseDir\"
    Copy-Item "README.md" "$releaseDir\"
    Copy-Item "PDF2PNG_仕様書.md" "$releaseDir\"

    # ZIP作成
    Compress-Archive -Path $releaseDir -DestinationPath "release\PDF2PNG_Windows_v$Version.zip" -Force

    Write-Host "🎉 配布パッケージ完成: release\PDF2PNG_Windows_v$Version.zip" -ForegroundColor Green
} else {
    Write-Error "ビルドが失敗しました"
    exit 1
}
```

## 🧪 Phase 5: テスト・品質保証

### 5.1 **自動テストスイート拡張**

```python
# tests/test_windows_integration.py
import pytest
import tempfile
import subprocess
from pathlib import Path

class TestWindowsIntegration:
    """Windows固有の統合テスト"""

    def test_executable_startup(self):
        """実行ファイルの起動テスト"""
        exe_path = Path("dist/PDF2PNG_Converter.exe")
        if not exe_path.exists():
            pytest.skip("実行ファイルが見つかりません")

        # 起動テスト（短時間で終了）
        process = subprocess.Popen(
            [str(exe_path), "--test-mode"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # 3秒後に終了
        try:
            stdout, stderr = process.communicate(timeout=3)
            assert process.returncode == 0
        except subprocess.TimeoutExpired:
            process.terminate()
            # タイムアウトは正常（GUIアプリのため）

    def test_file_associations(self):
        """ファイル関連付けテスト"""
        # Windows レジストリ確認
        pass

    def test_memory_usage(self):
        """メモリ使用量テスト"""
        import psutil
        import os

        # メモリ使用量監視
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # 大きなPDFファイルでテスト
        # ...テスト実行...

        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory

        # メモリ増加が200MB以下であること
        assert memory_increase < 200, f"メモリ使用量が過大です: {memory_increase}MB"
```

### 5.2 **パフォーマンステスト**

```python
# tests/test_performance.py
import time
import pytest
from pathlib import Path
from src.core.pdf_processor import PDFProcessor

class TestPerformance:
    """パフォーマンステスト"""

    @pytest.mark.performance
    def test_conversion_speed(self):
        """変換速度テスト"""
        test_files = [
            "sample_pdfs/small_1page.pdf",
            "sample_pdfs/medium_10pages.pdf",
            "sample_pdfs/large_50pages.pdf"
        ]

        processor = PDFProcessor()

        for test_file in test_files:
            if not Path(test_file).exists():
                continue

            start_time = time.time()
            # 変換実行
            end_time = time.time()

            processing_time = end_time - start_time

            # ページあたり1秒以下であること
            pages = processor.count_pages(Path(test_file))
            time_per_page = processing_time / pages

            assert time_per_page < 1.0, f"変換速度が遅すぎます: {time_per_page}秒/ページ"
```

## 📦 Phase 6: 配布・インストーラー

### 6.1 **Windowsインストーラー作成**

```nsis
; PDF2PNG_Installer.nsi - NSIS インストーラースクリプト
!define APP_NAME "PDF2PNG Converter"
!define APP_VERSION "3.0.0"
!define APP_PUBLISHER "PDF2PNG Project"
!define APP_URL "https://github.com/pdf2png/pdf2png-converter"
!define APP_EXEC "PDF2PNG_Converter.exe"

; インストーラー設定
Name "${APP_NAME}"
OutFile "PDF2PNG_Converter_v${APP_VERSION}_Setup.exe"
InstallDir "$PROGRAMFILES\${APP_NAME}"
RequestExecutionLevel admin

; ページ設定
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; アンインストールページ
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; 言語設定
!insertmacro MUI_LANGUAGE "Japanese"
!insertmacro MUI_LANGUAGE "English"

; インストール処理
Section "MainSection" SEC01
  SetOutPath "$INSTDIR"

  ; ファイルコピー
  File "dist\PDF2PNG_Converter.exe"
  File "README.md"
  File "PDF2PNG_仕様書.md"

  ; レジストリ設定
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
                   "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
                   "UninstallString" "$INSTDIR\Uninstall.exe"

  ; スタートメニューショートカット
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXEC}"
  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXEC}"

  ; アンインストーラー作成
  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

; アンインストール処理
Section "Uninstall"
  Delete "$INSTDIR\PDF2PNG_Converter.exe"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\PDF2PNG_仕様書.md"
  Delete "$INSTDIR\Uninstall.exe"

  ; ショートカット削除
  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  RMDir "$SMPROGRAMS\${APP_NAME}"

  ; レジストリクリーンアップ
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

  RMDir "$INSTDIR"
SectionEnd
```

## 🚀 実装スケジュール

### **Week 1-2: 基盤リファクタリング**
- [x] PowerPoint設定システム完成
- [ ] MVPアーキテクチャ実装
- [ ] 依存性注入システム導入
- [ ] 非同期処理基盤構築

### **Week 3-4: UI/UX改善**
- [ ] レスポンシブUI実装
- [ ] Windowsテーマ対応
- [ ] ファイル操作UI強化
- [ ] プログレス表示改善

### **Week 5-6: ビルド最適化**
- [ ] PyInstaller設定最適化
- [ ] パフォーマンステスト実施
- [ ] メモリ使用量最適化
- [ ] 起動時間短縮

### **Week 7-8: 配布準備**
- [ ] Windowsインストーラー作成
- [ ] 自動テストスイート拡充
- [ ] ドキュメント更新
- [ ] ベータテスト実施

## 🎯 成功指標

### **技術的指標**
- 起動時間: < 3秒
- メモリ使用量: < 100MB (アイドル時)
- 実行ファイルサイズ: < 50MB
- 変換速度: < 1秒/ページ

### **品質指標**
- テストカバレッジ: > 85%
- 静的解析エラー: 0件
- セキュリティ脆弱性: 0件
- ユーザビリティスコア: > 4.5/5.0

この計画により、PDF2PNGアプリケーションを現代的で高品質なWindowsアプリケーションに進化させ、優秀な配布可能な実行ファイルを作成できます。