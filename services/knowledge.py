# ナレッジ（ガイドライン）読み込みサービス
import os
from typing import Optional


def load_default_guidelines() -> Optional[str]:
    """
    デフォルトのガイドラインを読み込む。
    data/guidelines.md を返す。存在しなければ None。
    """
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, "..", "data", "guidelines.md")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def load_guidelines_from_text(content: Optional[str]) -> Optional[str]:
    """アップロードや入力テキストからガイドラインを受け取り、そのまま返す。"""
    if not content:
        return None
    text = content.strip()
    return text if text else None


def resolve_guidelines(upload_text: Optional[str] = None) -> Optional[str]:
    """
    ガイドラインを決定する。
    優先順位: アップロード/入力 > デフォルトファイル。
    """
    return load_guidelines_from_text(upload_text) or load_default_guidelines()
