"""
講座データ読み込みサービス
Google Sheets / CSVファイルから講座データを読み込む
"""
import os
import csv
import io
from typing import List, Dict, Optional
from config import get_google_sheets_id, get_google_sheets_credentials


def load_from_google_sheets() -> Optional[str]:
    """
    Google Sheetsから講座データを読み込む
    
    Returns:
        CSV形式の講座データ文字列、またはNone
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        sheets_id = get_google_sheets_id()
        credentials_dict = get_google_sheets_credentials()
        
        if not sheets_id or not credentials_dict:
            return None
        
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # 認証情報の辞書からCredentialsオブジェクトを作成
        creds = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        # スプレッドシートを開く
        spreadsheet = client.open_by_key(sheets_id)
        worksheet = spreadsheet.sheet1  # 最初のシートを取得
        
        # データを取得
        values = worksheet.get_all_values()
        
        if not values:
            return None
        
        # CSV形式の文字列に変換
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(values)
        return output.getvalue()
        
    except ImportError:
        # gspreadがインストールされていない場合
        return None
    except Exception as e:
        print(f"Google Sheets読み込みエラー: {e}")
        return None


def load_from_csv_file(csv_content: str) -> Optional[str]:
    """
    アップロードされたCSVコンテンツからデータを読み込む
    
    Args:
        csv_content: CSVファイルの内容（文字列）
    
    Returns:
        CSV形式の講座データ文字列、またはNone
    """
    try:
        # 文字列をそのまま返す（検証は必要に応じて追加）
        if csv_content and len(csv_content.strip()) > 0:
            return csv_content
        return None
    except Exception as e:
        print(f"CSV読み込みエラー: {e}")
        return None


def load_from_default_csv() -> Optional[str]:
    """
    デフォルトのCSVファイルから講座データを読み込む
    
    Returns:
        CSV形式の講座データ文字列、またはNone
    """
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'courses.csv')
    
    try:
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return None
    except Exception as e:
        print(f"デフォルトCSV読み込みエラー: {e}")
        return None


def load_course_data() -> Optional[str]:
    """
    講座データを読み込む（優先順位：Google Sheets > デフォルトCSV）
    
    Returns:
        CSV形式の講座データ文字列、またはNone
    """
    # 優先順位1: Google Sheets（環境変数が設定されている場合）
    data = load_from_google_sheets()
    if data:
        return data
    
    # 優先順位2: デフォルトCSV
    return load_from_default_csv()


def search_courses(query: str) -> List[Dict]:
    """
    講座データを検索する
    後で実装：現在は空のリストを返す
    
    Args:
        query: 検索クエリ
    
    Returns:
        講座データのリスト
    """
    # TODO: 講座データから検索して該当するものを返す
    return []
