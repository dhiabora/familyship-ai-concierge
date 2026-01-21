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
    画像がない場合は何もしない。
    """
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "concierge_logo.png")
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
    3. AIコンシェルジュが講座やナレッジをもとに提案します
    """)
    st.caption("Shift+Enterで改行できます")

    st.markdown("### 📚 コンシェルジュのナレッジ")
    st.caption("デフォルトは data/guidelines.md を使用。ここで差し替えもできます。")
    uploaded_file = st.file_uploader("ガイドラインを差し替え (md/txt)", type=["md", "txt"])
    manual_guideline = st.text_area("追記したいナレッジ (任意)", height=80)

    if st.button("ナレッジを適用", use_container_width=True):
        uploaded_text = None
        if uploaded_file:
            uploaded_text = uploaded_file.read().decode("utf-8")
        combined_text_parts = [part for part in [uploaded_text, manual_guideline] if part and part.strip()]
        combined_text = "\n\n".join(combined_text_parts) if combined_text_parts else None
        st.session_state.guidelines = resolve_guidelines(combined_text)
        st.success("ナレッジを更新しました")

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
    st.markdown("### 🖼️ ロゴ画像")
    st.caption("`assets/concierge_logo.png` を配置するとヘッダーに表示されます。")


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

# カスタムCSSで全体のスタイルを微調整（ランディングページカラーに合わせる）
st.markdown(
    f"""
<style>
:root {{
    --pink: {PINK};
    --mint: {MINT};
    --navy: {NAVY};
    --white: {WHITE};
    --light-gray: {LIGHT_GRAY};
}}

.main {{
    background: linear-gradient(135deg, var(--pink) 0%, var(--mint) 100%);
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
    background: rgba(255,255,255,0.92);
    border-radius: 14px;
    padding: 2rem 2.5rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.06);
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
    border-radius: 14px;
    padding: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04);
}}
.stChatMessage[data-testid="stChatMessage-user"] {{
    background: linear-gradient(135deg, rgba(246,201,213,0.35), rgba(199,231,229,0.35));
    border-color: rgba(246,201,213,0.6);
}}
.stChatMessage[data-testid="stChatMessage-assistant"] {{
    border-color: rgba(199,231,229,0.8);
}}
.stButton>button {{
    background: linear-gradient(120deg, var(--pink), var(--mint));
    color: var(--navy);
    font-weight: 700;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}}
.stButton>button:hover {{
    background: linear-gradient(120deg, var(--mint), var(--pink));
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