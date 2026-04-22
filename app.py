import os
import time
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from agent import build_agent

st.set_page_config(
    page_title="AutoStream",
    page_icon="🎬",
    layout="wide"
)

# ───────────────────────── CSS (clean + stable) ─────────────────────────
st.markdown("""
<style>
html, body {
    font-family: Inter, sans-serif;
    background: #0f1115;
}

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

.main {
    margin-left: 240px;
    display: flex;
    flex-direction: column;
    height: 100vh;
}

.topbar {
    padding: 14px 24px;
    background: #151922;
    border-bottom: 1px solid #242836;
    color: white;
}

.msgs {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    max-width: 800px;
    margin: auto;
}

.msg-u {
    display: flex;
    justify-content: flex-end;
}

.msg-a {
    display: flex;
    gap: 10px;
}

.bub-u {
    background: #e5e7eb;
    color: #111;
    padding: 10px 14px;
    border-radius: 14px;
    max-width: 70%;
}

.bub-a {
    background: #1b1f2a;
    color: #ddd;
    padding: 10px 14px;
    border-radius: 14px;
    max-width: 75%;
}

[data-testid="stChatInputContainer"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 240px !important;
    right: 0 !important;
    background: #0f1115 !important;
}
</style>
""", unsafe_allow_html=True)

# ───────────────────────── SESSION STATE ─────────────────────────
if "agent" not in st.session_state:
    st.session_state.agent = build_agent()

if "chat" not in st.session_state:
    st.session_state.chat = []

if "state" not in st.session_state:
    st.session_state.state = {
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

# ───────────────────────── UI ─────────────────────────
st.markdown('<div class="main">', unsafe_allow_html=True)

st.markdown("""
<div class="topbar">
🎬 AutoStream AI Assistant
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="msgs">', unsafe_allow_html=True)

for msg in st.session_state.chat:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="msg-u">
            <div class="bub-u">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-a">
            <div class="bub-a">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div></div>", unsafe_allow_html=True)

# ───────────────────────── CHAT INPUT ─────────────────────────
user_input = st.chat_input("Ask something...")

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})

    current_state = st.session_state.state.copy()
    current_state["messages"] = [HumanMessage(content=user_input)]

    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    try:
        result = st.session_state.agent.invoke(current_state, config=config)
    except Exception as e:
        st.error(f"❌ Agent Error: {e}")
        st.stop()

    ai_msgs = [m for m in result["messages"] if isinstance(m, AIMessage)]

    if ai_msgs:
        st.session_state.chat.append({
            "role": "assistant",
            "content": ai_msgs[-1].content
        })

    st.session_state.state = result

    st.rerun()
