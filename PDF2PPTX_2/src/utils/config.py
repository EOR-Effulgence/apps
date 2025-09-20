"""
設定管理システム
JSON形式での設定保存・読み込み、デフォルト値管理
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

class ConfigManager:
    """設定管理クラス"""

    DEFAULT_CONFIG_FILE = "config.json"
    DEFAULT_CONFIG_DIR = Path.home() / ".pdf2pptx"

    DEFAULT_CONFIG = {
        "conversion": {
            "pdf_to_png": {
                "dpi": 150,
                "scale": 1.5,
                "auto_rotate": True,
                "quality": "high"
            },
            "pdf_to_pptx": {
                "slide_size": [420, 297],  # A3横 (mm)
                "font_name": "メイリオ",
                "font_size": 14,
                "text_color": "#FFFFFF",
                "background_color": "#1976D2",
                "label_position": "top_left",
                "add_page_numbers": True
            },
            "output": {
                "create_subfolder": True,
                "subfolder_prefix": "converted",
                "overwrite_existing": False,
                "default_format": "PPTX"  # デフォルト出力フォーマットをPPTXに設定
            }
        },
        "ui": {
            "theme": "system",  # system/light/dark
            "language": "ja",
            "window_size": [800, 600],
            "remember_last_directory": True,
            "last_directory": "",
            "show_preview": True,
            "animation_enabled": True
        },
        "performance": {
            "max_concurrent_conversions": 3,
            "memory_limit_mb": 500,
            "temp_dir": "",  # 空の場合はシステムデフォルト
            "cleanup_temp_files": True
        },
        "logging": {
            "level": "INFO",
            "file_enabled": True,
            "max_log_size_mb": 10,
            "log_retention_days": 7
        }
    }

    def __init__(self, config_file: Optional[str] = None):
        """
        初期化

        Args:
            config_file: 設定ファイルパス（省略時はデフォルト）
        """
        if config_file:
            self.config_path = Path(config_file)
        else:
            self.config_path = self.DEFAULT_CONFIG_DIR / self.DEFAULT_CONFIG_FILE

        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """
        設定ファイルを読み込み

        Returns:
            設定辞書
        """
        try:
            # 設定ディレクトリが存在しない場合は作成
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # デフォルト値とマージ（新しい設定項目への対応）
                    self.config = self._merge_configs(self.DEFAULT_CONFIG, loaded_config)
                    logger.info(f"設定ファイルを読み込みました: {self.config_path}")
            else:
                # 設定ファイルが存在しない場合はデフォルト設定を使用
                self.config = self.DEFAULT_CONFIG.copy()
                self.save_config()  # デフォルト設定を保存
                logger.info(f"デフォルト設定ファイルを作成しました: {self.config_path}")

        except json.JSONDecodeError as e:
            logger.error(f"設定ファイルの解析に失敗: {e}")
            logger.warning("デフォルト設定を使用します")
            self.config = self.DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.error(f"設定ファイル読み込みエラー: {e}")
            self.config = self.DEFAULT_CONFIG.copy()

        return self.config

    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        設定をファイルに保存

        Args:
            config: 保存する設定（省略時は現在の設定）

        Returns:
            保存成功時True
        """
        if config:
            self.config = config

        try:
            # 設定ディレクトリが存在しない場合は作成
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)

            logger.info(f"設定を保存しました: {self.config_path}")
            return True

        except Exception as e:
            logger.error(f"設定保存エラー: {e}")
            return False

    def get_config(self, key_path: str = None) -> Any:
        """
        設定値を取得

        Args:
            key_path: ドット区切りのキーパス（例: "conversion.pdf_to_png.dpi"）

        Returns:
            指定されたキーの値、またはキーが存在しない場合はNone
        """
        if not key_path:
            return self.config

        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                logger.debug(f"設定キーが見つかりません: {key_path}")
                return None

        return value

    def set_config(self, key_path: str, value: Any, save: bool = True) -> bool:
        """
        設定値を更新

        Args:
            key_path: ドット区切りのキーパス
            value: 設定する値
            save: 即座にファイルに保存するか

        Returns:
            更新成功時True
        """
        try:
            keys = key_path.split('.')
            target = self.config

            # 最後のキー以外を辿る
            for key in keys[:-1]:
                if key not in target:
                    target[key] = {}
                target = target[key]

            # 値を設定
            target[keys[-1]] = value

            if save:
                return self.save_config()

            return True

        except Exception as e:
            logger.error(f"設定更新エラー: {e}")
            return False

    def get_default_config(self) -> Dict[str, Any]:
        """
        デフォルト設定を取得

        Returns:
            デフォルト設定の辞書
        """
        return self.DEFAULT_CONFIG.copy()

    def reset_config(self, save: bool = True) -> bool:
        """
        設定をデフォルトにリセット

        Args:
            save: 即座にファイルに保存するか

        Returns:
            リセット成功時True
        """
        self.config = self.DEFAULT_CONFIG.copy()

        if save:
            return self.save_config()

        return True

    def _merge_configs(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """
        デフォルト設定と読み込んだ設定をマージ

        Args:
            default: デフォルト設定
            loaded: 読み込んだ設定

        Returns:
            マージされた設定
        """
        merged = default.copy()

        for key, value in loaded.items():
            if key in merged:
                if isinstance(value, dict) and isinstance(merged[key], dict):
                    merged[key] = self._merge_configs(merged[key], value)
                else:
                    merged[key] = value
            else:
                merged[key] = value

        return merged

    def validate_config(self) -> bool:
        """
        設定の妥当性を検証

        Returns:
            検証成功時True
        """
        try:
            # DPI値の検証
            dpi = self.get_config("conversion.pdf_to_png.dpi")
            if not isinstance(dpi, int) or dpi < 50 or dpi > 600:
                logger.warning(f"不正なDPI値: {dpi}, デフォルト値を使用します")
                self.set_config("conversion.pdf_to_png.dpi", 150, save=False)

            # スケール値の検証
            scale = self.get_config("conversion.pdf_to_png.scale")
            if not isinstance(scale, (int, float)) or scale < 0.5 or scale > 3.0:
                logger.warning(f"不正なスケール値: {scale}, デフォルト値を使用します")
                self.set_config("conversion.pdf_to_png.scale", 1.5, save=False)

            # メモリ制限の検証
            memory_limit = self.get_config("performance.memory_limit_mb")
            if not isinstance(memory_limit, int) or memory_limit < 100 or memory_limit > 4000:
                logger.warning(f"不正なメモリ制限値: {memory_limit}, デフォルト値を使用します")
                self.set_config("performance.memory_limit_mb", 500, save=False)

            return True

        except Exception as e:
            logger.error(f"設定検証エラー: {e}")
            return False