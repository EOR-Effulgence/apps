"""
メインウィンドウ
customtkinterベースのGUIメインウィンドウ実装
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import List, Optional, Dict, Any
import threading
import queue
from loguru import logger
import sys
import os

# 親ディレクトリをパスに追加
sys.path.append(str(Path(__file__).parent.parent))

try:
    from utils.config import ConfigManager
    from utils.error_handler import ErrorHandler, ErrorType
    from core.conversion_service import ConversionService, ConversionType
    from gui.components import FileDropZone, SettingsPanel, ProgressPanel, OutputFormatSelector
    from gui.theme import ThemeColors, ButtonStyles, UIConfig, create_button, ResponsiveGrid, apply_custom_theme
except ImportError:
    # 絶対インポートにフォールバック
    from src.utils.config import ConfigManager
    from src.utils.error_handler import ErrorHandler, ErrorType
    from src.core.conversion_service import ConversionService, ConversionType
    from src.gui.components import FileDropZone, SettingsPanel, ProgressPanel, OutputFormatSelector
    from src.gui.theme import ThemeColors, ButtonStyles, UIConfig, create_button, ResponsiveGrid, apply_custom_theme


class MainWindow(ctk.CTk):
    """メインウィンドウクラス"""

    def __init__(self):
        """初期化"""
        super().__init__()

        # 設定とサービスの初期化
        self.config_manager = ConfigManager()
        self.error_handler = ErrorHandler(ui_callback=self.show_error_dialog)
        self.conversion_service = ConversionService(self.config_manager)

        # 状態管理
        self.selected_files: List[Path] = []
        self.output_directory: Optional[Path] = None
        self.is_converting = False
        self.conversion_thread: Optional[threading.Thread] = None
        self.progress_queue = queue.Queue()

        # ウィンドウ設定
        self._setup_window()

        # UI構築
        self._setup_ui()

        # イベントバインディング
        self._bind_events()

        logger.info("メインウィンドウを初期化しました")

    def _setup_window(self):
        """ウィンドウの基本設定"""
        # タイトルとサイズ
        self.title("PDF2PPTX v3.0 - PDF変換ツール")

        # ウィンドウサイズ
        window_config = self.config_manager.get_config("ui.window_size")
        if window_config:
            width, height = window_config
        else:
            width, height = 900, 700

        self.geometry(f"{width}x{height}")

        # 最小サイズ
        self.minsize(600, 500)

        # アイコン設定（存在する場合）
        icon_path = Path("assets/icon.ico")
        if icon_path.exists():
            self.iconbitmap(str(icon_path))

        # 中央配置
        self.center_window()

    def center_window(self):
        """ウィンドウを画面中央に配置"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _setup_ui(self):
        """UIコンポーネントの構築"""
        # グリッド設定
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ヘッダー
        self._create_header()

        # メインコンテンツエリア
        self._create_main_content()

        # フッター（ステータスバー）
        self._create_footer()

    def _create_header(self):
        """ヘッダー部分の作成"""
        header_frame = ctk.CTkFrame(self, height=60, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(1, weight=1)

        # ロゴ/タイトル
        title_label = ctk.CTkLabel(
            header_frame,
            text="PDF2PPTX Converter",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=15)

        # テーマ切り替えボタン
        self.theme_button = ctk.CTkButton(
            header_frame,
            text="🌙",
            width=40,
            height=40,
            command=self.toggle_theme,
            font=ctk.CTkFont(size=20)
        )
        self.theme_button.grid(row=0, column=2, padx=20, pady=10)

    def _create_main_content(self):
        """メインコンテンツエリアの作成"""
        # メインコンテナ
        main_frame = ctk.CTkFrame(self, corner_radius=0)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=0)
        main_frame.grid_rowconfigure(0, weight=1)

        # 左側：ファイル選択・変換エリア
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)

        # ファイルドロップゾーン
        self.drop_zone = FileDropZone(
            left_frame,
            on_files_dropped=self.on_files_dropped,
            accepted_extensions=[".pdf"]
        )
        self.drop_zone.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # ファイルリスト
        self._create_file_list(left_frame)

        # 変換ボタンエリア
        self._create_action_buttons(left_frame)

        # 右側：設定パネル
        self.settings_panel = SettingsPanel(
            main_frame,
            config_manager=self.config_manager,
            on_settings_changed=self.on_settings_changed
        )
        self.settings_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # 進捗表示パネル（初期は非表示）
        self.progress_panel = ProgressPanel(main_frame)
        # self.progress_panel.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=10)
        # 初期は非表示にしておく

    def _create_file_list(self, parent):
        """ファイルリストの作成"""
        list_frame = ctk.CTkFrame(parent)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)

        # ラベル
        list_label = ctk.CTkLabel(
            list_frame,
            text="選択されたファイル:",
            anchor="w",
            font=ctk.CTkFont(size=14)
        )
        list_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        # スクロール可能なテキストボックス
        self.file_list = ctk.CTkTextbox(
            list_frame,
            height=150,
            state="disabled"
        )
        self.file_list.grid(row=1, column=0, sticky="nsew")

        # クリアボタン
        clear_button = ctk.CTkButton(
            list_frame,
            text="クリア",
            width=80,
            command=self.clear_file_list
        )
        clear_button.grid(row=2, column=0, sticky="e", pady=5)

    def _create_action_buttons(self, parent):
        """アクションボタンの作成"""
        button_frame = ctk.CTkFrame(parent)
        button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        button_frame.grid_columnconfigure(1, weight=1)

        # ファイル選択ボタン
        self.select_button = ctk.CTkButton(
            button_frame,
            text="📁 ファイルを選択",
            width=150,
            height=40,
            command=self.select_files,
            font=ctk.CTkFont(size=14)
        )
        self.select_button.grid(row=0, column=0, padx=5)

        # 出力フォーマット選択
        self.format_selector = OutputFormatSelector(
            button_frame,
            on_format_changed=self.on_format_changed
        )
        self.format_selector.grid(row=0, column=1, padx=5)

        # 変換開始ボタン
        self.convert_button = ctk.CTkButton(
            button_frame,
            text="▶ 変換開始",
            width=150,
            height=40,
            command=self.start_conversion,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.convert_button.grid(row=0, column=2, padx=5)

    def _create_footer(self):
        """フッター（ステータスバー）の作成"""
        footer_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        footer_frame.grid_columnconfigure(1, weight=1)

        # ステータスラベル
        self.status_label = ctk.CTkLabel(
            footer_frame,
            text="準備完了",
            anchor="w"
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=5)

        # バージョン情報
        version_label = ctk.CTkLabel(
            footer_frame,
            text="v3.0.0",
            anchor="e"
        )
        version_label.grid(row=0, column=2, padx=10, pady=5)

    def _bind_events(self):
        """イベントバインディング"""
        # ウィンドウ閉じるイベント
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # キーボードショートカット
        self.bind("<Control-o>", lambda e: self.select_files())
        self.bind("<Control-Return>", lambda e: self.start_conversion())
        self.bind("<Escape>", lambda e: self.cancel_conversion())

    def on_files_dropped(self, files: List[Path]):
        """ファイルがドロップされた時の処理"""
        try:
            # PDFファイルのみフィルタリング
            pdf_files = [f for f in files if f.suffix.lower() == '.pdf']

            if not pdf_files:
                self.show_warning("対応していないファイル形式です。PDFファイルを選択してください。")
                return

            # ファイルリストに追加
            self.selected_files.extend(pdf_files)
            self.update_file_list()
            self.update_status(f"{len(pdf_files)} ファイルを追加しました")

            logger.info(f"ファイルドロップ: {len(pdf_files)} ファイル")

        except Exception as e:
            logger.error(f"ファイルドロップエラー: {e}")
            self.show_error(f"ファイル処理エラー: {str(e)}")

    def select_files(self):
        """ファイル選択ダイアログ"""
        try:
            # 最後のディレクトリを取得
            last_dir = self.config_manager.get_config("ui.last_directory")
            initial_dir = last_dir if last_dir and Path(last_dir).exists() else str(Path.home())

            files = filedialog.askopenfilenames(
                title="PDFファイルを選択",
                initialdir=initial_dir,
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )

            if files:
                pdf_files = [Path(f) for f in files]
                self.selected_files.extend(pdf_files)
                self.update_file_list()
                self.update_status(f"{len(pdf_files)} ファイルを選択しました")

                # 最後のディレクトリを保存
                self.config_manager.set_config(
                    "ui.last_directory",
                    str(pdf_files[0].parent)
                )

                logger.info(f"ファイル選択: {len(pdf_files)} ファイル")

        except Exception as e:
            logger.error(f"ファイル選択エラー: {e}")
            self.show_error(f"ファイル選択エラー: {str(e)}")

    def update_file_list(self):
        """ファイルリストの更新"""
        self.file_list.configure(state="normal")
        self.file_list.delete("1.0", tk.END)

        for i, file in enumerate(self.selected_files, 1):
            self.file_list.insert(tk.END, f"{i}. {file.name}\n")

        self.file_list.configure(state="disabled")

    def clear_file_list(self):
        """ファイルリストのクリア"""
        self.selected_files.clear()
        self.update_file_list()
        self.update_status("ファイルリストをクリアしました")

    def on_format_changed(self, format_type: str):
        """出力フォーマット変更時の処理"""
        logger.info(f"出力フォーマット変更: {format_type}")
        self.update_status(f"出力形式: {format_type}")

    def on_settings_changed(self, settings: Dict[str, Any]):
        """設定変更時の処理"""
        logger.info(f"設定変更: {settings}")
        # 設定を保存
        for key, value in settings.items():
            self.config_manager.set_config(f"conversion.{key}", value, save=False)
        self.config_manager.save_config()

    def start_conversion(self):
        """変換処理の開始"""
        if self.is_converting:
            self.show_warning("変換処理が実行中です")
            return

        if not self.selected_files:
            self.show_warning("PDFファイルを選択してください")
            return

        try:
            # 出力ディレクトリ選択
            output_dir = filedialog.askdirectory(
                title="出力先フォルダを選択",
                initialdir=str(Path.home())
            )

            if not output_dir:
                return

            self.output_directory = Path(output_dir)

            # 変換タイプを取得
            format_type = self.format_selector.get_selected_format()
            if format_type == "PNG":
                conversion_type = ConversionType.PDF_TO_PNG
            else:
                conversion_type = ConversionType.PDF_TO_PPTX

            # UI更新
            self.is_converting = True
            self.convert_button.configure(text="⏸ 処理中...", state="disabled")
            self.select_button.configure(state="disabled")

            # 進捗パネル表示
            self.progress_panel.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=10)
            self.progress_panel.reset()

            # 別スレッドで変換実行
            self.conversion_thread = threading.Thread(
                target=self._run_conversion,
                args=(conversion_type,),
                daemon=True
            )
            self.conversion_thread.start()

            # 進捗更新タイマー開始
            self.after(100, self._check_progress)

        except Exception as e:
            logger.error(f"変換開始エラー: {e}")
            self.show_error(f"変換開始エラー: {str(e)}")
            self.reset_conversion_state()

    def _run_conversion(self, conversion_type: ConversionType):
        """変換処理の実行（別スレッド）"""
        try:
            total_files = len(self.selected_files)
            completed = 0

            for i, pdf_file in enumerate(self.selected_files, 1):
                # 進捗更新
                self.progress_queue.put({
                    "current": i,
                    "total": total_files,
                    "message": f"処理中: {pdf_file.name}",
                    "percentage": (i - 1) / total_files * 100
                })

                # 変換実行
                if conversion_type == ConversionType.PDF_TO_PNG:
                    result = self.conversion_service.convert_pdf_to_png(
                        pdf_path=pdf_file,
                        output_dir=self.output_directory / pdf_file.stem
                    )
                else:
                    result = self.conversion_service.convert_pdf_to_pptx(
                        pdf_path=pdf_file,
                        output_path=self.output_directory / f"{pdf_file.stem}.pptx"
                    )

                if result and result.success:
                    completed += 1

                # 進捗更新
                self.progress_queue.put({
                    "current": i,
                    "total": total_files,
                    "message": f"完了: {pdf_file.name}",
                    "percentage": i / total_files * 100
                })

            # 完了通知
            self.progress_queue.put({
                "completed": True,
                "success_count": completed,
                "total_count": total_files
            })

        except Exception as e:
            logger.error(f"変換処理エラー: {e}")
            self.progress_queue.put({
                "error": str(e)
            })

    def _check_progress(self):
        """進捗確認と更新"""
        try:
            while not self.progress_queue.empty():
                progress = self.progress_queue.get_nowait()

                if "error" in progress:
                    self.show_error(f"変換エラー: {progress['error']}")
                    self.reset_conversion_state()
                    return

                elif "completed" in progress:
                    success = progress["success_count"]
                    total = progress["total_count"]
                    self.show_info(f"変換完了: {success}/{total} ファイル")
                    self.reset_conversion_state()
                    return

                else:
                    # 進捗更新
                    self.progress_panel.update_progress(
                        progress.get("percentage", 0),
                        progress.get("message", "")
                    )
                    self.update_status(progress.get("message", ""))

        except queue.Empty:
            pass

        # 変換中は継続
        if self.is_converting:
            self.after(100, self._check_progress)

    def cancel_conversion(self):
        """変換処理のキャンセル"""
        if self.is_converting:
            # TODO: 変換処理のキャンセル実装
            self.show_warning("キャンセル処理は未実装です")

    def reset_conversion_state(self):
        """変換状態のリセット"""
        self.is_converting = False
        self.convert_button.configure(text="▶ 変換開始", state="normal")
        self.select_button.configure(state="normal")
        self.progress_panel.grid_remove()

    def toggle_theme(self):
        """テーマ切り替え"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)

        # ボタンアイコン更新
        self.theme_button.configure(text="☀" if new_mode == "Light" else "🌙")

        # 設定保存
        self.config_manager.set_config("ui.theme", new_mode.lower())

    def update_status(self, message: str):
        """ステータスバー更新"""
        self.status_label.configure(text=message)

    def show_error(self, message: str):
        """エラーメッセージ表示"""
        messagebox.showerror("エラー", message)

    def show_warning(self, message: str):
        """警告メッセージ表示"""
        messagebox.showwarning("警告", message)

    def show_info(self, message: str):
        """情報メッセージ表示"""
        messagebox.showinfo("情報", message)

    def show_error_dialog(self, error_info: Dict[str, str], level):
        """エラーダイアログ表示（ErrorHandlerコールバック）"""
        self.show_error(f"{error_info.get('title', 'エラー')}\n{error_info.get('message', '')}")

    def on_closing(self):
        """ウィンドウを閉じる時の処理"""
        if self.is_converting:
            if messagebox.askokcancel("確認", "変換処理中です。終了しますか？"):
                self.destroy()
        else:
            self.destroy()


if __name__ == "__main__":
    # テスト実行
    app = MainWindow()
    app.mainloop()