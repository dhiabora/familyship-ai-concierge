"""
Streamlit AIコンシェルジュアプリ
"""
import streamlit as st
import os
from dotenv import load_dotenv
from services.llm import generate_response, initialize_gemini
from services.sheets import load_course_data
from config import get_gemini_api_key

# .envファイルから環境変数を読み込む
load_dotenv()

# 講座データをキャッシュで読み込む
@st.cache_data
def get_course_data():
    """講座データを取得（キャッシュ機能付き）"""
    return load_course_data()


# ページ設定
st.set_page_config(
    page_title="AIコンシェルジュ - ねんねママのファミリーシップ",
    page_icon="💬",
    layout="wide"
)

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# APIキーの確認（環境変数のみ）
api_key = get_gemini_api_key()
if not api_key:
    st.error("⚠️ エラー: GEMINI_API_KEY環境変数が設定されていません。")
    st.stop()

# サイドバー
with st.sidebar:
    st.markdown("### 💡 使い方")
    st.markdown("""
    1. 育児の悩みや質問を入力してください
    2. 送信ボタンをクリックして送信
    3. AIコンシェルジュが講座を提案します
    
    ※ Shift+Enterで改行できます
    """)


# メインコンテンツ
st.title("💬 AIコンシェルジュ")
st.markdown("**ねんねママのファミリーシップ** - 育児の悩みに最適な講座を提案します")

# チャット履歴の表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# カスタムCSSで入力欄の文字色を黒に
st.markdown("""
<style>
.stTextArea > div > div > textarea {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

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
                # 講座データを取得
                course_data = get_course_data()
                # 講座データを渡して回答を生成
                response = generate_response(user_input, course_data)
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