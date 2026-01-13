"""
設定管理
環境変数からAPIキーなどを読み込む
"""
import os
from typing import Optional

def get_gemini_api_key() -> Optional[str]:
    """Gemini APIキーを環境変数から取得"""
    return os.getenv("GEMINI_API_KEY")

def get_google_sheets_id() -> Optional[str]:
    """Google Sheets IDを環境変数から取得（後で使用）"""
    return os.getenv("GOOGLE_SHEETS_ID")

def get_google_sheets_credentials_path() -> Optional[str]:
    """Google Sheets認証情報のパスを環境変数から取得（後で使用）"""
    return os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
