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


# --- メイン投球ボタン用 CSS（丸形・80px以上）---
st.markdown(
    """
<style>
  div[data-testid="column"]:nth-of-type(2) button {
    min-height: 80px !important;
    height: 80px !important;
    width: 80px !important;
    max-width: 80px !important;
    border-radius: 50% !important;
    font-size: 1.1rem;
    margin: 0 auto;
  }
</style>
""",
    unsafe_allow_html=True,
)

# --- 背番号入力 ---
st.session_state.current_pitcher = st.text_input(
    "現在の投手の背番号",
    value=st.session_state.current_pitcher,
    key="pitcher_input",
    placeholder="例: 18",
).strip()

# --- 同じ背番号を入力した場合、履歴の投球数から再開 ---
current = st.session_state.current_pitcher
prev = st.session_state.prev_pitcher_input
if current != prev:
    # 履歴でこの背番号の最後の登板を検索
    last_count = None
    for record in reversed(st.session_state.history):
        if str(record["number"]) == str(current):
            last_count = record["count"]
            break
    if last_count is not None:
        st.session_state.current_count = last_count
    st.session_state.prev_pitcher_input = current

# --- 投球数 超大きく中央表示 ---
count = st.session_state.current_count
st.markdown(
    f'<div style="text-align: center;"><span style="font-size: 4rem; font-weight: 700;">{count}</span><span style="font-size: 1.5rem;"> 球</span></div>',
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

# --- メイン「投球」ボタン（中央配置）---
col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    if st.button("投球", key="main_pitch", use_container_width=True):
        st.session_state.current_count += 1
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- ＋ / − 横並び（間隔あり）---
col_minus, col_gap, col_plus = st.columns([1, 1, 1])
with col_minus:
    if st.button("−", key="btn_minus", use_container_width=True):
        st.session_state.current_count = max(0, st.session_state.current_count - 1)
        st.rerun()
with col_gap:
    st.write("")  # スペーサ
with col_plus:
    if st.button("＋", key="btn_plus", use_container_width=True):
        st.session_state.current_count += 1
        st.rerun()

st.markdown("<br><br>", unsafe_allow_html=True)

# --- 「交代する」幅広ボタン ---
if st.button("交代する", key="change_pitcher", use_container_width=True):
    st.session_state.history.append(
        {"number": st.session_state.current_pitcher or "—", "count": st.session_state.current_count}
    )
    st.session_state.current_count = 0
    st.rerun()

# --- 投球数・履歴をリセットするボタン ---
if st.button("投球数・履歴をリセット", key="reset_all", use_container_width=True):
    st.session_state.current_count = 0
    st.session_state.history = []
    st.session_state.prev_pitcher_input = None
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- 履歴一覧（登板順）---
if st.session_state.history:
    st.subheader("登板履歴")
    for i, record in enumerate(st.session_state.history, start=1):
        num = record["number"]
        c = record["count"]
        st.caption(f"{i}番手: 背番号 {num} — {c} 球")
