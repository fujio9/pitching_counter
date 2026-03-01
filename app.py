"""
野球投手 投球数カウントアプリ
Python + Streamlit / スマホ向け片手操作
"""

import streamlit as st
import streamlit.components.v1 as components

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

# --- カスタム CSS（aria-label で投球・＋・−のみ指定・交代・リセットには影響しない）---
st.markdown(
    """
<style>
  /* 投球ボタン: 約3倍の文字サイズ・太字・押しやすい高さ */
  button[aria-label="投球"] {
    font-size: 4rem !important;
    font-weight: 900 !important;
    min-height: 140px !important;
    border-radius: 16px !important;
  }
  /* ＋ボタン */
  button[aria-label="＋"] {
    font-size: 4rem !important;
    font-weight: 900 !important;
    min-height: 100px !important;
    border-radius: 16px !important;
  }
  /* −ボタン */
  button[aria-label="−"] {
    font-size: 4rem !important;
    font-weight: 900 !important;
    min-height: 100px !important;
    border-radius: 16px !important;
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
    last_count = None
    for record in reversed(st.session_state.history):
        if str(record["number"]) == str(current):
            last_count = record["count"]
            break
    if last_count is not None:
        st.session_state.current_count = last_count
    st.session_state.prev_pitcher_input = current

# --- カウント表示（中央・大きく）---
count = st.session_state.current_count
st.markdown(
    f'<div style="text-align: center;"><span style="font-size: 4rem; font-weight: 700;">{count}</span><span style="font-size: 1.5rem;"> 球</span></div>',
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

# --- 投球ボタン（中央・「投球」表示）---
col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    if st.button("投球", key="pitch_button", use_container_width=True):
        st.session_state.current_count += 1
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- ＋ / −（横並び）---
col_m, col_gap, col_p = st.columns([1, 1, 1])
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

# 投球・＋・− に aria-label を付与（CSS の button[aria-label="..."] で個別指定するため）
_script = """
<script>
(function() {
  function setLabels() {
    var doc = window.parent.document;
    doc.querySelectorAll('button').forEach(function(b) {
      var t = (b.innerText || b.textContent || '').trim();
      if (t === '投球') b.setAttribute('aria-label', '投球');
      else if (t === '＋') b.setAttribute('aria-label', '＋');
      else if (t === '−') b.setAttribute('aria-label', '−');
    });
  }
  setLabels();
  window.parent.setTimeout(setLabels, 300);
})();
</script>
"""
components.html(_script, height=0)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- 交代する ---
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
