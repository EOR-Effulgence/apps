"""
PDF2PPTX v3.0 - アプリケーション起動スクリプト
"""

import sys
from pathlib import Path

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import main

if __name__ == "__main__":
    sys.exit(main())