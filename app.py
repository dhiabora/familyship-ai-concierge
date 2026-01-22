"""
Streamlit AIコンシェルジュアプリ
"""
import streamlit as st
import os
import base64
from dotenv import load_dotenv
from services.llm import generate_response, initialize_gemini
from services.sheets import load_course_data
from services.knowledge import resolve_guidelines
from config import get_gemini_api_key

# カラーパレット（ランディングページに合わせたピンク＆ミント）
PINK = "#f6c9d5"
MINT = "#c7e7e5"
NAVY = "#2d2a32"
WHITE = "#ffffff"
LIGHT_GRAY = "#f7f7f7"


def render_logo():
    """
    アプリのロゴを表示（assets/concierge_logo.png に配置された場合のみ）。
    ファイル名にコロンが含まれる場合も補足。
    """
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    candidates = [
        os.path.join(assets_dir, "concierge_logo.png"),
        os.path.join(assets_dir, "assets:concierge_logo.png"),
    ]
    for logo_path in candidates:
        if os.path.exists(logo_path):
            st.image(logo_path, width=100)
            st.session_state.logo_loaded = True
            return True
    st.session_state.logo_loaded = False
    return False


def get_custom_icon(role: str):
    """
    カスタムアイコンを取得（assets/user_icon.png または assets/assistant_icon.png）
    """
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    icon_path = os.path.join(assets_dir, f"{role}_icon.png")
    if os.path.exists(icon_path):
        return icon_path
    return None


def _get_image_base64(image_path: str) -> str:
    """
    画像ファイルをbase64エンコードして返す
    """
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

# .envファイルから環境変数を読み込む
load_dotenv()

# 講座データをキャッシュで読み込む
@st.cache_data
def get_course_data():
    """講座データを取得（キャッシュ機能付き）"""
    return load_course_data()


@st.cache_data
def get_default_guidelines():
    """デフォルトのガイドラインを取得"""
    return resolve_guidelines()


# ページ設定
# page_iconは絵文字または画像ファイルのパス（相対パスまたはURL）
assistant_icon_for_page = get_custom_icon("assistant")
page_icon_path = assistant_icon_for_page if assistant_icon_for_page else "💬"

st.set_page_config(
    page_title="ファミリーシップ案内人 - ねんねママのファミリーシップ",
    page_icon=page_icon_path,
    layout="wide"
)

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []
if "guidelines" not in st.session_state:
    st.session_state.guidelines = get_default_guidelines()
if "logo_loaded" not in st.session_state:
    st.session_state.logo_loaded = False

# APIキーの確認（環境変数のみ）
api_key = get_gemini_api_key()
if not api_key:
    st.error("⚠️ エラー: GEMINI_API_KEY環境変数が設定されていません。")
    st.stop()

# サイドバー
with st.sidebar:
    st.markdown("### 💡 使い方")
    st.markdown("""
    - ファミリーシップのコンテンツ・講座・イベントの案内役です。
    - FANTSアプリの操作や、どの講座を見ればよいかも案内します。
    """)
    st.caption("Shift+Enterで改行できます")

    st.markdown("### ✍️ 質問の例")
    st.markdown("""
    - 「○ヶ月の夜泣きに効く講座を教えて」
    - 「FANTSアプリでライブの視聴URLはどこ？」
    - 「離乳食の悩みでどのクラスに相談したらいい？」
    """)


# メインコンテンツ（ヘッダー）
st.title("💬 ファミリーシップ案内人")
st.markdown("<div style='margin-top: 0.75rem;'>**ねんねママのファミリーシップ** - サロン全体のご案内役です。講座案内もアプリ操作もお気軽に。</div>", unsafe_allow_html=True)

# ロゴをタイトルの下に表示
render_logo()

# チャット履歴の表示エリア（スクロール可能）
# メッセージがある場合のみ表示
if st.session_state.messages:
    for message in st.session_state.messages:
        # カスタムアイコンの取得
        icon_path = get_custom_icon(message["role"])
        if icon_path:
            with st.chat_message(message["role"], avatar=icon_path):
                st.markdown(message["content"])
        else:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# カスタムCSSで全体のスタイルを微調整（柔らかいピンク×ミントベース + チャットUI）
st.markdown(
    f"""
<style>
:root {{
    --pink: #f9e8ef;
    --mint: #e7f4f3;
    --navy: {NAVY};
    --white: {WHITE};
    --light-gray: #fdfbfc;
}}

html, body, .stApp {{
    height: 100vh;
    width: 100%;
    max-width: 100vw;
    background: linear-gradient(135deg, var(--pink) 0%, var(--mint) 100%);
    overflow-x: hidden !important;
    overflow-y: auto;
}}

.main {{
    background: radial-gradient(circle at 20% 20%, rgba(249,232,239,0.9), transparent 35%),
                radial-gradient(circle at 80% 0%, rgba(231,244,243,0.9), transparent 30%),
                linear-gradient(135deg, var(--pink) 0%, var(--mint) 100%);
    height: 100vh;
    width: 100%;
    max-width: 100vw;
    overflow-x: hidden !important;
    overflow-y: auto;
}}
section.main > div {{
    background: transparent;
}}
.stApp {{
    color: var(--navy);
}}
.stSidebar {{
    background: rgba(255,255,255,0.92);
}}
.block-container {{
    background: rgba(255,255,255,0.96);
    border-radius: 18px;
    padding: 1rem 1.5rem;
    box-shadow: 0 12px 38px rgba(0,0,0,0.08);
    max-width: 1200px;
    width: 100%;
    margin-top: 1.5rem;
    margin-bottom: 0;
    display: flex;
    flex-direction: column;
    height: calc(100vh - 2rem);
    max-height: calc(100vh - 2rem);
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
section[data-testid="stMain"] > div:first-child,
section[data-testid="stMain"] > div:first-child > div:first-child {{
    padding-top: 1.5rem !important;
    margin-top: 0.5rem !important;
}}
/* タイトルを含む最初のブロックに余白を追加 */
div[data-testid="stVerticalBlock"]:first-of-type {{
    padding-top: 1rem !important;
    margin-top: 0.5rem !important;
}}
/* チャット履歴エリア（スクロール可能、最大限のスペースを確保） */
div[data-testid="stVerticalBlock"]:has(.stChatMessage) {{
    flex: 1;
    overflow-y: auto;
    padding-bottom: 0.5rem;
    margin-bottom: 0;
    min-height: 0;
}}
/* 入力フォームを下に固定（余白を最小化、背景を完全に不透明に） */
form[data-testid="stForm"] {{
    position: sticky;
    bottom: 0;
    background: #ffffff !important;
    padding: 0.75rem;
    border-radius: 12px;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.08);
    margin-top: 0.5rem;
    margin-bottom: 0;
    z-index: 1000 !important;
    flex-shrink: 0;
    border: 1px solid rgba(255,255,255,1);
}}
/* 入力フォーム内のコンテナも不透明に */
form[data-testid="stForm"] > div {{
    background: #ffffff !important;
}}
/* テキストエリアの背景も確実に白に */
form[data-testid="stForm"] .stTextArea > div > div > textarea {{
    background: #ffffff !important;
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
    color: #0f7b8e;
    text-decoration: none;
    font-weight: 600;
}}
.stMarkdown a:hover {{
    text-decoration: underline;
}}
.stChatMessage {{
    border: 1px solid rgba(45,42,50,0.08);
    background: var(--white);
    border-radius: 16px;
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
/* チャットメッセージのアイコンとテキストの位置を統一 - transformを使った微調整 */
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
    background: #f6c9d5 !important;
    color: #2d2a32 !important;
    font-weight: 700;
    border: 1px solid rgba(246, 201, 213, 0.3);
    border-radius: 12px;
    padding: 0.65rem 1.05rem;
    box-shadow: 0 6px 16px rgba(0,0,0,0.08);
}}
.stButton>button:hover {{
    background: #f8aacb !important;
    color: #2d2a32 !important;
}}
.stTextArea > div > div > textarea, textarea {{
    color: #1f1f1f !important;
    background: var(--white);
    border-radius: 12px;
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
@media screen and (max-width: 768px) {{
    html, body, .stApp, .main {{
        width: 100% !important;
        max-width: 100vw !important;
        overflow-x: hidden !important;
    }}
    .block-container {{
        padding: 0.75rem 1rem;
        margin-top: 0.5rem;
        margin-bottom: 0 !important;
        border-radius: 12px;
        padding-bottom: 0 !important;
        width: 100% !important;
        max-width: 100vw !important;
        overflow-x: hidden !important;
        box-sizing: border-box !important;
    }}
    /* 入力フォームをモバイルで確実に前面に、画面最下部に固定 */
    form[data-testid="stForm"] {{
        background: #ffffff !important;
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
    /* モバイルで入力フォームの背景を完全に不透明に */
    form[data-testid="stForm"] > div,
    form[data-testid="stForm"] .stTextArea,
    form[data-testid="stForm"] .stTextArea > div,
    form[data-testid="stForm"] .stTextArea > div > div,
    form[data-testid="stForm"] .stTextArea > div > div > textarea {{
        background: #ffffff !important;
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
        padding-bottom: 180px !important;
        margin-bottom: 0 !important;
    }}
    /* メインコンテンツの下部余白を追加 */
    .block-container {{
        padding-bottom: 180px !important;
        margin-bottom: 0 !important;
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
/* ロゴのスタイル調整（見切れ防止） */
div[data-testid="stVerticalBlock"]:has(img[src*="concierge_logo"]),
div:has(img[src*="concierge_logo"]) {{
    margin-top: 1rem;
    margin-bottom: 1rem;
    text-align: center;
}}
div:has(img[src*="concierge_logo"]) img {{
    max-width: 100px;
    height: auto;
    object-fit: contain;
}}
</style>
""",
    unsafe_allow_html=True,
)

# 入力フォーム（下に固定、Enterキーで自動送信されない）
with st.form(key="user_input_form", clear_on_submit=True):
    user_input = st.text_area(
        "質問や相談を入力してください...",
        key="user_input",
        height=80,
        help="Shift+Enterで改行、送信ボタンで送信します",
        placeholder="例: 3ヶ月の夜泣きに効く講座を教えて / FANTSアプリでライブの視聴URLはどこ？"
    )
    submit_button = st.form_submit_button("シップちゃんに案内してもらう", use_container_width=True)
    # フッターを入力フォーム内に配置
    st.markdown(
        "<div style='text-align: center; color: rgba(128,128,128,0.5); padding: 0.25rem 0; font-size: 0.7rem; margin: 0;'>"
        "© ねんねママのファミリーシップ"
        "</div>",
        unsafe_allow_html=True
    )

if submit_button and user_input:
    # ユーザーメッセージを履歴に追加
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # AI応答を生成
    with st.spinner("考えています..."):
        try:
            course_data = get_course_data()
            guidelines = st.session_state.get("guidelines")
            response = generate_response(user_input, course_data, guidelines)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            error_message = f"エラーが発生しました: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_message})
    
    # ページを再読み込みしてメッセージを表示
    st.rerun()

