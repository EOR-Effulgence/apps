"""
CSV2XLSX Converter - Unified GUI Application
統合された最適なユーザーエクスペリエンスを提供するGUIアプリケーション
"""

import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import sys
import math
from pathlib import Path
from typing import List, Optional, Callable
from src import converter

# CustomTkinterの設定
ctk.set_appearance_mode("light")  # ライトモード固定

# カスタムカラーテーマ（深い落ち着いた色）
DEEP_BLUE = "#2C3E50"  # 深い青
MEDIUM_BLUE = "#34495E"  # 中間の青
LIGHT_GRAY = "#ECF0F1"  # 薄いグレー
ACCENT_GREEN = "#27AE60"  # アクセント緑


class AnimatedButton(ctk.CTkButton):
    """ホバー時にアニメーションするボタン"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.default_size = kwargs.get('width', 120), kwargs.get('height', 50)
        self.is_animating = False
        self.bind("<Enter>", self.on_hover_enter)
        self.bind("<Leave>", self.on_hover_leave)

    def on_hover_enter(self, event):
        if not self.is_animating:
            self.is_animating = True
            self.animate_scale(1.0, 1.05, 150)

    def on_hover_leave(self, event):
        if self.is_animating:
            self.is_animating = False
            self.animate_scale(1.05, 1.0, 150)

    def animate_scale(self, start_scale, end_scale, duration):
        steps = 10
        step_duration = duration // steps
        scale_diff = end_scale - start_scale

        for i in range(steps + 1):
            scale = start_scale + (scale_diff * (i / steps))
            new_width = int(self.default_size[0] * scale)
            new_height = int(self.default_size[1] * scale)
            self.after(i * step_duration, lambda w=new_width, h=new_height:
                      self.configure(width=w, height=h))


class SlideInNotification(ctk.CTkToplevel):
    """スライドイン通知システム"""

    def __init__(self, master, message: str, type: str = "info", duration: int = 3000):
        super().__init__(master)
        self.master_window = master
        self.duration = duration

        # ウィンドウ設定
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # 透明度の設定
        if master.tk.call('tk', 'windowingsystem') == 'win32':
            self.attributes("-alpha", 0.0)

        # 色とアイコンの設定
        colors = {
            "success": ("#10B981", "white"),
            "error": ("#EF4444", "white"),
            "warning": ("#F59E0B", "white"),
            "info": ("#3B82F6", "white")
        }
        icons = {"success": "✓", "error": "✕", "warning": "⚠", "info": "ℹ"}

        bg_color, text_color = colors.get(type, colors["info"])
        icon = icons.get(type, "ℹ")

        # UI構築
        self.notification_frame = ctk.CTkFrame(
            self, corner_radius=12, fg_color=bg_color, border_width=0
        )
        self.notification_frame.pack(padx=5, pady=5)

        content_frame = ctk.CTkFrame(self.notification_frame, fg_color="transparent")
        content_frame.pack(padx=15, pady=12)

        # アイコンとメッセージ
        ctk.CTkLabel(
            content_frame, text=icon, font=ctk.CTkFont(size=20, weight="bold"),
            text_color=text_color
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            content_frame, text=message, font=ctk.CTkFont(size=14), text_color=text_color
        ).pack(side="left")

        # 閉じるボタン
        ctk.CTkButton(
            content_frame, text="✕", width=20, height=20, font=ctk.CTkFont(size=12),
            fg_color="transparent", text_color=text_color,
            hover_color=(bg_color[0], bg_color[0]), command=self.close_notification
        ).pack(side="right", padx=(20, 0))

        self.slide_in()

    def slide_in(self):
        """スライドインアニメーション"""
        self.update_idletasks()
        final_x = self.master_window.winfo_x() + self.master_window.winfo_width() - self.winfo_width() - 20
        final_y = self.master_window.winfo_y() + 80
        start_x = self.master_window.winfo_x() + self.master_window.winfo_width() + 10
        self.geometry(f"+{start_x}+{final_y}")

        steps = 15
        duration = 300
        step_duration = duration // steps

        for i in range(steps + 1):
            ratio = self.ease_out_cubic(i / steps)
            x = int(start_x - (start_x - final_x) * ratio)
            alpha = i / steps
            self.after(i * step_duration, lambda x=x, a=alpha: self.update_position(x, final_y, a))

        self.after(duration + self.duration, self.slide_out)

    def slide_out(self):
        """スライドアウトアニメーション"""
        if not self.winfo_exists():
            return
        current_x, current_y = self.winfo_x(), self.winfo_y()
        final_x = self.master_window.winfo_x() + self.master_window.winfo_width() + 10

        for i in range(16):
            ratio = self.ease_in_cubic(i / 15)
            x = int(current_x + (final_x - current_x) * ratio)
            alpha = 1 - (i / 15)
            self.after(i * 20, lambda x=x, a=alpha: self.update_position(x, current_y, a))

        self.after(320, self.destroy)

    def update_position(self, x, y, alpha):
        if self.winfo_exists():
            self.geometry(f"+{x}+{y}")
            if self.tk.call('tk', 'windowingsystem') == 'win32':
                self.attributes("-alpha", alpha)

    def close_notification(self):
        self.slide_out()

    @staticmethod
    def ease_out_cubic(t):
        return 1 - pow(1 - t, 3)

    @staticmethod
    def ease_in_cubic(t):
        return t * t * t


class CircularProgressBar(ctk.CTkCanvas):
    """円形プログレスバー"""

    def __init__(self, master, size=100, thickness=10, **kwargs):
        super().__init__(master, width=size, height=size, **kwargs)
        self.size = size
        self.thickness = thickness
        self.progress = 0
        self.configure(highlightthickness=0)
        self.bg_color = "#E5E5E5"
        self.fg_color = ACCENT_GREEN
        self.draw()

    def set_progress(self, value: float):
        self.progress = max(0, min(1, value))
        self.draw()

    def draw(self):
        self.delete("all")
        center = self.size // 2
        radius = (self.size - self.thickness) // 2

        # 背景の円
        self.create_oval(
            center - radius, center - radius, center + radius, center + radius,
            outline=self.bg_color, width=self.thickness, fill=""
        )

        # プログレスの円弧
        if self.progress > 0:
            extent = -360 * self.progress
            self.create_arc(
                center - radius, center - radius, center + radius, center + radius,
                outline=self.fg_color, width=self.thickness, fill="",
                start=90, extent=extent, style="arc"
            )

        # パーセンテージテキスト
        percentage = int(self.progress * 100)
        self.create_text(
            center, center, text=f"{percentage}%",
            font=("Arial", int(self.size * 0.2), "bold"), fill=self.fg_color
        )


class CSV2XLSXApp(ctk.CTk, TkinterDnD.DnDWrapper):
    """統合されたCSV/Excel変換アプリケーション"""

    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        # ウィンドウ設定
        self.title("CSV2XLSX 変換ツール")
        self.geometry("650x800")
        self.minsize(600, 450)

        # 状態管理
        self.file_list: List[str] = []
        self.conversion_mode: Optional[str] = None
        self.pulse_animation_running = False
        self.pulse_counter = 0

        # UI構築
        self.setup_ui()

    def setup_ui(self):
        """UIコンポーネントのセットアップ"""
        # メインコンテナ
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_header()
        self.create_drop_area()
        self.create_file_list()
        self.create_options()
        self.create_action_area()
        self.create_status_bar()

    def create_header(self):
        """ヘッダー部分の作成"""
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        # タイトル
        ctk.CTkLabel(
            header_frame, text="CSV ⇄ Excel 変換ツール",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        # ヘルプボタン
        ctk.CTkButton(
            header_frame, text="?", width=30, height=30,
            font=ctk.CTkFont(size=14), command=self.show_help
        ).pack(side="right")

    def create_drop_area(self):
        """ドラッグ&ドロップエリアの作成"""
        drop_frame = ctk.CTkFrame(
            self.main_container, height=150, corner_radius=15,
            border_width=2, border_color="#C0C0C0"
        )
        drop_frame.pack(fill="x", pady=(0, 20))
        drop_frame.pack_propagate(False)

        self.drop_label = ctk.CTkLabel(
            drop_frame, text="📁 ファイルをここにドラッグ&ドロップ",
            font=ctk.CTkFont(size=20)
        )
        self.drop_label.pack(expand=True, pady=(20, 10))

        ctk.CTkLabel(
            drop_frame, text="CSVファイル → Excel | Excelファイル → CSVファイル",
            font=ctk.CTkFont(size=14), text_color="#666666"
        ).pack()

        self.browse_button = AnimatedButton(
            drop_frame, text="ファイルを選択", width=150, height=35,
            corner_radius=20, command=self.browse_files
        )
        self.browse_button.pack(pady=(10, 20))

        # ドラッグ&ドロップ設定
        drop_frame.drop_target_register(DND_FILES)
        drop_frame.dnd_bind('<<Drop>>', self.on_drop)
        drop_frame.bind("<Enter>", lambda e: self.on_drop_hover(drop_frame, True))
        drop_frame.bind("<Leave>", lambda e: self.on_drop_hover(drop_frame, False))

    def create_file_list(self):
        """ファイルリストの作成"""
        list_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, pady=(0, 20))

        ctk.CTkLabel(
            list_frame, text="変換するファイル",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(0, 10))

        self.file_scroll_frame = ctk.CTkScrollableFrame(
            list_frame, height=180, corner_radius=10
        )
        self.file_scroll_frame.pack(fill="both", expand=True)

        self.empty_list_label = ctk.CTkLabel(
            self.file_scroll_frame, text="ファイルが選択されていません",
            font=ctk.CTkFont(size=14), text_color="#888888"
        )
        self.empty_list_label.pack(pady=50)

        self.file_cards = {}

    def create_options(self):
        """オプション設定エリアの作成"""
        options_frame = ctk.CTkFrame(self.main_container, height=100, corner_radius=10)
        options_frame.pack(fill="x", pady=(0, 20))
        options_frame.pack_propagate(False)

        ctk.CTkLabel(
            options_frame, text="オプション",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))

        options_content = ctk.CTkFrame(options_frame, fg_color="transparent")
        options_content.pack(fill="x", padx=20)

        # エンコーディング選択
        ctk.CTkLabel(
            options_content, text="出力エンコーディング (Excel→CSV):",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=(0, 10))

        self.encoding_var = ctk.StringVar(value="UTF-8 (BOM付き)")
        self.encoding_menu = ctk.CTkOptionMenu(
            options_content, values=["UTF-8 (BOM付き)", "Shift_JIS"],
            variable=self.encoding_var, width=180, height=35, corner_radius=8,
            fg_color=MEDIUM_BLUE, button_color=DEEP_BLUE, button_hover_color=MEDIUM_BLUE
        )
        self.encoding_menu.pack(side="left")

        # 出力フォルダ選択
        self.output_folder_button = ctk.CTkButton(
            options_content, text="📂 出力フォルダを選択",
            width=150, height=35, command=self.choose_output_folder,
            fg_color=MEDIUM_BLUE, hover_color=DEEP_BLUE
        )
        self.output_folder_button.pack(side="left", padx=(20, 0))

        self.output_folder_path = ctk.StringVar(value="入力ファイルと同じフォルダ")
        self.output_info_label = ctk.CTkLabel(
            options_content, textvariable=self.output_folder_path,
            font=ctk.CTkFont(size=12), text_color="#777777"
        )
        self.output_info_label.pack(side="right", padx=(20, 0))

    def create_action_area(self):
        """実行ボタンとプログレスバーエリアの作成"""
        action_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        action_frame.pack(fill="x", pady=(0, 10))

        # 変換ボタン（深い色でカスタマイズ）
        self.convert_button = ctk.CTkButton(
            action_frame, text="ファイルを変換",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45, corner_radius=12, command=self.start_conversion,
            fg_color=DEEP_BLUE, hover_color=MEDIUM_BLUE
        )
        self.convert_button.pack(fill="x")

        # プログレスバー
        self.progress_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        progress_container = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        progress_container.pack(fill="x", pady=(20, 5))

        self.progress_bar = ctk.CTkProgressBar(
            progress_container, height=15, corner_radius=10
        )
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=(0, 20))
        self.progress_bar.set(0)

        self.circular_progress = CircularProgressBar(progress_container, size=60, thickness=6)
        self.circular_progress.pack(side="right")

        self.progress_label = ctk.CTkLabel(
            self.progress_frame, text="", font=ctk.CTkFont(size=12)
        )
        self.progress_label.pack()

    def create_status_bar(self):
        """ステータスバーの作成"""
        self.status_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.status_frame.pack(fill="x", side="bottom")

        self.status_label = ctk.CTkLabel(
            self.status_frame, text="準備完了", font=ctk.CTkFont(size=12), anchor="w"
        )
        self.status_label.pack(side="left", padx=10)

        ctk.CTkLabel(
            self.status_frame, text="v2.0.0", font=ctk.CTkFont(size=12), anchor="e"
        ).pack(side="right", padx=10)

    def choose_output_folder(self):
        """出力フォルダ選択"""
        folder = filedialog.askdirectory(title="出力フォルダを選択")
        if folder:
            self.output_folder_path.set(folder)

    def on_drop(self, event):
        """ファイルドロップ時の処理"""
        files = self.tk.splitlist(event.data)
        self.drop_label.configure(
            text="✅ ファイルが追加されました！", text_color="#10B981"
        )
        self.after(1000, lambda: self.drop_label.configure(
            text="📁 ファイルをここにドラッグ&ドロップ", text_color="black"
        ))
        self.add_files(files)

    def on_drop_hover(self, widget, entering):
        """ドロップエリアのホバーエフェクト"""
        if entering:
            widget.configure(border_color="#3B82F6", border_width=3)
            self.drop_label.configure(
                text="📂 今すぐファイルをドロップ！", text_color="#3B82F6"
            )
            self.start_pulse_animation(widget)
        else:
            widget.configure(border_color="#C0C0C0", border_width=2)
            self.drop_label.configure(
                text="📁 ファイルをここにドラッグ&ドロップ", text_color="black"
            )
            self.stop_pulse_animation()

    def start_pulse_animation(self, widget):
        """脈動アニメーション開始"""
        self.pulse_animation_running = True
        self.pulse_counter = 0
        self.animate_pulse(widget)

    def stop_pulse_animation(self):
        """脈動アニメーション停止"""
        self.pulse_animation_running = False

    def animate_pulse(self, widget):
        """脈動アニメーション実行"""
        if not self.pulse_animation_running:
            return
        self.pulse_counter = (self.pulse_counter + 0.15) % (2 * math.pi)
        alpha = (math.sin(self.pulse_counter) + 1) / 2 * 0.3 + 0.7
        try:
            intensity = int(255 * alpha)
            color = f"#{60:02x}{intensity:02x}{250:02x}"
            widget.configure(border_color=(color, color))
        except:
            pass
        self.after(50, lambda: self.animate_pulse(widget))

    def browse_files(self):
        """ファイル選択ダイアログ"""
        filetypes = (
            ("サポートされているファイル", "*.csv *.xlsx"),
            ("CSVファイル", "*.csv"),
            ("Excelファイル", "*.xlsx"),
            ("すべてのファイル", "*.*")
        )
        files = filedialog.askopenfilenames(title="ファイルを選択", filetypes=filetypes)
        if files:
            self.add_files(files)

    def add_files(self, files: List[str]):
        """ファイルをリストに追加"""
        csv_files = [f for f in files if f.lower().endswith('.csv')]
        xlsx_files = [f for f in files if f.lower().endswith('.xlsx')]

        if csv_files and not xlsx_files:
            self.conversion_mode = "csv_to_xlsx"
            self.file_list = csv_files
        elif xlsx_files and not csv_files:
            if len(xlsx_files) == 1:
                self.conversion_mode = "xlsx_to_csv"
                self.file_list = xlsx_files
            else:
                self.show_error("CSV変換用にはExcelファイルを1つだけ選択してください。")
                return
        else:
            self.show_error("CSVファイルまたはExcelファイル（1つ）のいずれかを選択してください。両方は選択できません。")
            return

        self.update_file_list_ui()
        self.update_status(f"{len(self.file_list)}個のファイルを追加しました")

    def update_file_list_ui(self):
        """ファイルリストUIの更新"""
        for card in self.file_cards.values():
            card.destroy()
        self.file_cards.clear()

        if self.empty_list_label:
            self.empty_list_label.destroy()
            self.empty_list_label = None

        for i, filepath in enumerate(self.file_list):
            self.create_file_card(filepath, i)

    def create_file_card(self, filepath: str, index: int):
        """ファイルカードの作成"""
        filename = os.path.basename(filepath)
        filesize = self.format_filesize(os.path.getsize(filepath))

        card = ctk.CTkFrame(self.file_scroll_frame, height=60, corner_radius=10)
        card.pack(fill="x", padx=5, pady=5)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)

        # アイコン
        ctk.CTkLabel(
            info_frame, text="📄" if filepath.endswith('.csv') else "📊",
            font=ctk.CTkFont(size=24)
        ).pack(side="left", padx=(0, 10))

        # ファイル情報
        text_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            text_frame, text=filename, font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_frame, text=filesize, font=ctk.CTkFont(size=12),
            text_color="#777777", anchor="w"
        ).pack(anchor="w")

        # 削除ボタン
        ctk.CTkButton(
            card, text="✕", width=30, height=30, font=ctk.CTkFont(size=16),
            fg_color="transparent", hover_color=("gray80", "gray30"),
            command=lambda: self.remove_file(index)
        ).pack(side="right", padx=10)

        self.file_cards[index] = card

    def format_filesize(self, size: int) -> str:
        """ファイルサイズフォーマット"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def remove_file(self, index: int):
        """ファイル削除"""
        if 0 <= index < len(self.file_list):
            self.file_list.pop(index)
            self.update_file_list_ui()
            if not self.file_list:
                self.conversion_mode = None
                self.create_empty_list_label()

    def create_empty_list_label(self):
        """空リストラベル作成"""
        if not self.empty_list_label:
            self.empty_list_label = ctk.CTkLabel(
                self.file_scroll_frame, text="ファイルが選択されていません",
                font=ctk.CTkFont(size=14), text_color="#888888"
            )
            self.empty_list_label.pack(pady=50)

    def show_help(self):
        """ヘルプ表示"""
        help_text = """CSV2XLSX 変換ツール v2.1

使用方法:
1. ファイルをドラッグ&ドロップまたは「ファイルを選択」ボタンをクリック
2. 必要に応じて変換オプションを選択
3. 「🚀 ファイルを変換」ボタンをクリックして開始

サポートされている変換:
• 複数CSV → 単一Excel（複数シート）
• 単一Excel → 複数CSVファイル

エンコーディングオプション:
• UTF-8 (BOM付き) - 推奨、Excel互換
• Shift_JIS - 日本語Windows互換

その他の機能:
• 📂 出力フォルダ選択
• ⚡ リアルタイム進捗表示
• 🎨 見やすいライトモードデザイン"""
        messagebox.showinfo("ヘルプ", help_text)

    def start_conversion(self):
        """変換開始"""
        if not self.file_list:
            self.show_error("変換するファイルを選択してください。")
            return

        self.set_ui_state(False)
        self.progress_frame.pack(fill="x", pady=(20, 0))
        self.progress_bar.set(0)
        threading.Thread(target=self.run_conversion).start()

    def run_conversion(self):
        """変換実行"""
        try:
            if self.conversion_mode == "csv_to_xlsx":
                output_folder = self.output_folder_path.get()
                if output_folder == "入力ファイルと同じフォルダ":
                    output_file = os.path.splitext(self.file_list[0])[0] + ".xlsx"
                else:
                    filename = os.path.splitext(os.path.basename(self.file_list[0]))[0] + ".xlsx"
                    output_file = os.path.join(output_folder, filename)

                converter.csv_to_xlsx(
                    self.file_list, output_file, progress_callback=self.update_progress
                )
                self.show_success(f"変換完了: {os.path.basename(output_file)}")

            elif self.conversion_mode == "xlsx_to_csv":
                input_file = self.file_list[0]
                output_folder = self.output_folder_path.get()
                if output_folder == "入力ファイルと同じフォルダ":
                    output_dir = os.path.dirname(input_file)
                else:
                    output_dir = output_folder

                encoding_choice = self.encoding_var.get()
                if "UTF-8" in encoding_choice:
                    encoding = 'utf-8'  # BOM付きはconverterで自動処理
                else:
                    encoding = 'shift_jis'
                converter.xlsx_to_csv(
                    input_file, output_dir, encoding=encoding,
                    progress_callback=self.update_progress
                )
                self.show_success(f"CSVファイルを作成しました: {output_dir}")

        except Exception as e:
            self.show_error(f"変換に失敗しました: {str(e)}")
        finally:
            self.after(0, lambda: self.set_ui_state(True))
            self.after(0, lambda: self.progress_frame.pack_forget())

    def update_progress(self, current: int, total: int):
        """プログレス更新"""
        progress = current / total if total > 0 else 0

        def update_ui():
            self.progress_bar.set(progress)
            self.circular_progress.set_progress(progress)
            self.progress_label.configure(
                text=f"処理中: {current}/{total} ({int(progress * 100)}%)"
            )

        self.after(0, update_ui)

    def set_ui_state(self, enabled: bool):
        """UI状態切り替え"""
        state = "normal" if enabled else "disabled"
        self.browse_button.configure(state=state)
        self.convert_button.configure(state=state)
        self.encoding_menu.configure(state=state)

    def update_status(self, message: str):
        """ステータス更新"""
        self.status_label.configure(text=message)

    def show_error(self, message: str):
        """エラー表示"""
        SlideInNotification(self, message, "error")

    def show_success(self, message: str):
        """成功表示"""
        SlideInNotification(self, message, "success")


def main():
    """メインエントリーポイント"""
    app = CSV2XLSXApp()
    app.mainloop()


if __name__ == "__main__":
    main()