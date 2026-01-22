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
st.set_page_config(
    page_title="ファミリーシップ案内人 - ねんねママのファミリーシップ",
    page_icon="💬",
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
# タイトルにassistant_iconを使用
assistant_icon_path = get_custom_icon("assistant")
if assistant_icon_path:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.5rem;">
            <img src="data:image/png;base64,{_get_image_base64(assistant_icon_path)}" 
                 style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover;" />
            <h1 style="margin: 0; font-size: 2.25rem;">ファミリーシップ案内人</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.title("💬 ファミリーシップ案内人")
st.markdown("**ねんねママのファミリーシップ** - サロン全体のご案内役です。講座案内もアプリ操作もお気軽に。")

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
    background: linear-gradient(135deg, var(--pink) 0%, var(--mint) 100%);
    overflow: hidden;
}}

.main {{
    background: radial-gradient(circle at 20% 20%, rgba(249,232,239,0.9), transparent 35%),
                radial-gradient(circle at 80% 0%, rgba(231,244,243,0.9), transparent 30%),
                linear-gradient(135deg, var(--pink) 0%, var(--mint) 100%);
    height: 100vh;
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
    padding: 1.5rem 2rem;
    box-shadow: 0 12px 38px rgba(0,0,0,0.08);
    max-width: 1200px;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
    display: flex;
    flex-direction: column;
    min-height: calc(100vh - 4rem);
}}
/* チャット履歴エリア（スクロール可能） */
div[data-testid="stVerticalBlock"]:has(.stChatMessage) {{
    max-height: calc(100vh - 380px);
    overflow-y: auto;
    padding-bottom: 1rem;
    margin-bottom: 0.5rem;
}}
/* 入力フォームを下に固定 */
form[data-testid="stForm"] {{
    position: sticky;
    bottom: 0;
    background: rgba(255,255,255,0.98);
    padding: 1rem;
    border-radius: 12px;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.08);
    margin-top: auto;
    margin-bottom: 0;
    z-index: 100;
}}
/* フッターの余白を最小化 */
div:has(> div:contains("©")) {{
    margin-top: 0 !important;
    padding-top: 0 !important;
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
/* カスタムアイコンのスタイル */
.stChatMessage img {{
    border-radius: 50%;
    object-fit: cover;
}}
.stButton>button {{
    background: linear-gradient(120deg, #f8d9e4, #d9f0ee);
    color: var(--navy);
    font-weight: 700;
    border: 1px solid rgba(13, 30, 37, 0.05);
    border-radius: 12px;
    padding: 0.65rem 1.05rem;
    box-shadow: 0 6px 16px rgba(0,0,0,0.08);
}}
.stButton>button:hover {{
    background: linear-gradient(120deg, #d9f0ee, #f8d9e4);
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
}}
.stTextInput>div>div>input {{
    background: var(--white);
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
        height=100,
        help="Shift+Enterで改行、送信ボタンで送信します",
        placeholder="例: 3ヶ月の夜泣きに効く講座を教えて / FANTSアプリでライブの視聴URLはどこ？"
    )
    submit_button = st.form_submit_button("送信", use_container_width=True)

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


# フッター（最小限の表示、スペースを圧迫しない）
st.markdown(
    "<div style='text-align: center; color: rgba(128,128,128,0.6); padding: 0.5rem 0; font-size: 0.75rem; margin-top: 0.5rem;'>"
    "© ねんねママのファミリーシップ"
    "</div>",
    unsafe_allow_html=True
)