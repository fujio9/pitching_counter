"""
野球投手 投球数カウントアプリ
Python + Streamlit / スマホ向け片手操作
"""

import base64
from pathlib import Path

import streamlit as st

# --- Page config ---
st.set_page_config(
    page_title="投球数カウント",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- baseball.png を base64 で読み込み（app.py と同階層 / カレントディレクトリ）---
# ローカル・Streamlit Cloud 両対応: __file__ の親ディレクトリと cwd の両方を試す
try:
    BASE_DIR = Path(__file__).resolve().parent
except NameError:
    BASE_DIR = Path.cwd()
BASEBALL_B64 = None
for path in [BASE_DIR / "baseball.png", Path.cwd() / "baseball.png"]:
    try:
        with open(path, "rb") as f:
            raw = base64.b64encode(f.read()).decode("ascii")
            BASEBALL_B64 = raw.replace("\n", "").replace("\r", "")
        break
    except (FileNotFoundError, OSError):
        continue

# --- Session state 初期化 ---
if "current_pitcher" not in st.session_state:
    st.session_state.current_pitcher = ""
if "current_count" not in st.session_state:
    st.session_state.current_count = 0
if "history" not in st.session_state:
    st.session_state.history = []
if "prev_pitcher_input" not in st.session_state:
    st.session_state.prev_pitcher_input = None

# --- カスタム CSS（投球ボタン・＋/−・交代する）---
# data URL 形式で CSS に埋め込む（相対パスは Streamlit で参照されないため）
_bg = f'url("data:image/png;base64,{BASEBALL_B64}")' if BASEBALL_B64 else "none"
_pitch_bg = (
    f"background-image: {_bg}; background-size: cover; background-position: center;"
    if BASEBALL_B64
    else "background-color: #e0e0e0;"  # 画像なし時は円形が分かるようフォールバック
)

custom_css = f"""
<style>
  /* 投球ボタン: pitch-button-marker 直後のブロックの中央列を指定 */
  [data-testid="stMarkdown"]:has(.pitch-button-marker) + * div[data-testid="column"]:nth-of-type(2) button {{
    min-height: 200px !important;
    height: 200px !important;
    width: 200px !important;
    max-width: 200px !important;
    border-radius: 50% !important;
    {_pitch_bg}
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    font-size: 0 !important;
    color: transparent !important;
    margin-left: auto !important;
    margin-right: auto !important;
    display: block !important;
  }}
  [data-testid="stMarkdown"]:has(.pitch-button-marker) + * div[data-testid="column"]:nth-of-type(2) button:active {{
    transform: scale(0.95);
  }}
  /* ＋ / − ボタン: 高さ60px以上（plus-minus-marker 直後の1列目と3列目） */
  [data-testid="stMarkdown"]:has(.plus-minus-marker) + * div[data-testid="column"]:nth-of-type(1) button,
  [data-testid="stMarkdown"]:has(.plus-minus-marker) + * div[data-testid="column"]:nth-of-type(3) button {{
    min-height: 60px !important;
  }}
  /* 交代するボタン: 高さ60px以上・目立つ */
  :has(.change-btn-container) + div.stButton button {{
    min-height: 60px !important;
    font-weight: bold !important;
    font-size: 1.1rem !important;
  }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

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
    last_count = None
    for record in reversed(st.session_state.history):
        if str(record["number"]) == str(current):
            last_count = record["count"]
            break
    if last_count is not None:
        st.session_state.current_count = last_count
    st.session_state.prev_pitcher_input = current

# --- カウント表示（最上部・超大きく中央・「◯◯ 球」）---
count = st.session_state.current_count
st.markdown(
    f'<div style="text-align: center;"><span style="font-size: 4rem; font-weight: 700;">{count}</span><span style="font-size: 1.5rem;"> 球</span></div>',
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

# --- 投球ボタン（中央・画像のみ・文字なし）---
# マーカーで「この直後の横ブロックの中央列」を CSS で一意に指定
st.markdown('<div class="pitch-button-marker"></div>', unsafe_allow_html=True)
col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    if st.button(" ", key="pitch_button", use_container_width=True):
        st.session_state.current_count += 1
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- ＋ / − 横並び（間隔・高さ60px以上）---
st.markdown('<div class="plus-minus-marker"></div>', unsafe_allow_html=True)
col_minus, col_gap, col_plus = st.columns([1, 1, 1])
with col_minus:
    if st.button("−", key="btn_minus", use_container_width=True):
        st.session_state.current_count = max(0, st.session_state.current_count - 1)
        st.rerun()
with col_gap:
    st.write("")
with col_plus:
    if st.button("＋", key="btn_plus", use_container_width=True):
        st.session_state.current_count += 1
        st.rerun()

st.markdown("<br><br>", unsafe_allow_html=True)

# --- 「交代する」幅広・目立つ ---
st.markdown('<div class="change-btn-container"></div>', unsafe_allow_html=True)
if st.button("交代する", key="change_pitcher", use_container_width=True):
    st.session_state.history.append(
        {"number": st.session_state.current_pitcher or "—", "count": st.session_state.current_count}
    )
    st.session_state.current_count = 0
    st.rerun()

# --- 投球数・履歴をリセット ---
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
