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

# --- カスタム CSS（LINEライト風）---
st.markdown(
    """
<style>
  .stApp {
    background: #f5f6f8;
  }
  .line-header {
    background: #06c755;
    color: #ffffff;
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 12px;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
  }
  .line-header-title {
    font-size: 1.15rem;
    font-weight: 700;
  }
  .line-header-sub {
    margin-top: 4px;
    font-size: 0.92rem;
    opacity: 0.95;
  }
  .count-card {
    background: #ffffff;
    border-radius: 18px;
    padding: 18px 16px 14px;
    margin: 8px 0 12px;
    box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
    text-align: center;
  }
  .count-label {
    color: #6f7785;
    font-size: 0.95rem;
    margin-bottom: 4px;
  }
  .count-value {
    font-size: 4rem;
    font-weight: 800;
    color: #111827;
    line-height: 1.1;
  }
  .count-unit {
    font-size: 1.35rem;
    color: #111827;
    margin-left: 6px;
  }
  .section-label {
    color: #6b7280;
    font-size: 0.92rem;
    font-weight: 600;
    margin: 4px 2px 8px;
  }
  .history-area {
    margin-top: 8px;
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

  /* 主操作ボタン（投球、＋、−） */
  :has(.main-action-marker) + * div.stButton > button {
    background: #06c755 !important;
    color: #ffffff !important;
    border: none !important;
    min-height: 110px !important;
    border-radius: 18px !important;
    font-size: 3.2rem !important;
    font-weight: 900 !important;
    box-shadow: 0 8px 18px rgba(6, 199, 85, 0.28) !important;
    transition: transform 0.08s ease, box-shadow 0.08s ease !important;
  }
  :has(.main-action-marker) + * div.stButton > button:active {
    transform: scale(0.97);
    box-shadow: 0 4px 10px rgba(6, 199, 85, 0.22) !important;
  }
  :has(.plus-minus-marker) + * div.stButton > button,
  :has(.plus-minus-marker) + * + * div.stButton > button {
    background: #06c755 !important;
    color: #ffffff !important;
    border: none !important;
    min-height: 92px !important;
    border-radius: 16px !important;
    font-size: 3rem !important;
    font-weight: 900 !important;
    box-shadow: 0 8px 16px rgba(6, 199, 85, 0.24) !important;
  }

  /* 副操作ボタン（交代、リセット） */
  :has(.secondary-buttons) + * div.stButton > button,
  :has(.secondary-buttons) + * + * div.stButton > button {
    min-height: 54px !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
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
  <div class="line-header-title">Pitch Counter</div>
  <div class="line-header-sub">現在の投手: {current_pitcher_view}</div>
</div>
""",
    unsafe_allow_html=True,
)

# --- 投手入力（背番号・名前・任意テキスト） ---
st.session_state.current_pitcher = st.text_input(
    "現在の投手（背番号・名前・任意テキスト）",
    value=st.session_state.current_pitcher,
    key="pitcher_input",
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
st.markdown('<div class="main-action-marker"></div>', unsafe_allow_html=True)
col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    if st.button("投球", key="pitch_button", use_container_width=True):
        st.session_state.current_count += 1
        st.rerun()

# --- ＋ / −（横並び）---
st.markdown('<div class="plus-minus-marker"></div>', unsafe_allow_html=True)
col_m, col_gap, col_p = st.columns([1, 0.35, 1])
with col_m:
    if st.button("−", key="btn_minus", use_container_width=True):
        st.session_state.current_count = max(0, st.session_state.current_count - 1)
        st.rerun()
with col_gap:
    st.write("")
with col_p:
    if st.button("＋", key="btn_plus", use_container_width=True):
        st.session_state.current_count += 1
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- 副操作 ---
st.markdown('<div class="section-label">投手管理</div>', unsafe_allow_html=True)
st.markdown('<div class="secondary-buttons"></div>', unsafe_allow_html=True)
if st.button("交代する", key="change_pitcher", use_container_width=True):
    st.session_state.history.append(
        {"pitcher": st.session_state.current_pitcher or "—", "count": st.session_state.current_count}
    )
    st.session_state.current_count = 0
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
