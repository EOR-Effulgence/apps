"""
カスタムテーマ設定
アプリケーション全体のカラーテーマとスタイル定義
"""

import customtkinter as ctk


class ThemeColors:
    """テーマカラー定義"""

    # 深い青のカラーパレット
    DEEP_BLUE = "#1e3a5f"      # メインの深い青
    DEEP_BLUE_HOVER = "#2c4f7c" # ホバー時の青
    DEEP_BLUE_LIGHT = "#2e5090" # ライトモード用の青

    # アクセントカラー
    ACCENT_BLUE = "#4a90e2"
    ACCENT_GREEN = "#27ae60"
    ACCENT_RED = "#e74c3c"

    # 背景色
    BG_DARK = "#1a1a1a"
    BG_LIGHT = "#f5f5f5"

    # テキストカラー
    TEXT_WHITE = "#ffffff"
    TEXT_BLACK = "#333333"
    TEXT_GRAY = "#666666"


class ButtonStyles:
    """ボタンスタイル定義"""

    # 共通設定
    DEFAULT_HEIGHT = 45  # ボタンの高さを統一
    DEFAULT_CORNER_RADIUS = 8
    DEFAULT_FONT_SIZE = 14

    # プライマリボタン（深い青）
    PRIMARY = {
        "fg_color": ThemeColors.DEEP_BLUE,
        "hover_color": ThemeColors.DEEP_BLUE_HOVER,
        "text_color": ThemeColors.TEXT_WHITE,
        "height": DEFAULT_HEIGHT,
        "corner_radius": DEFAULT_CORNER_RADIUS,
        "font": ("Yu Gothic UI", DEFAULT_FONT_SIZE, "bold")
    }

    # セカンダリボタン
    SECONDARY = {
        "fg_color": "transparent",
        "hover_color": ("gray80", "gray30"),
        "border_width": 2,
        "border_color": ThemeColors.DEEP_BLUE,
        "text_color": ("gray10", "gray90"),
        "height": DEFAULT_HEIGHT,
        "corner_radius": DEFAULT_CORNER_RADIUS,
        "font": ("Yu Gothic UI", DEFAULT_FONT_SIZE)
    }

    # 成功ボタン（変換開始など）
    SUCCESS = {
        "fg_color": ThemeColors.ACCENT_GREEN,
        "hover_color": "#229954",
        "text_color": ThemeColors.TEXT_WHITE,
        "height": DEFAULT_HEIGHT,
        "corner_radius": DEFAULT_CORNER_RADIUS,
        "font": ("Yu Gothic UI", DEFAULT_FONT_SIZE, "bold")
    }

    # 危険ボタン（削除など）
    DANGER = {
        "fg_color": ThemeColors.ACCENT_RED,
        "hover_color": "#c0392b",
        "text_color": ThemeColors.TEXT_WHITE,
        "height": DEFAULT_HEIGHT - 5,  # 少し小さめ
        "corner_radius": DEFAULT_CORNER_RADIUS,
        "font": ("Yu Gothic UI", DEFAULT_FONT_SIZE - 1)
    }

    # 小さいボタン
    SMALL = {
        "height": 35,
        "corner_radius": 6,
        "font": ("Yu Gothic UI", 12)
    }

    # 大きいボタン
    LARGE = {
        "height": 55,
        "corner_radius": 10,
        "font": ("Yu Gothic UI", 16, "bold")
    }


class UIConfig:
    """UI設定定義"""

    # レイアウト設定
    WINDOW_MIN_WIDTH = 900
    WINDOW_MIN_HEIGHT = 700
    WINDOW_DEFAULT_WIDTH = 1100
    WINDOW_DEFAULT_HEIGHT = 750

    # パディング
    PADDING_LARGE = 20
    PADDING_MEDIUM = 15
    PADDING_SMALL = 10
    PADDING_TINY = 5

    # 間隔
    SPACING_LARGE = 20
    SPACING_MEDIUM = 15
    SPACING_SMALL = 10

    # コンポーネントサイズ
    SIDEBAR_WIDTH = 350  # サイドバー幅を広げる
    HEADER_HEIGHT = 70
    FOOTER_HEIGHT = 40

    # ボタンの最小幅（文字が切れないように）
    BUTTON_MIN_WIDTH = {
        "small": 100,
        "medium": 150,
        "large": 200,
        "xlarge": 250
    }


def apply_custom_theme():
    """カスタムテーマを適用"""

    # カスタムテーマの登録
    ctk.ThemeManager.theme["CTkButton"] = {
        "corner_radius": ButtonStyles.DEFAULT_CORNER_RADIUS,
        "border_width": 0,
        "fg_color": [ThemeColors.DEEP_BLUE_LIGHT, ThemeColors.DEEP_BLUE],
        "hover_color": [ThemeColors.ACCENT_BLUE, ThemeColors.DEEP_BLUE_HOVER],
        "text_color": [ThemeColors.TEXT_WHITE, ThemeColors.TEXT_WHITE]
    }

    # フォント設定
    ctk.set_default_color_theme("dark-blue")


def create_button(parent, text: str, style: str = "primary", width: str = "medium", **kwargs):
    """
    スタイル付きボタンを作成

    Args:
        parent: 親ウィジェット
        text: ボタンテキスト
        style: ボタンスタイル ("primary", "secondary", "success", "danger")
        width: ボタン幅 ("small", "medium", "large", "xlarge")
        **kwargs: 追加のオプション
    """
    # スタイル取得
    style_dict = {
        "primary": ButtonStyles.PRIMARY,
        "secondary": ButtonStyles.SECONDARY,
        "success": ButtonStyles.SUCCESS,
        "danger": ButtonStyles.DANGER
    }.get(style, ButtonStyles.PRIMARY)

    # 幅の設定
    button_width = UIConfig.BUTTON_MIN_WIDTH.get(width, UIConfig.BUTTON_MIN_WIDTH["medium"])

    # スタイルとカスタム設定をマージ
    button_config = style_dict.copy()
    button_config["width"] = button_width
    button_config.update(kwargs)

    return ctk.CTkButton(parent, text=text, **button_config)


class ResponsiveGrid:
    """レスポンシブグリッドレイアウトヘルパー"""

    @staticmethod
    def configure_main_grid(widget):
        """メイングリッドの設定"""
        widget.grid_columnconfigure(0, weight=1)  # メインコンテンツ
        widget.grid_columnconfigure(1, weight=0, minsize=UIConfig.SIDEBAR_WIDTH)  # サイドバー
        widget.grid_rowconfigure(0, weight=0, minsize=UIConfig.HEADER_HEIGHT)  # ヘッダー
        widget.grid_rowconfigure(1, weight=1)  # メインコンテンツ
        widget.grid_rowconfigure(2, weight=0, minsize=UIConfig.FOOTER_HEIGHT)  # フッター

    @staticmethod
    def configure_content_grid(widget):
        """コンテンツエリアのグリッド設定"""
        widget.grid_columnconfigure(0, weight=1)
        widget.grid_rowconfigure(0, weight=1)  # ファイルドロップゾーン
        widget.grid_rowconfigure(1, weight=2)  # ファイルリスト
        widget.grid_rowconfigure(2, weight=0)  # アクションボタン