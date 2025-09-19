# PDF2PNG プロジェクト ファイル整理計画

## 🎯 整理の目的
- 重複ファイルの除去
- 最新バージョン（v3.0）への統一
- プロジェクト構造の簡素化
- 保守性の向上

## 📋 重複・廃止対象ファイル分析

### 🔴 **削除対象ファイル**

#### **1. 古いビルド設定ファイル**
- `build.spec` → 削除（`build_windows_v3.spec`で置換済み）
- `build_windows.spec` → 削除（v3.0で改良済み）

#### **2. 古いメインファイル**
- `main.py` → 削除（`main_v3.py`で置換済み）

#### **3. 古いビルドスクリプト**
- `scripts/create_windows_package.ps1` → 削除（`scripts/build_windows_v3.ps1`で統合済み）

#### **4. 重複ドキュメント**
- `BUILD_QUICK_GUIDE.md` → 削除（`REFACTORING_PLAN.md`に統合済み）
- `PROJECT_STRUCTURE.md` → 削除（`README.md`に統合済み）

### 🟡 **統合・リネーム対象ファイル**

#### **1. メインファイルの整理**
- `main_v3.py` → `main.py`にリネーム（v3.0が正式版）

#### **2. ビルド設定の整理**
- `build_windows_v3.spec` → `build_windows.spec`にリネーム

#### **3. スクリプトの整理**
- `scripts/build_windows_v3.ps1` → `scripts/build_windows.ps1`にリネーム

### 🟢 **保持・更新対象ファイル**

#### **1. 仕様書・計画書**
- `README.md` - プロジェクト概要（更新）
- `PDF2PNG_仕様書.md` - 詳細仕様（保持）
- `PDF2PNG_UX改善仕様書.md` - UX改善計画（保持）
- `REFACTORING_PLAN.md` - リファクタリング計画（保持）

#### **2. セキュリティ関連**
- `security/` ディレクトリ全体（保持）

#### **3. ドキュメント**
- `docs/` ディレクトリ内の詳細ドキュメント（保持）

## 🔧 実行手順

### Phase 1: バックアップ作成
1. 重要ファイルのバックアップ
2. Git コミット状態の確認

### Phase 2: 古いファイル削除
1. 廃止されたビルド設定ファイル削除
2. 古いメインファイル削除
3. 重複スクリプト削除
4. 重複ドキュメント削除

### Phase 3: ファイルリネーム
1. v3.0ファイルを正式版名に変更
2. 参照の更新

### Phase 4: 参照更新
1. ドキュメント内の参照修正
2. スクリプト内のパス修正

### Phase 5: 検証
1. ビルド動作確認
2. テスト実行確認

## 📁 整理後のファイル構造

```
PDF2PNG/
├── main.py                         # ← main_v3.py から名称変更
├── build_windows.spec              # ← build_windows_v3.spec から名称変更
├── requirements.txt
├── pyproject.toml
├──
├── README.md                       # 更新
├── PDF2PNG_仕様書.md
├── PDF2PNG_UX改善仕様書.md
├── REFACTORING_PLAN.md
├──
├── scripts/
│   ├── build_windows.ps1           # ← build_windows_v3.ps1 から名称変更
│   └── validate_build.ps1
├──
├── src/                            # リファクタリング済みソースコード
├── tests/
├── docs/                           # 詳細ドキュメント
├── security/                       # セキュリティ関連
├── legacy_original/               # 旧バージョン（アーカイブ）
└── sample_outputs/
```

## ⚠️ 注意事項

### **削除前確認**
- Git 状態の確認
- 重要な変更のコミット
- バックアップの作成

### **参照更新対象**
- README.md 内のファイル参照
- ドキュメント内のパス
- ビルドスクリプト内の参照

### **テスト項目**
- ビルドスクリプトの動作確認
- アプリケーション起動確認
- 基本機能の動作確認