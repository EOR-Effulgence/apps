"""
GUIコンポーネント
カスタムUIコンポーネントの実装
"""

import customtkinter as ctk
import tkinter as tk
# from tkinterdnd2 import *  # tkinterdnd2が必要な場合（オプション）
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
from loguru import logger


class FileDropZone(ctk.CTkFrame):
    """ファイルドロップゾーンコンポーネント"""

    def __init__(self,
                 master,
                 on_files_dropped: Optional[Callable[[List[Path]], None]] = None,
                 accepted_extensions: Optional[List[str]] = None,
                 **kwargs):
        """
        初期化

        Args:
            master: 親ウィジェット
            on_files_dropped: ファイルドロップ時のコールバック
            accepted_extensions: 受け入れる拡張子のリスト
        """
        super().__init__(master, **kwargs)

        self.on_files_dropped = on_files_dropped
        self.accepted_extensions = accepted_extensions or [".pdf"]

        self._setup_ui()
        self._setup_drag_drop()

    def _setup_ui(self):
        """UIセットアップ"""
        # 最小サイズ設定
        self.configure(height=200)

        # ボーダー設定
        self.configure(border_width=2, border_color="gray")

        # グリッド設定
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ドロップエリアのラベル
        self.drop_label = ctk.CTkLabel(
            self,
            text="📄\nPDFファイルをドラッグ&ドロップ\nまたは",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        self.drop_label.grid(row=0, column=0, pady=(20, 5))

        # ファイル選択ボタン
        self.browse_button = ctk.CTkButton(
            self,
            text="ファイルを選択",
            width=150,
            height=35,
            command=self._browse_files
        )
        self.browse_button.grid(row=1, column=0, pady=(5, 20))

    def _setup_drag_drop(self):
        """ドラッグ&ドロップの設定"""
        # Tkinterの基本的なドラッグ&ドロップ実装
        # tkinterdnd2を使用する場合はより高度な実装が可能
        self.bind("<Button-1>", self._on_click)

    def _browse_files(self):
        """ファイル選択ダイアログを開く"""
        from tkinter import filedialog

        filetypes = [(f"{ext.upper()} files", f"*{ext}") for ext in self.accepted_extensions]
        filetypes.append(("All files", "*.*"))

        files = filedialog.askopenfilenames(
            title="ファイルを選択",
            filetypes=filetypes
        )

        if files and self.on_files_dropped:
            file_paths = [Path(f) for f in files]
            self.on_files_dropped(file_paths)

    def _on_click(self, event):
        """クリック時の処理"""
        self._browse_files()

    def highlight(self, active: bool = True):
        """ドロップゾーンのハイライト"""
        if active:
            self.configure(border_color="blue", border_width=3)
            self.drop_label.configure(text_color="blue")
        else:
            self.configure(border_color="gray", border_width=2)
            self.drop_label.configure(text_color="gray")


class SettingsPanel(ctk.CTkScrollableFrame):
    """設定パネルコンポーネント"""

    def __init__(self,
                 master,
                 config_manager=None,
                 on_settings_changed: Optional[Callable[[Dict[str, Any]], None]] = None,
                 **kwargs):
        """
        初期化

        Args:
            master: 親ウィジェット
            config_manager: 設定管理オブジェクト
            on_settings_changed: 設定変更時のコールバック
        """
        # widthがkwargsにある場合は削除してから設定
        width = kwargs.pop('width', 300)
        super().__init__(master, width=width, **kwargs)

        self.config_manager = config_manager
        self.on_settings_changed = on_settings_changed
        self.settings_vars = {}

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """UIセットアップ"""
        # タイトル
        title_label = ctk.CTkLabel(
            self,
            text="変換設定",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 20))

        # PDF→PNG設定セクション
        png_section_label = ctk.CTkLabel(
            self,
            text="PDF → PNG 設定",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        png_section_label.grid(row=1, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        # DPI設定
        dpi_label = ctk.CTkLabel(self, text="解像度 (DPI):")
        dpi_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.dpi_var = tk.IntVar(value=150)
        self.settings_vars["dpi"] = self.dpi_var

        dpi_slider = ctk.CTkSlider(
            self,
            from_=72,
            to=300,
            variable=self.dpi_var,
            command=self._on_setting_changed
        )
        dpi_slider.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        self.dpi_value_label = ctk.CTkLabel(self, text="150")
        self.dpi_value_label.grid(row=3, column=1, padx=10, pady=0)

        # スケール設定
        scale_label = ctk.CTkLabel(self, text="拡大率:")
        scale_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self.scale_var = tk.DoubleVar(value=1.5)
        self.settings_vars["scale"] = self.scale_var

        scale_slider = ctk.CTkSlider(
            self,
            from_=0.5,
            to=3.0,
            variable=self.scale_var,
            command=self._on_setting_changed
        )
        scale_slider.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        self.scale_value_label = ctk.CTkLabel(self, text="1.5x")
        self.scale_value_label.grid(row=5, column=1, padx=10, pady=0)

        # 自動回転
        self.auto_rotate_var = tk.BooleanVar(value=True)
        self.settings_vars["auto_rotate"] = self.auto_rotate_var

        auto_rotate_check = ctk.CTkCheckBox(
            self,
            text="自動回転",
            variable=self.auto_rotate_var,
            command=self._on_setting_changed
        )
        auto_rotate_check.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # PowerPoint設定セクション
        pptx_section_label = ctk.CTkLabel(
            self,
            text="PowerPoint 設定",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        pptx_section_label.grid(row=7, column=0, columnspan=2, padx=10, pady=(20, 5), sticky="w")

        # スライドサイズ
        slide_size_label = ctk.CTkLabel(self, text="スライドサイズ:")
        slide_size_label.grid(row=8, column=0, padx=10, pady=5, sticky="w")

        self.slide_size_var = tk.StringVar(value="A3横")
        self.settings_vars["slide_size"] = self.slide_size_var

        slide_size_menu = ctk.CTkOptionMenu(
            self,
            values=["A3横", "A4横", "16:9", "4:3"],
            variable=self.slide_size_var,
            command=self._on_setting_changed
        )
        slide_size_menu.grid(row=8, column=1, padx=10, pady=5, sticky="ew")

        # ページ番号追加
        self.add_page_numbers_var = tk.BooleanVar(value=True)
        self.settings_vars["add_page_numbers"] = self.add_page_numbers_var

        page_numbers_check = ctk.CTkCheckBox(
            self,
            text="ページ番号を追加",
            variable=self.add_page_numbers_var,
            command=self._on_setting_changed
        )
        page_numbers_check.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # 出力設定セクション
        output_section_label = ctk.CTkLabel(
            self,
            text="出力設定",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        output_section_label.grid(row=10, column=0, columnspan=2, padx=10, pady=(20, 5), sticky="w")

        # サブフォルダ作成
        self.create_subfolder_var = tk.BooleanVar(value=True)
        self.settings_vars["create_subfolder"] = self.create_subfolder_var

        subfolder_check = ctk.CTkCheckBox(
            self,
            text="ファイルごとにサブフォルダ作成",
            variable=self.create_subfolder_var,
            command=self._on_setting_changed
        )
        subfolder_check.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # 既存ファイル上書き
        self.overwrite_var = tk.BooleanVar(value=False)
        self.settings_vars["overwrite_existing"] = self.overwrite_var

        overwrite_check = ctk.CTkCheckBox(
            self,
            text="既存ファイルを上書き",
            variable=self.overwrite_var,
            command=self._on_setting_changed
        )
        overwrite_check.grid(row=12, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # リセットボタン
        reset_button = ctk.CTkButton(
            self,
            text="設定をリセット",
            command=self._reset_settings
        )
        reset_button.grid(row=13, column=0, columnspan=2, padx=10, pady=20)

    def _load_settings(self):
        """設定を読み込み"""
        if not self.config_manager:
            return

        try:
            # PDF→PNG設定
            png_config = self.config_manager.get_config("conversion.pdf_to_png")
            if png_config:
                self.dpi_var.set(png_config.get("dpi", 150))
                self.scale_var.set(png_config.get("scale", 1.5))
                self.auto_rotate_var.set(png_config.get("auto_rotate", True))

            # PowerPoint設定
            pptx_config = self.config_manager.get_config("conversion.pdf_to_pptx")
            if pptx_config:
                self.add_page_numbers_var.set(pptx_config.get("add_page_numbers", True))

            # 出力設定
            output_config = self.config_manager.get_config("conversion.output")
            if output_config:
                self.create_subfolder_var.set(output_config.get("create_subfolder", True))
                self.overwrite_var.set(output_config.get("overwrite_existing", False))

            self._update_value_labels()

        except Exception as e:
            logger.error(f"設定読み込みエラー: {e}")

    def _on_setting_changed(self, *args):
        """設定変更時の処理"""
        self._update_value_labels()

        if self.on_settings_changed:
            settings = self.get_settings()
            self.on_settings_changed(settings)

    def _update_value_labels(self):
        """値ラベルの更新"""
        self.dpi_value_label.configure(text=str(int(self.dpi_var.get())))
        self.scale_value_label.configure(text=f"{self.scale_var.get():.1f}x")

    def _reset_settings(self):
        """設定をリセット"""
        self.dpi_var.set(150)
        self.scale_var.set(1.5)
        self.auto_rotate_var.set(True)
        self.slide_size_var.set("A3横")
        self.add_page_numbers_var.set(True)
        self.create_subfolder_var.set(True)
        self.overwrite_var.set(False)

        self._on_setting_changed()

    def get_settings(self) -> Dict[str, Any]:
        """現在の設定を取得"""
        return {
            "pdf_to_png.dpi": int(self.dpi_var.get()),
            "pdf_to_png.scale": self.scale_var.get(),
            "pdf_to_png.auto_rotate": self.auto_rotate_var.get(),
            "pdf_to_pptx.slide_size": self.slide_size_var.get(),
            "pdf_to_pptx.add_page_numbers": self.add_page_numbers_var.get(),
            "output.create_subfolder": self.create_subfolder_var.get(),
            "output.overwrite_existing": self.overwrite_var.get()
        }


class ProgressPanel(ctk.CTkFrame):
    """進捗表示パネルコンポーネント"""

    def __init__(self, master, **kwargs):
        """初期化"""
        super().__init__(master, **kwargs)

        self._setup_ui()

    def _setup_ui(self):
        """UIセットアップ"""
        self.grid_columnconfigure(0, weight=1)

        # 進捗メッセージ
        self.message_label = ctk.CTkLabel(
            self,
            text="準備中...",
            font=ctk.CTkFont(size=12)
        )
        self.message_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # プログレスバー
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.progress_bar.set(0)

        # パーセント表示
        self.percent_label = ctk.CTkLabel(
            self,
            text="0%",
            font=ctk.CTkFont(size=12)
        )
        self.percent_label.grid(row=1, column=1, padx=10, pady=5)

        # キャンセルボタン
        self.cancel_button = ctk.CTkButton(
            self,
            text="キャンセル",
            width=80,
            height=30
        )
        self.cancel_button.grid(row=1, column=2, padx=10, pady=5)

    def update_progress(self, percentage: float, message: str = ""):
        """進捗更新"""
        self.progress_bar.set(percentage / 100)
        self.percent_label.configure(text=f"{int(percentage)}%")

        if message:
            self.message_label.configure(text=message)

    def reset(self):
        """リセット"""
        self.progress_bar.set(0)
        self.percent_label.configure(text="0%")
        self.message_label.configure(text="準備中...")

    def set_cancel_callback(self, callback: Callable):
        """キャンセルボタンのコールバック設定"""
        self.cancel_button.configure(command=callback)


class OutputFormatSelector(ctk.CTkFrame):
    """出力形式選択コンポーネント"""

    def __init__(self,
                 master,
                 on_format_changed: Optional[Callable[[str], None]] = None,
                 **kwargs):
        """初期化"""
        super().__init__(master, **kwargs)

        self.on_format_changed = on_format_changed
        self._setup_ui()

    def _setup_ui(self):
        """UIセットアップ"""
        # ラベル
        label = ctk.CTkLabel(self, text="出力形式:")
        label.grid(row=0, column=0, padx=(0, 10))

        # 形式選択（デフォルトをPPTXに変更）
        self.format_var = tk.StringVar(value="PPTX")

        # PPTXを最初に配置（推奨）
        pptx_radio = ctk.CTkRadioButton(
            self,
            text="PowerPoint (推奨)",
            variable=self.format_var,
            value="PPTX",
            command=self._on_change
        )
        pptx_radio.grid(row=0, column=1, padx=5)

        png_radio = ctk.CTkRadioButton(
            self,
            text="PNG画像",
            variable=self.format_var,
            value="PNG",
            command=self._on_change
        )
        png_radio.grid(row=0, column=2, padx=5)

    def _on_change(self):
        """変更時の処理"""
        if self.on_format_changed:
            self.on_format_changed(self.format_var.get())

    def get_selected_format(self) -> str:
        """選択された形式を取得"""
        return self.format_var.get()


class ThemeManager:
    """テーマ管理クラス"""

    @staticmethod
    def apply_theme(theme: str = "dark"):
        """テーマを適用"""
        if theme.lower() == "dark":
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("dark-blue")
        elif theme.lower() == "light":
            ctk.set_appearance_mode("light")
            ctk.set_default_color_theme("blue")
        else:
            ctk.set_appearance_mode("system")

    @staticmethod
    def get_current_theme() -> str:
        """現在のテーマを取得"""
        return ctk.get_appearance_mode()