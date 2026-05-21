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
    "cream": "#fff8dc",
    "sun": "#ffe89f",
    "sun_deep": "#f5c954",
    "aqua": "#d9f1f2",
    "aqua_deep": "#9fd5d9",
    "coral": "#f3a89b",
    "navy": "#2d2a32",
    "white": "#ffffff",
    "soft_gray": "#f8f4e8",
    "text_muted": "#6f6757",
    "button": "#ffd966",
    "button_hover": "#f5c954",
    "link": "#087986",
}

# デザイン設定
DESIGN = {
    "logo_width": 88,
    "container_max_width": 860,
    "border_radius": 14,
    "button_border_radius": 12,
    "chat_border_radius": 14,
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
    "subtitle": "講座案内も、アプリ操作も、今の困りごとも。ファミリーシップの中をやさしく案内します。",
    "input_label": "質問や相談を入力してください...",
    "input_placeholder": "例: 3ヶ月の夜泣きに効く講座を教えて",
    "submit_button": "案内してもらう",
    "footer": "© ねんねママのファミリーシップ",
    "loading_message": "考えています...",
    "error_message": "エラーが発生しました: {error}",
    "welcome_title": "今日はどんなことを探しますか？",
    "welcome_body": "月齢やお悩みをそのまま書いてください。関連する講座や、FANTS内で見る場所を案内します。",
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
    "mobile_padding": "0.75rem 0.8rem",
    "mobile_font_size": "0.95rem",
    "mobile_line_height": "1.6",
    "form_bottom_padding": 184,
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
    usage_items = "".join(f"<li>{item}</li>" for item in SIDEBAR["usage_items"])
    examples = "".join(f"<li>{example}</li>" for example in SIDEBAR["examples"])
    st.markdown(
        f"""
        <div class="sidebar-card">
            <div class="sidebar-kicker">はじめての方へ</div>
            <h3>{SIDEBAR['usage_title']}</h3>
            <ul>{usage_items}</ul>
            <p class="sidebar-note">{SIDEBAR["help_text"]}</p>
        </div>
        <div class="sidebar-card sidebar-card-accent">
            <div class="sidebar-kicker">迷ったら</div>
            <h3>{SIDEBAR['examples_title']}</h3>
            <ul>{examples}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    """
    ヘッダー（タイトルと説明）を表示する
    """
    logo_html = ""
    assets_dir = get_assets_dir()
    for logo_filename in ICONS["logo_candidates"]:
        logo_path = os.path.join(assets_dir, logo_filename)
        if os.path.exists(logo_path):
            logo_base64 = _get_image_base64(logo_path)
            if logo_base64:
                logo_html = (
                    f"<img src='data:image/png;base64,{logo_base64}' "
                    f"alt='ファミリーシップ案内人' />"
                )
                st.session_state.logo_loaded = True
                break
    if not logo_html:
        st.session_state.logo_loaded = False

    st.markdown(
        f"""
        <section class="app-hero">
            <div class="hero-logo">{logo_html}</div>
            <div class="hero-copy">
                <div class="hero-kicker">ねんねママのファミリーシップ</div>
                <div class="hero-title">{TEXTS['main_title']}</div>
                <div class="hero-subtitle">{TEXTS['subtitle']}</div>
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )


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
    else:
        st.markdown(
            f"""
            <section class="welcome-panel">
                <div class="welcome-kicker">AI concierge</div>
                <h2>{TEXTS['welcome_title']}</h2>
                <p>{TEXTS['welcome_body']}</p>
                <div class="prompt-chips">
                    <span>夜泣きに効く講座</span>
                    <span>ライブ視聴URL</span>
                    <span>離乳食の相談先</span>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )


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
            f"<div class='form-footer'>"
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
    --cream: {COLORS['cream']};
    --sun: {COLORS['sun']};
    --sun-deep: {COLORS['sun_deep']};
    --aqua: {COLORS['aqua']};
    --aqua-deep: {COLORS['aqua_deep']};
    --coral: {COLORS['coral']};
    --navy: {COLORS['navy']};
    --white: {COLORS['white']};
    --soft-gray: {COLORS['soft_gray']};
    --text-muted: {COLORS['text_muted']};
    --shadow: 0 18px 48px rgba(92, 72, 34, 0.12);
    --soft-shadow: 0 10px 26px rgba(92, 72, 34, 0.10);
}}

html, body, .stApp, .main {{
    width: 100%;
    max-width: 100vw;
    background:
        radial-gradient(circle at 18px 18px, rgba(245, 201, 84, 0.16) 0 2px, transparent 2.5px),
        radial-gradient(circle at calc(100% - 34px) 118px, rgba(243, 168, 155, 0.12) 0 48px, transparent 49px),
        linear-gradient(180deg, #fffdf3 0%, var(--cream) 48%, #fff4c6 100%) !important;
    background-size: 28px 28px, auto, auto !important;
    overflow-x: hidden !important;
    min-height: 100vh;
}}

.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background:
        linear-gradient(135deg, transparent 0 44%, rgba(255, 232, 159, 0.28) 44% 47%, transparent 47% 100%),
        radial-gradient(circle at 86% 18%, rgba(255, 255, 255, 0.65) 0 0.45rem, transparent 0.5rem),
        radial-gradient(circle at 12% 82%, rgba(255, 255, 255, 0.52) 0 0.38rem, transparent 0.43rem);
    opacity: 0.9;
}}

[data-testid="stAppViewContainer"],
.stApp > div {{
    background: transparent !important;
}}

.stApp {{
    color: var(--navy);
    font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", "YuGothic", "Noto Sans JP", sans-serif;
}}

.stSidebar {{
    background: rgba(255, 253, 241, 0.96) !important;
    border-right: 1px solid rgba(245, 201, 84, 0.35);
}}

.stSidebar [data-testid="stVerticalBlock"] {{
    gap: 0.9rem;
}}

.block-container {{
    background: rgba(255, 253, 244, 0.82);
    border: 1px solid rgba(245, 201, 84, 0.24);
    border-radius: {DESIGN['border_radius']}px;
    box-shadow: var(--shadow);
    max-width: {DESIGN['container_max_width']}px;
    width: 100%;
    margin-top: 1.25rem;
    margin-bottom: 1.25rem;
    padding: 1.35rem 1.35rem 0;
    min-height: calc(100vh - 2.5rem);
    overflow-x: hidden !important;
    box-sizing: border-box;
}}

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

section[data-testid="stMain"] > div:first-child {{
    padding-top: 0.35rem !important;
}}

[data-testid="stHeader"] {{
    background: transparent !important;
    height: 0 !important;
}}

#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stMainMenuButton"],
[data-testid="stDeployButton"],
[data-testid="stExpandSidebarButton"],
[data-testid="stBaseButton-header"],
[data-testid="stBaseButton-headerNoPadding"] {{
    display: none !important;
}}

.app-hero {{
    display: flex;
    align-items: center;
    gap: 0.82rem;
    padding: 0.72rem 0.2rem 0.82rem;
}}

.hero-logo {{
    width: 74px;
    height: 74px;
    display: grid;
    place-items: center;
    flex: 0 0 auto;
    border-radius: 14px;
    background: linear-gradient(145deg, var(--white), #fff0ab);
    border: 1px solid rgba(245, 201, 84, 0.42);
    box-shadow: var(--soft-shadow);
}}

.hero-logo img {{
    width: 58px;
    height: 58px;
    object-fit: contain;
}}

.hero-copy {{
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 0.14rem;
}}

.hero-kicker,
.welcome-kicker,
.sidebar-kicker {{
    color: #7c6a32;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0;
    margin: 0 0 0.12rem;
    text-transform: uppercase;
}}

.hero-title {{
    color: var(--navy);
    font-size: clamp(1.7rem, 4vw, 2.45rem);
    line-height: 1.18;
    margin: 0;
    letter-spacing: 0;
    font-weight: 800;
}}

.hero-subtitle {{
    color: var(--text-muted);
    font-size: 0.98rem;
    line-height: 1.62;
    margin: 0.12rem 0 0;
}}

.welcome-panel {{
    position: relative;
    margin: 0.15rem 0 1rem;
    padding: 1.2rem 1.1rem 1.08rem;
    border-radius: 14px;
    background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(255, 250, 225, 0.88)),
        repeating-linear-gradient(135deg, rgba(245, 201, 84, 0.08) 0 8px, transparent 8px 16px);
    border: 1px solid rgba(208, 161, 37, 0.26);
    box-shadow: 0 14px 34px rgba(118, 88, 20, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.9);
    overflow: hidden;
}}

.welcome-panel::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 7px;
    background: linear-gradient(90deg, var(--sun-deep), #ffdba6, var(--sun));
}}

.welcome-panel::after {{
    content: "";
    position: absolute;
    right: 1rem;
    top: 1rem;
    width: 46px;
    height: 46px;
    border-radius: 50%;
    background:
        radial-gradient(circle at 50% 50%, rgba(245, 201, 84, 0.28) 0 2px, transparent 2.5px);
    background-size: 10px 10px;
    opacity: 0.9;
}}

.welcome-panel h2 {{
    color: var(--navy);
    font-size: 1.2rem;
    line-height: 1.35;
    margin: 0;
    letter-spacing: 0;
}}

.welcome-panel p {{
    color: var(--text-muted);
    font-size: 0.94rem;
    line-height: 1.75;
    margin: 0.55rem 0 0;
}}

.prompt-chips {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    margin-top: 0.85rem;
}}

.prompt-chips span {{
    display: inline-flex;
    align-items: center;
    min-height: 32px;
    padding: 0.36rem 0.68rem;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid rgba(218, 174, 57, 0.24);
    color: #72591a;
    font-size: 0.84rem;
    font-weight: 700;
}}

.stMarkdown a {{
    color: {COLORS['link']};
    text-decoration: none;
    font-weight: 700;
}}

.stMarkdown a:hover {{
    text-decoration: underline;
}}

.stChatMessage {{
    border: 1px solid rgba(245, 201, 84, 0.24);
    background: rgba(255, 255, 255, 0.82);
    border-radius: {DESIGN['chat_border_radius']}px;
    padding: 0.9rem 1rem;
    box-shadow: 0 8px 24px rgba(92, 72, 34, 0.08);
    overflow: visible;
    margin: 0.72rem 0;
}}

.stChatMessage[data-testid="stChatMessage-user"] {{
    background: linear-gradient(145deg, rgba(255, 245, 195, 0.86), rgba(255, 255, 255, 0.9));
    border-color: rgba(245, 201, 84, 0.38);
}}

.stChatMessage[data-testid="stChatMessage-assistant"] {{
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.92), rgba(255, 248, 220, 0.9));
    border-color: rgba(245, 201, 84, 0.32);
}}

.stChatMessage > div {{
    display: flex !important;
    align-items: flex-start !important;
    gap: 0.75rem !important;
    width: 100% !important;
    overflow-x: hidden !important;
}}

.stChatMessage img,
.stChatMessage > div > div:first-child,
.stChatMessage > div > div:first-child img {{
    margin: 0 !important;
    padding: 0 !important;
    flex-shrink: 0 !important;
}}

.stChatMessage > div > div:last-child,
.stChatMessage .stMarkdown {{
    margin-top: 0 !important;
    padding-top: 0 !important;
    width: 100% !important;
    overflow-x: hidden !important;
    word-wrap: break-word !important;
    word-break: break-word !important;
}}

.stChatMessage .stMarkdown > p:first-child,
.stChatMessage .stMarkdown > *:first-child {{
    margin-top: 0 !important;
    padding-top: 0 !important;
}}

.stChatMessage .stMarkdown p {{
    color: #40382e;
    line-height: 1.75;
    margin-bottom: 0.45rem;
}}

[data-testid="stForm"] {{
    position: sticky;
    bottom: 0.85rem;
    top: auto !important;
    height: auto !important;
    min-height: 0 !important;
    z-index: 50 !important;
    margin: 1rem -0.35rem 0.2rem;
    padding: 0.8rem;
    border-radius: 14px;
    background: rgba(255, 253, 241, 0.95) !important;
    border: 1px solid rgba(245, 201, 84, 0.34);
    box-shadow: 0 -10px 36px rgba(92, 72, 34, 0.12);
    backdrop-filter: blur(14px);
}}

[data-testid="stForm"] > div {{
    background: transparent !important;
}}

[data-testid="stForm"] .stTextArea {{
    margin-bottom: 0.58rem;
}}

.stButton>button,
[data-testid="stBaseButton-secondaryFormSubmit"] {{
    min-height: 46px;
    background: linear-gradient(180deg, {COLORS['button']}, {COLORS['button_hover']}) !important;
    color: {COLORS['navy']} !important;
    font-weight: 700;
    border: 1px solid rgba(159, 124, 24, 0.18);
    border-radius: {DESIGN['button_border_radius']}px;
    padding: 0.72rem 1.05rem;
    box-shadow: 0 8px 18px rgba(143, 106, 11, 0.16);
    transition: transform 160ms ease, box-shadow 160ms ease;
}}

.stButton>button:hover,
[data-testid="stBaseButton-secondaryFormSubmit"]:hover {{
    background: {COLORS['button_hover']} !important;
    color: {COLORS['navy']} !important;
    border-color: rgba(159, 124, 24, 0.28);
    box-shadow: 0 10px 22px rgba(143, 106, 11, 0.20);
    transform: translateY(-1px);
}}

.stButton>button:active,
[data-testid="stBaseButton-secondaryFormSubmit"]:active {{
    transform: translateY(0);
}}

.stTextArea > div > div > textarea, textarea {{
    color: #1f1f1f !important;
    background: var(--white) !important;
    border-radius: {DESIGN['button_border_radius']}px;
    box-shadow: inset 0 1px 2px rgba(92, 72, 34, 0.06);
    border: 1px solid rgba(141, 119, 58, 0.24) !important;
    line-height: 1.55 !important;
    min-height: 76px !important;
}}

.stTextArea > div > div > textarea:focus {{
    border-color: var(--sun-deep) !important;
    box-shadow: 0 0 0 3px rgba(245, 201, 84, 0.18) !important;
}}

.stTextArea label, label {{
    color: var(--navy);
    font-weight: 700;
    margin-top: 0 !important;
    padding-top: 0 !important;
    margin-bottom: 0.25rem !important;
}}

.form-footer {{
    text-align: center;
    color: rgba(111, 103, 87, 0.58);
    padding: 0.24rem 0 0;
    font-size: 0.72rem;
    margin-top: 0 !important;
}}

.sidebar-card {{
    margin: 0.75rem 0;
    padding: 1rem;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.76);
    border: 1px solid rgba(245, 201, 84, 0.32);
    box-shadow: 0 8px 22px rgba(92, 72, 34, 0.08);
}}

.sidebar-card-accent {{
    background: linear-gradient(145deg, rgba(255, 232, 159, 0.46), rgba(255, 255, 255, 0.72));
}}

.sidebar-card h3 {{
    color: var(--navy);
    font-size: 1rem;
    line-height: 1.35;
    margin: 0 0 0.55rem;
    letter-spacing: 0;
}}

.sidebar-card ul {{
    margin: 0;
    padding-left: 1.05rem;
}}

.sidebar-card li {{
    color: #51483a;
    font-size: 0.9rem;
    line-height: 1.65;
    margin: 0.25rem 0;
}}

.sidebar-note {{
    color: var(--text-muted);
    font-size: 0.78rem;
    margin: 0.7rem 0 0;
}}

@media screen and (max-width: {RESPONSIVE['mobile_breakpoint']}px) {{
    html, body, .stApp, .main {{
        width: 100% !important;
        max-width: 100vw !important;
        min-height: 100vh;
    }}

    .block-container {{
        max-width: 100vw;
        width: 100% !important;
        margin: 0;
        padding: {RESPONSIVE['mobile_padding']};
        padding-bottom: {RESPONSIVE['form_bottom_padding']}px !important;
        border-width: 0;
        border-radius: 0;
        box-shadow: none;
        min-height: 100vh;
        background: rgba(255, 253, 244, 0.58);
    }}

    section[data-testid="stMain"] > div:first-child {{
        padding-top: 0 !important;
    }}

    .app-hero {{
        gap: 0.68rem;
        align-items: flex-start;
        padding: 0.5rem 0 0.64rem;
    }}

    .hero-logo {{
        width: 52px;
        height: 52px;
        border-radius: 12px;
    }}

    .hero-logo img {{
        width: 40px;
        height: 40px;
    }}

    .hero-title {{
        font-size: 1.62rem;
    }}

    .hero-subtitle {{
        font-size: 0.9rem;
        line-height: 1.55;
        margin-top: 0.08rem;
    }}

    .hero-kicker,
    .welcome-kicker,
    .sidebar-kicker {{
        font-size: 0.7rem;
    }}

    .welcome-panel {{
        padding: 1.08rem 0.92rem 0.94rem;
        border-radius: 14px;
        margin-top: 0.08rem;
    }}

    .welcome-panel h2 {{
        font-size: 1.08rem;
    }}

    .welcome-panel p,
    .stMarkdown,
    .stMarkdown p,
    .stChatMessage .stMarkdown,
    .stChatMessage .stMarkdown p {{
        font-size: {RESPONSIVE['mobile_font_size']} !important;
        line-height: {RESPONSIVE['mobile_line_height']} !important;
        overflow-wrap: anywhere !important;
    }}

    .prompt-chips {{
        gap: 0.38rem;
    }}

    .prompt-chips span {{
        min-height: 30px;
        padding: 0.32rem 0.56rem;
        font-size: 0.78rem;
    }}

    .stChatMessage {{
        width: 100% !important;
        padding: 0.78rem !important;
        border-radius: 14px;
        margin: 0.58rem 0;
    }}

    .stChatMessage > div {{
        gap: 0.58rem !important;
    }}

    [data-testid="stForm"] {{
        position: fixed !important;
        top: auto !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
        height: auto !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0.72rem 0.78rem calc(0.62rem + env(safe-area-inset-bottom)) !important;
        border-radius: 14px 14px 0 0 !important;
        border-left: 0;
        border-right: 0;
        border-bottom: 0;
        background: rgba(255, 253, 241, 0.98) !important;
        box-shadow: 0 -12px 34px rgba(92, 72, 34, 0.16) !important;
    }}

    .stTextArea > div > div > textarea, textarea {{
        min-height: 68px !important;
        font-size: 16px !important;
    }}

    .stButton>button,
    [data-testid="stBaseButton-secondaryFormSubmit"] {{
        min-height: 44px;
        padding: 0.62rem 0.9rem;
    }}

    .form-footer {{
        padding-top: 0.2rem;
        font-size: 0.66rem;
    }}

    [data-testid="stSidebar"][aria-expanded="true"] {{
        min-width: min(88vw, 360px) !important;
        max-width: min(88vw, 360px) !important;
    }}

    .stSidebar {{
        z-index: 999 !important;
    }}
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
    
    # ページ設定（page_iconは絵文字のみ使用＝モバイル/Cloudでパス指定が失敗するため）
    st.set_page_config(
        page_title=TEXTS["page_title"],
        page_icon="💬",
        layout="wide"
    )
    
    # セッション状態の初期化
    initialize_session_state()
    
    # APIキーの確認
    api_key = get_gemini_api_key()
    if not api_key:
        st.error("⚠️ エラー: GEMINI_API_KEY環境変数が設定されていません。")
        st.markdown("""
        **設定方法：**
        - **ローカル / Codespaces:** プロジェクト直下に `.env` を作成し、`GEMINI_API_KEY=あなたのキー` を1行で記述してください。
        - **Streamlit Cloud:** アプリの Settings → Secrets に `GEMINI_API_KEY = "あなたのキー"` を追加してください。
        - **GitHub Codespaces:** リポジトリの Settings → Secrets and variables → Codespaces で `GEMINI_API_KEY` を追加すると、自動で環境変数になります。
        """)
        st.stop()
    
    # CSSスタイルの適用
    st.markdown(generate_css(), unsafe_allow_html=True)
    
    # メインコンテンツの表示
    render_header()
    render_chat_history()
    
    # 入力フォームの表示と処理
    user_input, submit_button = render_input_form()
    
    if submit_button and user_input:
        handle_form_submission(user_input)


if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception as e:
        # 起動時エラー時にトレースバックを画面に表示（デバッグ用）
        st.error("⚠️ アプリの起動中にエラーが発生しました。")
        st.code(traceback.format_exc(), language="text")
        st.caption("上記のトレースバックは、ターミナルで `streamlit run app.py` を実行した場合も同じ内容が表示されます。")
        raise
