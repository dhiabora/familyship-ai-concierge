"""
Gemini LLM呼び出しサービス
"""
import google.generativeai as genai
from typing import Optional, List
from config import get_gemini_api_key
from prompts import SYSTEM_PROMPT


def initialize_gemini() -> bool:
    """Gemini APIを初期化"""
    api_key = get_gemini_api_key()
    if not api_key:
        return False
    genai.configure(api_key=api_key)
    return True


def list_available_models() -> List[str]:
    """利用可能なモデル一覧を取得"""
    try:
        api_key = get_gemini_api_key()
        if not api_key:
            return []
        genai.configure(api_key=api_key)
        models = genai.list_models()
        model_names = []
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                # モデル名から 'models/' プレフィックスを削除（GenerativeModelには不要）
                name = m.name.replace('models/', '')
                model_names.append(name)
        return model_names
    except Exception as e:
        return []


def generate_response(user_input: str, course_data: Optional[str] = None) -> str:
    """
    ユーザーの入力に対してGeminiで回答を生成
    
    Args:
        user_input: ユーザーの悩み・質問
        course_data: 講座データ（CSV形式、後で実装時に対応）
    
    Returns:
        AIが生成した回答テキスト
    """
    # Gemini APIの初期化
    api_key = get_gemini_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY環境変数が設定されていません")
    
    genai.configure(api_key=api_key)
    
    # モデルの設定（優先順位に従って試す）
    preferred_models = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-pro',
    ]
    
    model = None
    last_error = None
    
    # まず利用可能なモデル一覧を取得して、その中から優先モデルを選ぶ
    try:
        available_models = list_available_models()
        if available_models:
            for preferred in preferred_models:
                if preferred in available_models:
                    try:
                        model = genai.GenerativeModel(preferred)
                        break
                    except:
                        continue
    except:
        pass
    
    # 利用可能なモデル一覧から選べなかった場合、直接試す
    if model is None:
        for model_name in preferred_models:
            try:
                model = genai.GenerativeModel(model_name)
                break
            except Exception as e:
                last_error = e
                continue
    
    if model is None:
        # エラーメッセージに利用可能なモデルを含める
        error_msg = "モデルの初期化に失敗しました。\n"
        try:
            available = list_available_models()
            if available:
                error_msg += f"利用可能なモデル: {', '.join(available[:10])}\n"
        except:
            pass
        if last_error:
            error_msg += f"エラー詳細: {str(last_error)}"
        raise ValueError(error_msg)
    
    # プロンプトの構築
    if course_data:
        # 後で実装: 講座データを含める場合
        prompt = f"""{SYSTEM_PROMPT}

# 講座データベース（CSV形式）
{course_data}

上記の講座データベースを参考に、以下のユーザーの悩みに対して適切な講座を2〜3件提案してください。

ユーザーの悩み：
{user_input}
"""
    else:
        # データがない場合でも、一般的なアドバイスを提供
        prompt = f"""{SYSTEM_PROMPT}

ユーザーの悩み：
{user_input}

上記の悩みに対して、優しく共感しながら応答してください。名前を呼ぶ必要はありません。温かくサポートする姿勢で回答してください。
"""
    
    # 回答生成（エラー時は別のモデルを試す）
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # エラーが発生した場合、利用可能な他のモデルを試す
        error_str = str(e)
        if "404" in error_str or "not found" in error_str.lower():
            try:
                available_models = list_available_models()
                if available_models:
                    # 利用可能なモデルを順に試す
                    for alt_model_name in available_models:
                        try:
                            alt_model = genai.GenerativeModel(alt_model_name)
                            response = alt_model.generate_content(prompt)
                            return response.text
                        except:
                            continue
            except:
                pass
        
        # すべての試行が失敗した場合
        try:
            available = list_available_models()
            if available:
                error_msg = f"モデルの呼び出しに失敗しました。\n利用可能なモデル: {', '.join(available[:5])}\nエラー: {error_str}"
            else:
                error_msg = f"モデルの呼び出しに失敗しました: {error_str}"
        except:
            error_msg = f"モデルの呼び出しに失敗しました: {error_str}"
        raise ValueError(error_msg)
