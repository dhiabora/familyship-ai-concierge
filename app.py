"""
Streamlit AIコンシェルジュアプリ
ねんねママのファミリーシップ向けの案内人アプリケーション
"""
import streamlit as st
import os
import base64
from typing import Optional
from dotenv import load_dotenv
from services.llm import generate_response, initialize_gemini
from services.sheets import load_course_data
from services.knowledge import resolve_guidelines
from config import get_gemini_api_key


# ============================================================================
# 設定の外部化（デザイン設定を一括管理）
# ============================================================================

# カラーパレット
COLORS = {
    "pink": "#f6c9d5",
    "mint": "#c7e7e5",
    "navy": "#2d2a32",
    "white": "#ffffff",
    "light_gray": "#f7f7f7",
    "beige": "#FFF4F0",  # 背景色
    "button_pink": "#f6c9d5",  # ボタン背景色
    "button_hover": "#f8aacb",  # ボタンホバー色
    "link": "#0f7b8e",  # リンク色
}

# デザイン設定
DESIGN = {
    "title_icon": "👨‍👩‍👧‍👦",  # タイトル横のアイコン
    "logo_width": 150,  # ロゴの幅（px）
    "container_max_width": 1200,  # コンテナの最大幅（px）
    "border_radius": 18,  # コンテナの角丸（px）
    "button_border_radius": 12,  # ボタンの角丸（px）
    "chat_border_radius": 16,  # チャットメッセージの角丸（px）
}

# アイコンファイル設定
ICONS = {
    "logo_candidates": [
        "concierge_logo.png",
        "assets:concierge_logo.png",
    ],
    "user_icon": "user_icon.png",
    "assistant_icon": "assistant_icon.png",
}

# テキスト設定
TEXTS = {
    "page_title": "ファミリーシップ案内人 - ねんねママのファミリーシップ",
    "main_title": "ファミリーシップ案内人",
    "subtitle": "ねんねママのファミリーシップ - サロン全体のご案内役です。講座案内もアプリ操作もお気軽に。",
    "input_label": "質問や相談を入力してください...",
    "input_placeholder": "例: 3ヶ月の夜泣きに効く講座を教えて / FANTSアプリでライブの視聴URLはどこ？",
    "submit_button": "シップちゃんに案内してもらう",
    "footer": "© ねんねママのファミリーシップ",
    "loading_message": "考えています...",
    "error_message": "エラーが発生しました: {error}",
}

# サイドバー設定
SIDEBAR = {
    "usage_title": "💡 使い方",
    "usage_items": [
        "ファミリーシップのコンテンツ・講座・イベントの案内役です。",
        "FANTSアプリの操作や、どの講座を見ればよいかも案内します。",
    ],
    "examples_title": "✍️ 質問の例",
    "examples": [
        "「○ヶ月の夜泣きに効く講座を教えて」",
        "「FANTSアプリでライブの視聴URLはどこ？」",
        "「離乳食の悩みでどのクラスに相談したらいい？」",
    ],
    "help_text": "Shift+Enterで改行できます",
}

# レスポンシブ設定
RESPONSIVE = {
    "mobile_breakpoint": 768,  # モバイル判定のブレークポイント（px）
    "mobile_padding": "0.75rem 0.5rem",
    "mobile_font_size": "0.95rem",
    "mobile_line_height": "1.6",
    "form_bottom_padding": 200,  # モバイル時の入力フォーム下の余白（px）
}


# ============================================================================
# ユーティリティ関数
# ============================================================================

def get_assets_dir() -> str:
    """
    アセットディレクトリのパスを取得する
    
    Returns:
        str: アセットディレクトリのパス
    """
    return os.path.join(os.path.dirname(__file__), "assets")


def get_custom_icon(role: str) -> Optional[str]:
    """
    カスタムアイコンを取得する
    
    Args:
        role: ロール名（"user" または "assistant"）
    
    Returns:
        str | None: アイコンファイルのパス、存在しない場合はNone
    """
    assets_dir = get_assets_dir()
    icon_path = os.path.join(assets_dir, ICONS.get(f"{role}_icon", f"{role}_icon.png"))
    if os.path.exists(icon_path):
        return icon_path
    return None


def _get_image_base64(image_path: str) -> str:
    """
    画像ファイルをbase64エンコードして返す
    
    Args:
        image_path: 画像ファイルのパス
    
    Returns:
        str: base64エンコードされた画像データ
    """
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""


# ============================================================================
# UI関数（画面表示部分）
# ============================================================================

def render_logo() -> bool:
    """
    アプリのロゴを表示する
    
    Returns:
        bool: ロゴが表示された場合はTrue、そうでない場合はFalse
    """
    assets_dir = get_assets_dir()
    for logo_filename in ICONS["logo_candidates"]:
        logo_path = os.path.join(assets_dir, logo_filename)
        if os.path.exists(logo_path):
            st.image(logo_path, width=DESIGN["logo_width"])
            st.session_state.logo_loaded = True
            return True
    st.session_state.logo_loaded = False
    return False


def render_sidebar():
    """
    サイドバーを表示する
    """
    st.markdown(f"### {SIDEBAR['usage_title']}")
    usage_text = "\n    - ".join([""] + SIDEBAR["usage_items"])
    st.markdown(usage_text)
    st.caption(SIDEBAR["help_text"])

    st.markdown(f"### {SIDEBAR['examples_title']}")
    examples_text = "\n    - ".join([""] + SIDEBAR["examples"])
    st.markdown(examples_text)


def render_header():
    """
    ヘッダー（タイトルと説明）を表示する
    """
    st.title(f"{DESIGN['title_icon']} {TEXTS['main_title']}")
    st.markdown(
        f"<div style='margin-top: 0.75rem;'>{TEXTS['subtitle']}</div>",
        unsafe_allow_html=True
    )
    render_logo()


def render_chat_history():
    """
    チャット履歴を表示する
    """
    if st.session_state.messages:
        for message in st.session_state.messages:
            icon_path = get_custom_icon(message["role"])
            if icon_path:
                with st.chat_message(message["role"], avatar=icon_path):
                    st.markdown(message["content"])
            else:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])


def render_input_form():
    """
    入力フォームを表示する
    """
    with st.form(key="user_input_form", clear_on_submit=True):
        user_input = st.text_area(
            TEXTS["input_label"],
            key="user_input",
            height=80,
            help=SIDEBAR["help_text"],
            placeholder=TEXTS["input_placeholder"]
        )
        submit_button = st.form_submit_button(
            TEXTS["submit_button"],
            use_container_width=True
        )
        # フッターを入力フォーム内に配置
        st.markdown(
            f"<div style='text-align: center; color: rgba(128,128,128,0.5); "
            f"padding: 0.25rem 0; font-size: 0.7rem; margin: 0;'>"
            f"{TEXTS['footer']}"
            f"</div>",
            unsafe_allow_html=True
        )
        return user_input, submit_button


def generate_css() -> str:
    """
    CSSスタイルを生成する
    
    Returns:
        str: CSSスタイルの文字列
    """
    return f"""
<style>
:root {{
    --pink: #f9e8ef;
    --mint: #e7f4f3;
    --navy: {COLORS['navy']};
    --white: {COLORS['white']};
    --light-gray: #fdfbfc;
}}

html, body, .stApp {{
    width: 100%;
    max-width: 100vw;
    background: linear-gradient(135deg, var(--pink) 0%, var(--mint) 100%);
    overflow-x: hidden !important;
    overflow-y: visible !important;
    min-height: 100vh;
}}

.main {{
    background: radial-gradient(circle at 20% 20%, rgba(249,232,239,0.9), transparent 35%),
                radial-gradient(circle at 80% 0%, rgba(231,244,243,0.9), transparent 30%),
                linear-gradient(135deg, var(--pink) 0%, var(--mint) 100%);
    width: 100%;
    max-width: 100vw;
    overflow-x: hidden !important;
    overflow-y: visible !important;
    min-height: 100vh;
}}
section.main > div {{
    background: transparent;
}}
.stApp {{
    color: var(--navy);
}}
.stSidebar {{
    background: {COLORS['beige']};
}}
.block-container {{
    background: {COLORS['beige']};
    border-radius: {DESIGN['border_radius']}px;
    padding: 1rem 1.5rem;
    box-shadow: 0 12px 38px rgba(0,0,0,0.08);
    max-width: {DESIGN['container_max_width']}px;
    width: 100%;
    margin-top: 1.5rem;
    margin-bottom: 0;
    display: flex;
    flex-direction: column;
    min-height: calc(100vh - 2rem);
    overflow-x: hidden !important;
    box-sizing: border-box;
}}
/* タイトル部分のヘッダー被りを防止 */
h1, div:has(> h1), div:has(> img[src*="assistant_icon"]) {{
    margin-top: 1rem !important;
    padding-top: 1rem !important;
    margin-bottom: 0.75rem !important;
}}
/* タイトルの下の説明テキストの間隔を調整 */
h1 + .stMarkdown,
h1 ~ .stMarkdown:first-of-type {{
    margin-top: 0.75rem !important;
    padding-top: 0 !important;
}}
/* 横スクロールを防ぐための包括的な設定 */
* {{
    box-sizing: border-box;
    max-width: 100%;
}}
section[data-testid="stMain"],
section[data-testid="stMain"] > div,
.stApp > div {{
    width: 100% !important;
    max-width: 100vw !important;
    overflow-x: hidden !important;
}}
/* Streamlitのデフォルトヘッダーとの間隔を確保 */
section[data-testid="stMain"] > div:first-child {{
    padding-top: 1.5rem !important;
    margin-top: 0.5rem !important;
}}
section[data-testid="stMain"] > div:first-child > div:first-child {{
    padding-top: 0.2rem !important;
    margin-top: 0.5rem !important;
}}
/* タイトルを含む最初のブロックに余白を追加 */
div[data-testid="stVerticalBlock"]:first-of-type {{
    padding-top: 0.1rem !important;
    margin-top: 0.1rem !important;
}}
/* stVerticalBlockのpadding-topとmargin-topを0.1remに */
div[data-testid="stVerticalBlock"] {{
    padding-top: 0.1rem !important;
    margin-top: 0.1rem !important;
}}
/* チャット履歴エリア（スクロール可能、最大限のスペースを確保） */
div[data-testid="stVerticalBlock"]:has(.stChatMessage) {{
    flex: 1;
    overflow-y: visible;
    padding-bottom: 0.5rem;
    margin-bottom: 0;
    min-height: 0;
}}
/* 入力フォームを下に固定（余白を最小化、背景をベージュに） */
form[data-testid="stForm"] {{
    position: sticky;
    bottom: 0;
    background: {COLORS['beige']} !important;
    padding: 0.75rem;
    border-radius: {DESIGN['button_border_radius']}px;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.08);
    margin-top: 0.5rem;
    margin-bottom: 0;
    z-index: 1000 !important;
    flex-shrink: 0;
    border: 1px solid rgba(255,244,240,1);
}}
/* 入力フォーム内のコンテナもベージュに */
form[data-testid="stForm"] > div {{
    background: {COLORS['beige']} !important;
}}
/* テキストエリアの背景もベージュに */
form[data-testid="stForm"] .stTextArea > div > div > textarea {{
    background: {COLORS['white']} !important;
    border: 1px solid rgba(45,42,50,0.15) !important;
}}
/* 入力フォーム内の要素の余白を削減 */
form[data-testid="stForm"] .stTextArea {{
    margin-bottom: 0.5rem;
}}
form[data-testid="stForm"] .stButton {{
    margin-top: 0;
}}
/* フッターの余白を最小化 */
div:has(> div:contains("©")) {{
    margin-top: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 0.25rem !important;
    margin-bottom: 0 !important;
}}
/* フッターテキストのスタイル */
div:has(> div:contains("©")) div {{
    margin: 0 !important;
    padding: 0.25rem 0 !important;
}}
.stMarkdown a {{
    color: {COLORS['link']};
    text-decoration: none;
    font-weight: 600;
}}
.stMarkdown a:hover {{
    text-decoration: underline;
}}
.stChatMessage {{
    border: 1px solid rgba(45,42,50,0.08);
    background: {COLORS['beige']};
    border-radius: {DESIGN['chat_border_radius']}px;
    padding: 14px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.05);
    overflow: visible;
    margin-bottom: 1rem;
}}
.stChatMessage[data-testid="stChatMessage-user"] {{
    background: linear-gradient(135deg, rgba(249,232,239,0.55), rgba(231,244,243,0.45));
    border-color: rgba(249,232,239,0.8);
}}
.stChatMessage[data-testid="stChatMessage-assistant"] {{
    border-color: rgba(231,244,243,0.9);
}}
/* チャットメッセージのアイコンとテキストの位置を統一 */
.stChatMessage > div {{
    display: flex !important;
    align-items: flex-start !important;
    gap: 12px !important;
    width: 100% !important;
    max-width: 100% !important;
    overflow-x: hidden !important;
}}
/* アイコン部分を上に揃える */
.stChatMessage img,
.stChatMessage > div > div:first-child,
.stChatMessage > div > div:first-child img {{
    margin: 0 !important;
    padding: 0 !important;
    vertical-align: top !important;
    transform: translateY(0) !important;
    flex-shrink: 0 !important;
}}
/* テキスト部分をアイコンと同じ高さに調整 */
.stChatMessage > div > div:last-child,
.stChatMessage .stMarkdown {{
    margin-top: 0 !important;
    padding-top: 0 !important;
    transform: translateY(0) !important;
    width: 100% !important;
    max-width: 100% !important;
    overflow-x: hidden !important;
    word-wrap: break-word !important;
    word-break: break-word !important;
}}
/* テキストの最初の要素の余白を削除 */
.stChatMessage .stMarkdown > p:first-child,
.stChatMessage .stMarkdown > div:first-child,
.stChatMessage .stMarkdown > *:first-child {{
    margin-top: 0 !important;
    padding-top: 0 !important;
    line-height: 1.4 !important;
    word-wrap: break-word !important;
    word-break: break-word !important;
}}
.stButton>button {{
    background: {COLORS['button_pink']} !important;
    color: {COLORS['navy']} !important;
    font-weight: 700;
    border: 1px solid rgba(246, 201, 213, 0.3);
    border-radius: {DESIGN['button_border_radius']}px;
    padding: 0.65rem 1.05rem;
    box-shadow: 0 6px 16px rgba(0,0,0,0.08);
}}
.stButton>button:hover {{
    background: {COLORS['button_hover']} !important;
    color: {COLORS['navy']} !important;
}}
.stTextArea > div > div > textarea, textarea {{
    color: #1f1f1f !important;
    background: var(--white);
    border-radius: {DESIGN['button_border_radius']}px;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
    border: 1px solid rgba(45,42,50,0.1);
}}
.stTextArea label, label {{
    color: var(--navy);
    font-weight: 600;
    margin-top: 0 !important;
    padding-top: 0 !important;
    margin-bottom: 0.25rem !important;
}}
/* 質問入力欄のラベルの上の余白を削減 */
form[data-testid="stForm"] .stTextArea label,
form[data-testid="stForm"] label {{
    margin-top: 0 !important;
    padding-top: 0 !important;
    margin-bottom: 0.25rem !important;
}}
.stTextInput>div>div>input {{
    background: var(--white);
}}
/* レスポンシブ対応：モバイル表示時の調整 */
@media screen and (max-width: {RESPONSIVE['mobile_breakpoint']}px) {{
    html, body, .stApp, .main {{
        width: 100% !important;
        max-width: 100vw !important;
        overflow-x: hidden !important;
        overflow-y: visible !important;
        height: auto !important;
        min-height: 100vh;
    }}
    .block-container {{
        padding: {RESPONSIVE['mobile_padding']};
        margin-top: 0.5rem;
        margin-bottom: 0 !important;
        border-radius: 12px;
        padding-bottom: 0 !important;
        width: 100% !important;
        max-width: 100vw !important;
        overflow-x: hidden !important;
        overflow-y: visible !important;
        box-sizing: border-box !important;
        min-height: auto !important;
        height: auto !important;
    }}
    /* モバイルで1行の文字数を増やす */
    .stMarkdown,
    .stMarkdown p,
    .stMarkdown div,
    .stChatMessage .stMarkdown,
    .stChatMessage .stMarkdown p {{
        font-size: {RESPONSIVE['mobile_font_size']} !important;
        line-height: {RESPONSIVE['mobile_line_height']} !important;
        word-break: keep-all !important;
        overflow-wrap: break-word !important;
    }}
    /* チャットメッセージの幅を最大限に */
    .stChatMessage {{
        width: 100% !important;
        max-width: 100% !important;
        padding: 12px !important;
    }}
    /* サイドバーの幅を調整 */
    .stSidebar {{
        padding: {RESPONSIVE['mobile_padding']} !important;
    }}
    /* 入力フォームをモバイルで確実に前面に、画面最下部に固定 */
    form[data-testid="stForm"] {{
        background: {COLORS['beige']} !important;
        padding: 0.75rem !important;
        padding-bottom: 0.5rem !important;
        border-radius: 12px 12px 0 0 !important;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.12) !important;
        z-index: 1000 !important;
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 !important;
        margin-bottom: 0 !important;
    }}
    /* モバイルで入力フォームの背景をベージュに */
    form[data-testid="stForm"] > div,
    form[data-testid="stForm"] .stTextArea,
    form[data-testid="stForm"] .stTextArea > div,
    form[data-testid="stForm"] .stTextArea > div > div {{
        background: {COLORS['beige']} !important;
    }}
    form[data-testid="stForm"] .stTextArea > div > div > textarea {{
        background: {COLORS['white']} !important;
    }}
    /* フッターの余白を完全に削除（モバイル） */
    form[data-testid="stForm"] div:has(> div:contains("©")),
    form[data-testid="stForm"] div:has(> div:contains("©")) div {{
        margin: 0 !important;
        padding: 0.15rem 0 !important;
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }}
    /* 入力フォームの下の余白を完全に削除 */
    form[data-testid="stForm"] + *,
    form[data-testid="stForm"] ~ * {{
        margin-top: 0 !important;
        padding-top: 0 !important;
        display: none !important;
    }}
    /* 入力フォームの直下のすべての要素を非表示 */
    form[data-testid="stForm"]::after {{
        display: none !important;
        content: none !important;
    }}
    /* チャット履歴エリアに下部の余白を追加（入力フォームの高さ分） */
    div[data-testid="stVerticalBlock"]:has(.stChatMessage) {{
        padding-bottom: {RESPONSIVE['form_bottom_padding']}px !important;
        margin-bottom: 0 !important;
        overflow-y: visible !important;
    }}
    /* メインコンテンツの下部余白を追加 */
    .block-container {{
        padding-bottom: {RESPONSIVE['form_bottom_padding']}px !important;
        margin-bottom: 0 !important;
        overflow-y: visible !important;
    }}
    /* 入力フォームの下に表示される可能性のある要素を非表示 */
    section[data-testid="stMain"] > div:last-child,
    section[data-testid="stMain"] > div:last-child > div:last-child,
    section[data-testid="stMain"] > div:last-child > div:last-child > div {{
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }}
    /* Streamlitのデフォルトの下部余白を削除 */
    .main {{
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }}
    /* 入力フォームの親要素の余白も削除 */
    form[data-testid="stForm"] {{
        margin-bottom: 0 !important;
        padding-bottom: 0.5rem !important;
    }}
    /* 入力フォーム内の最後の要素の余白を削除 */
    form[data-testid="stForm"] > div:last-child {{
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }}
    /* 画面最下部の余白を完全に削除 */
    section[data-testid="stMain"],
    section[data-testid="stMain"] > div,
    .element-container:last-child,
    .stMarkdown:last-child {{
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }}
    /* 入力フォームの下の白いスペースを削除 */
    div[data-testid="stVerticalBlock"]:has(form[data-testid="stForm"]) ~ * {{
        display: none !important;
    }}
    h1 {{
        font-size: 1.75rem !important;
    }}
    /* モバイルでもサイドバーを表示可能にする */
    .stSidebar {{
        display: block !important;
        z-index: 999 !important;
    }}
    /* モバイルでサイドバーが開いた時のスタイル */
    [data-testid="stSidebar"][aria-expanded="true"] {{
        min-width: 85vw !important;
        max-width: 85vw !important;
    }}
    /* ページ全体の下部余白を削除 */
    body, html {{
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }}
}}
/* ロゴのスタイル調整（見切れ防止、画像の品質向上） */
div[data-testid="stVerticalBlock"]:has(img[src*="concierge_logo"]),
div:has(img[src*="concierge_logo"]) {{
    margin-top: 1rem;
    margin-bottom: 1rem;
    text-align: center;
}}
div:has(img[src*="concierge_logo"]) img {{
    max-width: {DESIGN['logo_width']}px;
    width: {DESIGN['logo_width']}px;
    height: auto;
    object-fit: contain;
    image-rendering: -webkit-optimize-contrast;
    image-rendering: crisp-edges;
    image-rendering: auto;
}}
</style>
"""


# ============================================================================
# ロジック関数（AIとの通信部分）
# ============================================================================

@st.cache_data
def get_course_data():
    """
    講座データを取得する（キャッシュ機能付き）
    
    Returns:
        str | None: CSV形式の講座データ、取得できない場合はNone
    """
    return load_course_data()


@st.cache_data
def get_default_guidelines():
    """
    デフォルトのガイドラインを取得する（キャッシュ機能付き）
    
    Returns:
        str: ガイドラインテキスト
    """
    return resolve_guidelines()


def initialize_session_state():
    """
    セッション状態を初期化する
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "guidelines" not in st.session_state:
        st.session_state.guidelines = get_default_guidelines()
    if "logo_loaded" not in st.session_state:
        st.session_state.logo_loaded = False


def process_user_message(user_input: str) -> str:
    """
    ユーザーメッセージを処理し、AI応答を生成する
    
    Args:
        user_input: ユーザーの入力テキスト
    
    Returns:
        str: AIが生成した応答テキスト
    
    Raises:
        Exception: AI応答生成時にエラーが発生した場合
    """
    course_data = get_course_data()
    guidelines = st.session_state.get("guidelines")
    return generate_response(user_input, course_data, guidelines)


def handle_form_submission(user_input: str):
    """
    フォーム送信を処理する
    
    Args:
        user_input: ユーザーの入力テキスト
    """
    # ユーザーメッセージを履歴に追加
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # AI応答を生成
    with st.spinner(TEXTS["loading_message"]):
        try:
            response = process_user_message(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            error_message = TEXTS["error_message"].format(error=str(e))
            st.session_state.messages.append({"role": "assistant", "content": error_message})
    
    # ページを再読み込みしてメッセージを表示
    st.rerun()


# ============================================================================
# メイン処理
# ============================================================================

def main():
    """
    アプリケーションのメイン処理
    """
    # 環境変数の読み込み
    load_dotenv()
    
    # ページ設定
    assistant_icon_for_page = get_custom_icon("assistant")
    page_icon_path = assistant_icon_for_page if assistant_icon_for_page else "💬"
    
    st.set_page_config(
        page_title=TEXTS["page_title"],
        page_icon=page_icon_path,
        layout="wide"
    )
    
    # セッション状態の初期化
    initialize_session_state()
    
    # APIキーの確認
    api_key = get_gemini_api_key()
    if not api_key:
        st.error("⚠️ エラー: GEMINI_API_KEY環境変数が設定されていません。")
        st.stop()
    
    # CSSスタイルの適用
    st.markdown(generate_css(), unsafe_allow_html=True)
    
    # サイドバーの表示
    with st.sidebar:
        render_sidebar()
    
    # メインコンテンツの表示
    render_header()
    render_chat_history()
    
    # 入力フォームの表示と処理
    user_input, submit_button = render_input_form()
    
    if submit_button and user_input:
        handle_form_submission(user_input)


if __name__ == "__main__":
    main()
