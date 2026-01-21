"""
設定管理
Streamlit Secrets / 環境変数からAPIキーなどを読み込む
"""
import os
import json
from typing import Optional, Dict, Any
import streamlit as st

def _get_from_secrets_or_env(key: str) -> Optional[str]:
    """
    Streamlit Secretsを優先、なければ環境変数から取得
    """
    try:
        # Streamlit Secretsから取得を試みる
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    
    # 環境変数から取得
    return os.getenv(key)

def get_gemini_api_key() -> Optional[str]:
    """Gemini APIキーをStreamlit Secrets / 環境変数から取得"""
    return _get_from_secrets_or_env("GEMINI_API_KEY")

def get_google_sheets_id() -> Optional[str]:
    """Google Sheets IDをStreamlit Secrets / 環境変数から取得"""
    return _get_from_secrets_or_env("GOOGLE_SHEETS_ID")

def get_google_sheets_credentials() -> Optional[Dict[str, Any]]:
    """
    Google Sheets認証情報を取得
    Streamlit SecretsにJSON文字列がある場合はそれを使用、
    なければファイルパスから読み込む
    
    Returns:
        認証情報の辞書、またはNone
    """
    # 方法1: Streamlit SecretsにJSON文字列がある場合
    try:
        if hasattr(st, 'secrets') and 'GOOGLE_SHEETS_CREDENTIALS' in st.secrets:
            creds_str = st.secrets['GOOGLE_SHEETS_CREDENTIALS']
            if isinstance(creds_str, str):
                return json.loads(creds_str)
            elif isinstance(creds_str, dict):
                return creds_str
    except:
        pass
    
    # 方法2: ファイルパスが指定されている場合
    credentials_path = _get_from_secrets_or_env("GOOGLE_SHEETS_CREDENTIALS_PATH")
    if credentials_path and os.path.exists(credentials_path):
        try:
            with open(credentials_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"認証ファイル読み込みエラー: {e}")
            return None
    
    return None
