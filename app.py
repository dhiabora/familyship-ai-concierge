"""
Streamlit AIコンシェルジュアプリ
"""
import streamlit as st
import os
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
            st.image(logo_path, width=140)
            st.session_state.logo_loaded = True
            return True
    st.session_state.logo_loaded = False
    return False

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
    page_title="AIコンシェルジュ - ねんねママのファミリーシップ",
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
    1. 育児の悩みや質問を入力
    2. 送信ボタンをクリック
    3. AIコンシェルジュが講座データとガイドラインをもとに提案します
    """)
    st.caption("Shift+Enterで改行できます")

    st.markdown("### 🔗 データソース")
    with st.expander("講座データ読み込み状況", expanded=False):
        from config import get_google_sheets_id, get_google_sheets_credentials
        sheets_id = get_google_sheets_id()
        creds = get_google_sheets_credentials()
        
        if sheets_id and creds:
            st.write("✅ **Google Sheets** に接続中")
            st.caption(f"シートID: {sheets_id[:20]}...")
        elif sheets_id:
            st.write("⚠️ **Google Sheets ID** は設定済み")
            st.caption("認証情報が設定されていません")
        else:
            st.write("📄 **ローカルCSV** (data/courses.csv)")
            st.caption("Google Sheets未設定のため、ローカルファイルを使用")


# メインコンテンツ（ヘッダー）
header_left, header_right = st.columns([1, 4])
with header_left:
    render_logo()
with header_right:
    st.title("💬 AIコンシェルジュ")
    st.markdown("**ねんねママのファミリーシップ** - 育児の悩みに最適な講座を提案します")

# チャット履歴の表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# カスタムCSSで全体のスタイルを微調整（柔らかいピンク×ミントベース）
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

.main {{
    background: radial-gradient(circle at 20% 20%, rgba(249,232,239,0.9), transparent 35%),
                radial-gradient(circle at 80% 0%, rgba(231,244,243,0.9), transparent 30%),
                linear-gradient(135deg, var(--pink) 0%, var(--mint) 100%);
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
    padding: 2.25rem 2.75rem;
    box-shadow: 0 12px 38px rgba(0,0,0,0.08);
    max-width: 1100px;
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
}}
.stChatMessage[data-testid="stChatMessage-user"] {{
    background: linear-gradient(135deg, rgba(249,232,239,0.55), rgba(231,244,243,0.45));
    border-color: rgba(249,232,239,0.8);
}}
.stChatMessage[data-testid="stChatMessage-assistant"] {{
    border-color: rgba(231,244,243,0.9);
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
}}
.stTextArea label, label {{
    color: var(--navy);
    font-weight: 600;
}}
.stTextInput>div>div>input {{
    background: var(--white);
}}
</style>
""",
    unsafe_allow_html=True,
)

# 入力フォーム（Enterキーで自動送信されない）
with st.form(key="user_input_form", clear_on_submit=True):
    user_input = st.text_area(
        "育児の悩みや質問を入力してください...",
        key="user_input",
        height=100,
        help="Shift+Enterで改行、送信ボタンで送信します"
    )
    submit_button = st.form_submit_button("送信", use_container_width=True)

if submit_button and user_input:
    # ユーザーメッセージを履歴に追加
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # ユーザーメッセージを表示
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # AI応答を生成
    with st.chat_message("assistant"):
        with st.spinner("考えています..."):
            try:
                course_data = get_course_data()
                guidelines = st.session_state.get("guidelines")
                response = generate_response(user_input, course_data, guidelines)
                st.markdown(response)

                # AIメッセージを履歴に追加
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_message = f"エラーが発生しました: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})


# フッター
st.divider()
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "© ねんねママのファミリーシップ - AIコンシェルジュ"
    "</div>",
    unsafe_allow_html=True
)
# テスト