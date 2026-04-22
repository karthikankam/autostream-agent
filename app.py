import os
import time
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from agent import build_agent

# ───────────────────────────────
# PAGE CONFIG
# ───────────────────────────────
st.set_page_config(
    page_title="AutoStream",
    page_icon="🎬",
    layout="wide"
)

# ───────────────────────────────
# CLEAN MODERN CSS
# ───────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body {
    font-family: 'Inter', sans-serif;
    background: #0f1115;
}

/* Hide Streamlit UI */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stSidebar"],
footer, #MainMenu {
    display: none !important;
}

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ───────── SIDEBAR ───────── */
.nav {
    position: fixed;
    top: 0;
    left: 0;
    width: 240px;
    height: 100vh;
    background: #151922;
    border-right: 1px solid #242836;
    padding: 22px 18px;
    display: flex;
    flex-direction: column;
    gap: 18px;
}

.nav-logo-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
}

.nav-logo-icon {
    width: 34px;
    height: 34px;
    background: #6366f1;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.nav-logo {
    font-size: 14px;
    font-weight: 700;
    color: white;
}

.nav-logo-sub {
    font-size: 11px;
    color: #777;
}

.nav-section {
    font-size: 10px;
    letter-spacing: 1.2px;
    color: #666;
    text-transform: uppercase;
}

/* ───────── MAIN ───────── */
.main {
    margin-left: 240px;
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: #0f1115;
}

/* TOPBAR */
.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 26px;
    background: #151922;
    border-bottom: 1px solid #242836;
}

.tb-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.tb-avatar {
    width: 36px;
    height: 36px;
    background: #6366f1;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.tb-name { color: white; font-weight: 600; }
.tb-role { font-size: 12px; color: #777; }

.tb-online {
    display: flex;
    align-items: center;
    gap: 6px;
    background: #142a18;
    padding: 4px 10px;
    border-radius: 999px;
    color: #4ade80;
    font-size: 12px;
}

/* ───────── CHAT ───────── */
.msgs {
    flex: 1;
    overflow-y: auto;
    padding: 26px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    max-width: 820px;
    width: 100%;
    margin: 0 auto;
}

/* USER BUBBLE */
.msg-u {
    display: flex;
    justify-content: flex-end;
}

.bub-u {
    background: #e5e7eb;
    color: #111;
    padding: 10px 14px;
    border-radius: 16px 16px 4px 16px;
    max-width: 70%;
    font-size: 14px;
}

/* AI BUBBLE */
.msg-a {
    display: flex;
    gap: 10px;
    align-items: flex-start;
}

.a-dot {
    width: 30px;
    height: 30px;
    background: #6366f1;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.bub-a {
    background: #1b1f2a;
    border: 1px solid #2a3042;
    color: #ddd;
    padding: 10px 14px;
    border-radius: 4px 16px 16px 16px;
    max-width: 75%;
    font-size: 14px;
    line-height: 1.5;
}

/* ───────── INPUT ───────── */
[data-testid="stChatInputContainer"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 240px !important;
    right: 0 !important;
    padding: 14px 24px !important;
    background: #0f1115 !important;
    border-top: 1px solid #242836 !important;
}

[data-testid="stChatInput"] textarea {
    background: #1b1f2a !important;
    color: white !important;
    font-size: 14px !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ───────────────────────────────
# SESSION STATE
# ───────────────────────────────
if "agent" not in st.session_state:
    st.session_state.agent = build_agent()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "messages": [],
        "intent": "",
        "lead_name": "",
        "lead_email": "",
        "lead_platform": "",
        "lead_captured": False,
        "awaiting": ""
    }

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"session-{int(time.time())}"

# ───────────────────────────────
# SIDEBAR
# ───────────────────────────────
st.markdown("""
<div class="nav">
  <div class="nav-logo-wrap">
    <div class="nav-logo-icon">🎬</div>
    <div>
      <div class="nav-logo">AutoStream</div>
      <div class="nav-logo-sub">AI Assistant</div>
    </div>
  </div>

  <div class="nav-section">💰 Pricing</div>
  <div class="nav-plan">Basic — $29</div>
  <div class="nav-plan">Pro — $79</div>

  <div class="nav-section">✨ Features</div>
  <div class="nav-plan">AI Captions</div>
  <div class="nav-plan">4K Export</div>
  <div class="nav-plan">Fast Rendering</div>
</div>
""", unsafe_allow_html=True)

# ───────────────────────────────
# MAIN UI
# ───────────────────────────────
_, right = st.columns([1, 3.5])

with right:
    st.markdown("""
    <div class="main">
      <div class="topbar">
        <div class="tb-left">
          <div class="tb-avatar">🤖</div>
          <div>
            <div class="tb-name">AutoStream Assistant</div>
            <div class="tb-role">Lead Qualification AI</div>
          </div>
        </div>
        <div class="tb-online">● Online</div>
      </div>

      <div class="msgs">
    """, unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="msg-u">
                <div class="bub-u">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-a">
                <div class="a-dot">🤖</div>
                <div class="bub-a">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

# ───────────────────────────────
# CHAT INPUT
# ───────────────────────────────
user_input = st.chat_input("Ask something about AutoStream...")

if user_input:
    # Save user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    # Run agent
    current_state = st.session_state.agent_state.copy()
    current_state["messages"] = [HumanMessage(content=user_input)]

    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    result = st.session_state.agent.invoke(current_state, config=config)

    ai_msgs = [m for m in result["messages"] if isinstance(m, AIMessage)]

    if ai_msgs:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": ai_msgs[-1].content
        })

    st.session_state.agent_state = result

    st.rerun()
