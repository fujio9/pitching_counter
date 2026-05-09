"""
野球投手 投球数カウントアプリ
Python + Streamlit / スマホ向け片手操作
"""

import streamlit as st

# --- Page config ---
st.set_page_config(
    page_title="投球数カウント",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Session state 初期化 ---
if "current_pitcher" not in st.session_state:
    st.session_state.current_pitcher = ""
if "current_count" not in st.session_state:
    st.session_state.current_count = 0
if "history" not in st.session_state:
    st.session_state.history = []
if "prev_pitcher_input" not in st.session_state:
    st.session_state.prev_pitcher_input = None
if "pitcher_input_version" not in st.session_state:
    st.session_state.pitcher_input_version = 0

# --- 交代直後: 動的 key で text_input を作り直し、入力欄を確実に空にする ---
if st.session_state.get("_clear_pitcher_after_change"):
    st.session_state._clear_pitcher_after_change = False
    st.session_state.current_pitcher = ""
    st.session_state.prev_pitcher_input = None
    st.session_state.pitcher_input_version += 1

# --- カスタム CSS（LINEライト風）---
st.markdown(
    """
<style>
  section.main > div.block-container {
    padding-top: 0.55rem !important;
    padding-bottom: 0.75rem !important;
  }
  .stApp {
    background: #f5f6f8;
  }
  .line-header {
    background: #06c755;
    color: #ffffff;
    border-radius: 12px;
    padding: 10px 14px;
    margin-bottom: 6px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  .line-header-title {
    font-size: 1rem;
    font-weight: 700;
  }
  .line-header-sub {
    margin-top: 2px;
    font-size: 0.82rem;
    opacity: 0.95;
  }
  /* 投手入力欄を白系に固定 */
  div[data-baseweb="input"] > div {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 10px !important;
  }
  div[data-baseweb="input"] input {
    color: #111827 !important;
    background: transparent !important;
  }
  div[data-baseweb="input"] input::placeholder {
    color: #6b7280 !important;
  }
  div[data-baseweb="input"]:focus-within > div {
    border-color: #06c755 !important;
    box-shadow: 0 0 0 1px rgba(6, 199, 85, 0.22) !important;
  }
  .count-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 10px 12px 8px;
    margin: 6px 0 8px;
    box-shadow: 0 5px 12px rgba(0, 0, 0, 0.07);
    text-align: center;
  }
  .count-label {
    color: #6f7785;
    font-size: 0.95rem;
    margin-bottom: 4px;
  }
  .count-value {
    font-size: 3.1rem;
    font-weight: 800;
    color: #111827;
    line-height: 1.1;
  }
  .count-unit {
    font-size: 1.05rem;
    color: #111827;
    margin-left: 4px;
  }
  .section-label {
    color: #6b7280;
    font-size: 0.84rem;
    font-weight: 600;
    margin: 0 2px 3px;
  }
  .history-area {
    margin-top: 4px;
  }
  .history-row {
    display: flex;
    justify-content: flex-start;
    margin: 8px 0;
  }
  .history-bubble {
    background: #ffffff;
    border-radius: 14px;
    padding: 10px 12px;
    box-shadow: 0 4px 14px rgba(17, 24, 39, 0.08);
    max-width: 92%;
  }
  .history-meta {
    font-size: 0.78rem;
    color: #6b7280;
    margin-bottom: 3px;
  }
  .history-main {
    font-size: 0.95rem;
    color: #111827;
    font-weight: 600;
  }
  .history-count {
    font-size: 0.84rem;
    color: #374151;
    margin-top: 4px;
  }
  .empty-history {
    color: #8a94a6;
    font-size: 0.9rem;
    background: #ffffff;
    border-radius: 12px;
    padding: 10px 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  }

  /* 主操作ボタン（＋、−） */
  :has(.main-actions-row) + * div.stButton > button {
    background: #06c755 !important;
    color: #ffffff !important;
    border: none !important;
    min-height: 96px !important;
    border-radius: 12px !important;
    font-size: 3.1rem !important;
    font-weight: 900 !important;
    line-height: 1 !important;
    box-shadow: 0 6px 12px rgba(6, 199, 85, 0.24) !important;
    transition: transform 0.08s ease, box-shadow 0.08s ease !important;
  }
  :has(.main-actions-row) + * div.stButton > button:active {
    transform: scale(0.97);
    box-shadow: 0 3px 8px rgba(6, 199, 85, 0.2) !important;
  }

  /* 副操作ボタン（交代、リセット） */
  :has(.secondary-buttons) + * div.stButton > button,
  :has(.secondary-buttons) + * + * div.stButton > button {
    min-height: 46px !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    border: 1px solid #d1d5db !important;
    background: #ffffff !important;
    color: #1f2937 !important;
    box-shadow: none !important;
  }
  :has(.secondary-buttons) + * + * div.stButton > button {
    background: #f9fafb !important;
  }
</style>
""",
    unsafe_allow_html=True,
)

# --- ヘッダー ---
current_pitcher_view = st.session_state.current_pitcher or "未入力"
st.markdown(
    f"""
<div class="line-header">
  <div class="line-header-title">投球数カウンター</div>
  <div class="line-header-sub">現在の投手: {current_pitcher_view}</div>
</div>
""",
    unsafe_allow_html=True,
)

# --- 投手入力（背番号・名前・任意テキスト） ---
_pitcher_widget_key = f"pitcher_input_v{st.session_state.pitcher_input_version}"
st.session_state.current_pitcher = st.text_input(
    "現在の投手（背番号・名前・任意テキスト）",
    value=st.session_state.current_pitcher,
    key=_pitcher_widget_key,
    placeholder="例: 18 / 佐藤 / 先発A",
).strip()

# --- 同じ投手入力を再入力した場合、履歴の投球数から再開 ---
current = st.session_state.current_pitcher
prev = st.session_state.prev_pitcher_input
if current != prev:
    last_count = None
    for record in reversed(st.session_state.history):
        # 旧データ（numberキー）との互換を維持
        saved_pitcher = record.get("pitcher", record.get("number", ""))
        if str(saved_pitcher) == str(current):
            last_count = record["count"]
            break
    if last_count is not None:
        st.session_state.current_count = last_count
    st.session_state.prev_pitcher_input = current

# --- メインカード（カウント表示）---
count = st.session_state.current_count
st.markdown(
    f"""
<div class="count-card">
  <div class="count-label">現在の投球数</div>
  <div><span class="count-value">{count}</span><span class="count-unit">球</span></div>
</div>
""",
    unsafe_allow_html=True,
)

# --- 操作エリア ---
st.markdown('<div class="section-label">メイン操作</div>', unsafe_allow_html=True)
st.markdown('<div class="main-actions-row"></div>', unsafe_allow_html=True)
col_left, col_right = st.columns([1, 1], gap="small")
with col_left:
    if st.button("＋", key="btn_plus", use_container_width=True):
        st.session_state.current_count += 1
        st.rerun()
with col_right:
    if st.button("−", key="btn_minus", use_container_width=True):
        st.session_state.current_count = max(0, st.session_state.current_count - 1)
        st.rerun()

# --- 副操作 ---
st.markdown('<div class="section-label">投手管理</div>', unsafe_allow_html=True)
st.markdown('<div class="secondary-buttons"></div>', unsafe_allow_html=True)
if st.button("交代する", key="change_pitcher", use_container_width=True):
    st.session_state.history.append(
        {"pitcher": st.session_state.current_pitcher or "—", "count": st.session_state.current_count}
    )
    st.session_state.current_count = 0
    st.session_state._clear_pitcher_after_change = True
    st.rerun()

# --- 投球数・履歴をリセット ---
if st.button("投球数・履歴をリセット", key="reset_all", use_container_width=True):
    st.session_state.current_count = 0
    st.session_state.history = []
    st.session_state.prev_pitcher_input = None
    st.rerun()

# --- 履歴（吹き出し風）---
st.markdown('<div class="section-label">登板履歴</div>', unsafe_allow_html=True)
st.markdown('<div class="history-area">', unsafe_allow_html=True)
if st.session_state.history:
    for i, record in enumerate(st.session_state.history, start=1):
        pitcher = record.get("pitcher", record.get("number", "—"))
        c = record["count"]
        st.markdown(
            f"""
<div class="history-row">
  <div class="history-bubble">
    <div class="history-meta">{i}番手</div>
    <div class="history-main">投手: {pitcher}</div>
    <div class="history-count">投球数: {c} 球</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
else:
    st.markdown('<div class="empty-history">まだ履歴はありません。</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
