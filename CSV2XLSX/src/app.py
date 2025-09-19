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
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class AnimatedButton(ctk.CTkButton):
    """ホバー時にアニメーションするボタン"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.default_size = kwargs.get('width', 100), kwargs.get('height', 40)
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
        self.fg_color = "#3B82F6"
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
        self.title("CSV2XLSX Converter Pro")
        self.geometry("900x700")
        self.minsize(800, 600)

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
            header_frame, text="CSV ⇄ Excel Converter Pro",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(side="left")

        # テーマ切り替えボタン
        self.theme_button = ctk.CTkButton(
            header_frame, text="🌙", width=40, height=40,
            font=ctk.CTkFont(size=20), command=self.toggle_theme
        )
        self.theme_button.pack(side="right", padx=(10, 0))

        # ヘルプボタン
        ctk.CTkButton(
            header_frame, text="?", width=40, height=40,
            font=ctk.CTkFont(size=18), command=self.show_help
        ).pack(side="right", padx=(10, 0))

    def create_drop_area(self):
        """ドラッグ&ドロップエリアの作成"""
        drop_frame = ctk.CTkFrame(
            self.main_container, height=150, corner_radius=15,
            border_width=2, border_color=("gray50", "gray30")
        )
        drop_frame.pack(fill="x", pady=(0, 20))
        drop_frame.pack_propagate(False)

        self.drop_label = ctk.CTkLabel(
            drop_frame, text="📁 Drag & Drop Files Here",
            font=ctk.CTkFont(size=20)
        )
        self.drop_label.pack(expand=True, pady=(20, 10))

        ctk.CTkLabel(
            drop_frame, text="CSV files → Excel | Excel file → CSV files",
            font=ctk.CTkFont(size=14), text_color=("gray60", "gray40")
        ).pack()

        self.browse_button = AnimatedButton(
            drop_frame, text="Browse Files", width=150, height=35,
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
            list_frame, text="Files to Convert",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(0, 10))

        self.file_scroll_frame = ctk.CTkScrollableFrame(
            list_frame, height=200, corner_radius=10
        )
        self.file_scroll_frame.pack(fill="both", expand=True)

        self.empty_list_label = ctk.CTkLabel(
            self.file_scroll_frame, text="No files selected",
            font=ctk.CTkFont(size=14), text_color=("gray60", "gray40")
        )
        self.empty_list_label.pack(pady=50)

        self.file_cards = {}

    def create_options(self):
        """オプション設定エリアの作成"""
        options_frame = ctk.CTkFrame(self.main_container, height=100, corner_radius=10)
        options_frame.pack(fill="x", pady=(0, 20))
        options_frame.pack_propagate(False)

        ctk.CTkLabel(
            options_frame, text="Options",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))

        options_content = ctk.CTkFrame(options_frame, fg_color="transparent")
        options_content.pack(fill="x", padx=20)

        # エンコーディング選択
        ctk.CTkLabel(
            options_content, text="Output Encoding (Excel→CSV):",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=(0, 10))

        self.encoding_var = ctk.StringVar(value="UTF-8")
        self.encoding_menu = ctk.CTkOptionMenu(
            options_content, values=["UTF-8", "Shift_JIS"],
            variable=self.encoding_var, width=150, height=35, corner_radius=8
        )
        self.encoding_menu.pack(side="left")

        # 出力フォルダ選択
        self.output_folder_button = ctk.CTkButton(
            options_content, text="📂 Choose Output Folder",
            width=150, height=35, command=self.choose_output_folder
        )
        self.output_folder_button.pack(side="left", padx=(20, 0))

        self.output_folder_path = ctk.StringVar(value="Same as input files")
        self.output_info_label = ctk.CTkLabel(
            options_content, textvariable=self.output_folder_path,
            font=ctk.CTkFont(size=12), text_color=("gray60", "gray40")
        )
        self.output_info_label.pack(side="right", padx=(20, 0))

    def create_action_area(self):
        """実行ボタンとプログレスバーエリアの作成"""
        action_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        action_frame.pack(fill="x", pady=(0, 10))

        # 変換ボタン
        self.convert_button = AnimatedButton(
            action_frame, text="🚀 Convert Files",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=50, width=300, corner_radius=25, command=self.start_conversion
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
            self.status_frame, text="Ready", font=ctk.CTkFont(size=12), anchor="w"
        )
        self.status_label.pack(side="left", padx=10)

        ctk.CTkLabel(
            self.status_frame, text="v2.0.0", font=ctk.CTkFont(size=12), anchor="e"
        ).pack(side="right", padx=10)

    def choose_output_folder(self):
        """出力フォルダ選択"""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder_path.set(folder)

    def on_drop(self, event):
        """ファイルドロップ時の処理"""
        files = self.tk.splitlist(event.data)
        self.drop_label.configure(
            text="✅ Files Added!", text_color=("#10B981", "#34D399")
        )
        self.after(1000, lambda: self.drop_label.configure(
            text="📁 Drag & Drop Files Here", text_color=("black", "white")
        ))
        self.add_files(files)

    def on_drop_hover(self, widget, entering):
        """ドロップエリアのホバーエフェクト"""
        if entering:
            widget.configure(border_color=("#3B82F6", "#60A5FA"), border_width=3)
            self.drop_label.configure(
                text="📂 Drop Files Now!", text_color=("#3B82F6", "#60A5FA")
            )
            self.start_pulse_animation(widget)
        else:
            widget.configure(border_color=("gray50", "gray30"), border_width=2)
            self.drop_label.configure(
                text="📁 Drag & Drop Files Here", text_color=("black", "white")
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
            ("Supported files", "*.csv *.xlsx"),
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx"),
            ("All files", "*.*")
        )
        files = filedialog.askopenfilenames(title="Select files", filetypes=filetypes)
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
                self.show_error("Please select only one Excel file for conversion to CSV.")
                return
        else:
            self.show_error("Please select either CSV files or one Excel file, not both.")
            return

        self.update_file_list_ui()
        self.update_status(f"Added {len(self.file_list)} file(s)")

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
            text_color=("gray60", "gray40"), anchor="w"
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
                self.file_scroll_frame, text="No files selected",
                font=ctk.CTkFont(size=14), text_color=("gray60", "gray40")
            )
            self.empty_list_label.pack(pady=50)

    def toggle_theme(self):
        """テーマ切り替え"""
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_button.configure(text="☀️")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_button.configure(text="🌙")

    def show_help(self):
        """ヘルプ表示"""
        help_text = """CSV2XLSX Converter Pro v2.0

How to use:
1. Drag & drop files or click 'Browse Files'
2. Select conversion options if needed
3. Click 'Convert Files' to start

Supported conversions:
• Multiple CSV → Single Excel (multiple sheets)
• Single Excel → Multiple CSV files

Encoding options:
• UTF-8 (recommended)
• Shift_JIS (for Japanese Windows compatibility)"""
        messagebox.showinfo("Help", help_text)

    def start_conversion(self):
        """変換開始"""
        if not self.file_list:
            self.show_error("Please select files to convert.")
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
                if output_folder == "Same as input files":
                    output_file = os.path.splitext(self.file_list[0])[0] + ".xlsx"
                else:
                    filename = os.path.splitext(os.path.basename(self.file_list[0]))[0] + ".xlsx"
                    output_file = os.path.join(output_folder, filename)

                converter.csv_to_xlsx(
                    self.file_list, output_file, progress_callback=self.update_progress
                )
                self.show_success(f"Successfully created: {os.path.basename(output_file)}")

            elif self.conversion_mode == "xlsx_to_csv":
                input_file = self.file_list[0]
                output_folder = self.output_folder_path.get()
                if output_folder == "Same as input files":
                    output_dir = os.path.dirname(input_file)
                else:
                    output_dir = output_folder

                encoding = self.encoding_var.get().lower().replace('_', '-')
                converter.xlsx_to_csv(
                    input_file, output_dir, encoding=encoding,
                    progress_callback=self.update_progress
                )
                self.show_success(f"CSV files created in: {output_dir}")

        except Exception as e:
            self.show_error(f"Conversion failed: {str(e)}")
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
                text=f"Processing: {current}/{total} ({int(progress * 100)}%)"
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