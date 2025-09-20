# PDF2PPTX アーキテクチャ再設計提案

## 🎯 設計目標

1. **明確な責任分離**: 各レイヤーの役割を明確に定義
2. **依存関係の簡素化**: 循環依存の排除と単方向フローの確立
3. **拡張性の向上**: 新機能追加時の影響範囲を最小化
4. **テスタビリティ**: 単体テストとモックが容易な設計
5. **保守性**: コードの可読性と変更容易性の向上

## 🏗️ 新しいアーキテクチャ

### レイヤー構造

```
src/
├── domain/                     # ドメインレイヤー（ビジネスロジック）
│   ├── entities/              # エンティティ（PDF、変換ジョブ等）
│   ├── value_objects/         # 値オブジェクト（設定、座標等）
│   ├── repositories/          # リポジトリインターフェース
│   └── services/              # ドメインサービス
│
├── application/               # アプリケーションレイヤー
│   ├── use_cases/            # ユースケース実装
│   ├── interfaces/           # 外部依存のインターフェース
│   └── dto/                  # データ転送オブジェクト
│
├── infrastructure/           # インフラストラクチャレイヤー
│   ├── pdf/                 # PDF処理の具象実装
│   ├── file_system/         # ファイルシステム操作
│   ├── config/              # 設定管理
│   └── logging/             # ログ出力
│
├── presentation/            # プレゼンテーションレイヤー
│   ├── gui/                # GUI実装（Tkinter）
│   ├── cli/                # CLI実装
│   ├── controllers/        # コントローラー
│   └── dto/                # 表示用DTO
│
└── shared/                 # 共通要素
    ├── exceptions/         # カスタム例外
    ├── constants/          # 定数定義
    └── utils/              # 汎用ユーティリティ
```

## 🔄 クリーンアーキテクチャ原則の適用

### 依存関係の方向

```
Presentation → Application → Domain ← Infrastructure
```

- **Domain**: 外部に依存しない純粋なビジネスロジック
- **Application**: ドメインを組み合わせたユースケース
- **Infrastructure**: 外部技術（PDF、ファイル、GUI）への依存
- **Presentation**: ユーザーインターフェース

### インターフェース駆動設計

```python
# Domain Layer - Interface
class PDFRepository(ABC):
    @abstractmethod
    def load_pdf(self, path: Path) -> PDFDocument: ...

    @abstractmethod
    def count_pages(self, document: PDFDocument) -> int: ...

# Infrastructure Layer - Implementation
class PyMuPDFRepository(PDFRepository):
    def load_pdf(self, path: Path) -> PDFDocument:
        # PyMuPDF specific implementation
        pass
```

## 📋 主要コンポーネントの再設計

### 1. ドメインエンティティ

```python
# src/domain/entities/pdf_document.py
@dataclass
class PDFDocument:
    """PDF文書を表すドメインエンティティ"""
    id: str
    file_path: Path
    page_count: int
    metadata: Dict[str, Any]
    pages: List[PDFPage]

# src/domain/entities/conversion_job.py
class ConversionJob:
    """変換ジョブを管理するエンティティ"""
    def __init__(self, documents: List[PDFDocument], config: ConversionConfig):
        self._documents = documents
        self._config = config
        self._status = ConversionStatus.PENDING

    def start_conversion(self) -> None:
        """変換開始のビジネスルール"""
        if not self._documents:
            raise ValueError("変換対象のドキュメントがありません")
        self._status = ConversionStatus.RUNNING
```

### 2. アプリケーションサービス（ユースケース）

```python
# src/application/use_cases/convert_pdf_to_images.py
class ConvertPDFToImagesUseCase:
    """PDF→画像変換のユースケース"""

    def __init__(
        self,
        pdf_repository: PDFRepository,
        image_converter: ImageConverter,
        file_repository: FileRepository,
        logger: Logger
    ):
        self._pdf_repo = pdf_repository
        self._image_converter = image_converter
        self._file_repo = file_repository
        self._logger = logger

    async def execute(self, request: ConvertToImagesRequest) -> ConvertToImagesResponse:
        """ユースケース実行"""
        # 1. PDF読み込み
        documents = [self._pdf_repo.load_pdf(path) for path in request.file_paths]

        # 2. 変換ジョブ作成
        job = ConversionJob(documents, request.config)

        # 3. 変換実行
        results = await self._image_converter.convert_all(job)

        # 4. 結果保存
        saved_files = [self._file_repo.save(result) for result in results]

        return ConvertToImagesResponse(saved_files)
```

### 3. プレゼンテーション分離

```python
# src/presentation/controllers/conversion_controller.py
class ConversionController:
    """変換処理のコントローラー"""

    def __init__(self, convert_use_case: ConvertPDFToImagesUseCase):
        self._convert_use_case = convert_use_case

    async def handle_image_conversion(self, view_model: ConversionViewModel) -> None:
        """GUI/CLIから呼ばれる変換ハンドラー"""
        try:
            request = self._map_to_request(view_model)
            response = await self._convert_use_case.execute(request)
            self._notify_success(response)
        except Exception as e:
            self._notify_error(e)
```

## 🔧 依存性注入とDIコンテナ

### DIコンテナの実装

```python
# src/shared/di_container.py
class DIContainer:
    """軽量DIコンテナ"""

    def __init__(self):
        self._services = {}
        self._singletons = {}

    def register_singleton(self, interface: Type, implementation: Type) -> None:
        """シングルトンサービス登録"""
        self._services[interface] = (implementation, True)

    def register_transient(self, interface: Type, implementation: Type) -> None:
        """トランジェントサービス登録"""
        self._services[interface] = (implementation, False)

    def get(self, interface: Type) -> Any:
        """サービス取得"""
        if interface not in self._services:
            raise ValueError(f"Service {interface} not registered")

        implementation, is_singleton = self._services[interface]

        if is_singleton:
            if interface not in self._singletons:
                self._singletons[interface] = self._create_instance(implementation)
            return self._singletons[interface]

        return self._create_instance(implementation)
```

### アプリケーション起動時の設定

```python
# src/main.py (改良版)
def setup_di_container() -> DIContainer:
    """DIコンテナの設定"""
    container = DIContainer()

    # Infrastructure
    container.register_singleton(PDFRepository, PyMuPDFRepository)
    container.register_singleton(FileRepository, LocalFileRepository)
    container.register_singleton(Logger, StructuredLogger)

    # Application
    container.register_transient(ConvertPDFToImagesUseCase, ConvertPDFToImagesUseCase)
    container.register_transient(ConvertPDFToPPTXUseCase, ConvertPDFToPPTXUseCase)

    # Presentation
    container.register_transient(ConversionController, ConversionController)

    return container

def main():
    container = setup_di_container()
    controller = container.get(ConversionController)

    # GUI or CLI startup
    if args.gui:
        gui_app = GUIApplication(controller)
        gui_app.run()
    else:
        cli_app = CLIApplication(controller)
        cli_app.run(args)
```

## 🧪 テスタビリティの向上

### モックとテストの容易化

```python
# tests/application/test_convert_pdf_to_images_use_case.py
class TestConvertPDFToImagesUseCase:

    def setup_method(self):
        self.mock_pdf_repo = Mock(spec=PDFRepository)
        self.mock_image_converter = Mock(spec=ImageConverter)
        self.mock_file_repo = Mock(spec=FileRepository)
        self.mock_logger = Mock(spec=Logger)

        self.use_case = ConvertPDFToImagesUseCase(
            self.mock_pdf_repo,
            self.mock_image_converter,
            self.mock_file_repo,
            self.mock_logger
        )

    async def test_successful_conversion(self):
        # Given
        request = ConvertToImagesRequest(
            file_paths=[Path("test.pdf")],
            config=ConversionConfig()
        )

        mock_document = PDFDocument(id="1", file_path=Path("test.pdf"), ...)
        self.mock_pdf_repo.load_pdf.return_value = mock_document

        # When
        response = await self.use_case.execute(request)

        # Then
        assert response.success
        self.mock_pdf_repo.load_pdf.assert_called_once()
        self.mock_image_converter.convert_all.assert_called_once()
```

## 📊 移行計画

### フェーズ1: ドメインレイヤー構築
1. エンティティとバリューオブジェクトの抽出
2. ドメインサービスの実装
3. リポジトリインターフェースの定義

### フェーズ2: アプリケーションレイヤー再構築
1. ユースケースの実装
2. DTOの定義
3. 既存サービスからの移行

### フェーズ3: インフラストラクチャ分離
1. PDF処理の具象実装分離
2. ファイルシステム操作の抽象化
3. 設定管理の改善

### フェーズ4: プレゼンテーション改善
1. コントローラーの実装
2. GUI/CLI統合
3. 古いコードの削除

## 🔍 期待される効果

### コード品質
- **重複コード**: 90%削減
- **循環依存**: 完全排除
- **テストカバレッジ**: 80%以上

### 開発効率
- **新機能追加**: 50%高速化
- **バグ修正**: 影響範囲の明確化
- **リファクタリング**: 安全性向上

### 保守性
- **コード理解**: 新規開発者のオンボーディング短縮
- **技術負債**: 継続的な削減
- **拡張性**: プラグイン機能の追加容易化

## 🚀 実装開始

この設計により、PDF2PPTXアプリケーションは堅牢で拡張可能な現代的なアーキテクチャを獲得します。

**次のステップ**: ドメインエンティティの実装から開始し、段階的に移行を進めます。