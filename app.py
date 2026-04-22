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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { font-family: 'Inter', sans-serif; background: #111317; }

[data-testid="stAppViewContainer"] { background: #111317 !important; font-family: 'Inter', sans-serif !important; }
[data-testid="stHeader"]  { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stMain"] > div { padding-top: 0 !important; }

/* ── FIXED LEFT NAV ── */
.nav {
    position: fixed;
    top: 0; left: 0;
    width: 230px;
    height: 100vh;
    background: #1a1d23;
    border-right: 1px solid #2a2d35;
    display: flex;
    flex-direction: column;
    padding: 1.8rem 1.5rem;
    gap: 1.6rem;
    z-index: 100;
    overflow-y: auto;
}

.nav-logo-wrap { display: flex; align-items: center; gap: 0.6rem; }
.nav-logo-icon {
    width: 32px; height: 32px;
    background: #6366f1;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
}
.nav-logo      { font-size: 0.95rem; font-weight: 700; color: #f0f0f0; letter-spacing: -0.2px; }
.nav-logo-sub  { font-size: 0.6rem; color: #555; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 1px; }

.nav-rule { border: none; border-top: 1px solid #2a2d35; }

.nav-section { font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.14em; color: #555; font-weight: 600; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.4rem; }

.nav-plan {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.55rem 0.75rem;
    border-radius: 8px;
    margin-bottom: 0.3rem;
    background: #1e2128;
    border: 1px solid #2a2d35;
    font-size: 0.78rem;
}
.nav-plan-n { color: #aaa; display: flex; align-items: center; gap: 0.4rem; }
.nav-plan-p { color: #fff; font-weight: 700; font-size: 0.82rem; }

.nav-feat {
    font-size: 0.75rem; color: #888;
    padding: 0.3rem 0;
    display: flex; align-items: center; gap: 0.5rem;
}
.nav-feat-icon { font-size: 0.75rem; }

.nav-policy {
    background: #1e2128;
    border: 1px solid #2a2d35;
    border-radius: 8px;
    padding: 0.6rem 0.75rem;
    font-size: 0.73rem;
    color: #666;
    display: flex; align-items: flex-start; gap: 0.4rem;
    line-height: 1.5;
}

.nav-intent { margin-top: auto; background: #1e2128; border: 1px solid #2a2d35; border-radius: 10px; padding: 0.85rem 0.9rem; }
.nav-int-lbl { font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.14em; color: #555; margin-bottom: 0.5rem; font-weight: 600; display: flex; align-items: center; gap: 0.35rem; }
.iv-wait    { font-size: 0.78rem; color: #555; font-style: italic; }
.iv-greet   { font-size: 0.78rem; color: #4ade80; font-weight: 600; }
.iv-inquiry { font-size: 0.78rem; color: #60a5fa; font-weight: 600; }
.iv-hot     { font-size: 0.78rem; color: #fb923c; font-weight: 700; }

/* ── MAIN ── */
.main {
    margin-left: 230px;
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: #111317;
}

/* ── TOPBAR ── */
.topbar {
    background: #1a1d23;
    border-bottom: 1px solid #2a2d35;
    padding: 0.85rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
}
.tb-left { display: flex; align-items: center; gap: 0.75rem; }
.tb-avatar {
    width: 34px; height: 34px;
    background: #6366f1;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
}
.tb-name { font-size: 0.88rem; font-weight: 600; color: #f0f0f0; }
.tb-role { font-size: 0.68rem; color: #666; margin-top: 1px; }
.tb-right { display: flex; align-items: center; gap: 0.6rem; }
.tb-online {
    display: flex; align-items: center; gap: 0.4rem;
    background: #1b2e1e; border: 1px solid #2d4a30;
    border-radius: 20px; padding: 3px 10px;
    font-size: 0.68rem; color: #4ade80; font-weight: 500;
}
.tb-online-dot { width: 6px; height: 6px; background: #4ade80; border-radius: 50%; }
.tb-badge { font-size: 0.62rem; color: #555; border: 1px solid #2a2d35; border-radius: 4px; padding: 3px 8px; letter-spacing: 0.06em; text-transform: uppercase; background: #1e2128; }

/* ── MESSAGES ── */
.msgs {
    flex: 1;
    overflow-y: auto;
    padding: 2rem 3rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-width: 900px;
    width: 100%;
    margin: 0 auto;
    align-self: stretch;
}

.welcome { padding: 1.5rem 0 1rem; max-width: 540px; }
.w-eyebrow { font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.14em; color: #555; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.4rem; }
.w-title { font-size: 1.65rem; font-weight: 300; color: #e8e8e8; line-height: 1.25; letter-spacing: -0.4px; margin-bottom: 0.5rem; }
.w-title b { font-weight: 700; color: #fff; }
.w-sub { font-size: 0.8rem; color: #666; line-height: 1.7; }
.chips { display: flex; flex-wrap: wrap; gap: 0.45rem; margin-top: 1.2rem; }
.chip {
    background: #1e2128; border: 1px solid #2a2d35;
    border-radius: 20px; padding: 0.35rem 0.9rem;
    font-size: 0.74rem; color: #aaa;
    font-family: 'Inter', sans-serif;
    display: flex; align-items: center; gap: 0.35rem;
}

.msg-u { display: flex; justify-content: flex-end; }
.msg-a { display: flex; align-items: flex-start; gap: 0.65rem; }

.a-dot {
    width: 28px; height: 28px;
    background: #6366f1;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; flex-shrink: 0; margin-top: 2px;
}

.bub-u {
    background: #f0f0f0;
    color: #111;
    padding: 0.7rem 1.1rem;
    border-radius: 18px 18px 3px 18px;
    max-width: 58%;
    font-size: 0.84rem;
    line-height: 1.6;
    font-weight: 400;
}

.bub-a {
    background: #1e2128;
    border: 1px solid #2a2d35;
    color: #d0d0d0;
    padding: 0.7rem 1.1rem;
    border-radius: 3px 18px 18px 18px;
    max-width: 66%;
    font-size: 0.84rem;
    line-height: 1.6;
}

/* ── LEAD CARD ── */
.lead-card {
    background: #1b2e1e;
    border: 1px solid #2d4a30;
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    max-width: 66%;
}
.lc-top { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.12em; color: #4ade80; font-weight: 700; margin-bottom: 0.85rem; display: flex; align-items: center; gap: 0.4rem; }
.lc-row { display: flex; justify-content: space-between; padding: 0.42rem 0; border-bottom: 1px solid #243527; font-size: 0.8rem; }
.lc-row:last-child { border-bottom: none; }
.lc-k { color: #6a9e7a; display: flex; align-items: center; gap: 0.4rem; }
.lc-v { color: #e0e0e0; font-weight: 500; }

/* ── INPUT ── */
[data-testid="stChatInputContainer"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 230px !important;
    right: 0 !important;
    padding: 0.6rem 3rem 0.8rem !important;
    background: #111317 !important;
    border-top: 1px solid #1e2128 !important;
    z-index: 99 !important;
}
[data-testid="stChatInput"] > div {
    background: #2a2d35 !important;
    border: 1px solid #3a3d45 !important;
    border-radius: 10px !important;
    max-width: 700px !important;
    margin: 0 auto !important;
    min-height: 42px !important;
    max-height: 42px !important;
}
[data-testid="stChatInput"] textarea {
    background: #2a2d35 !important;
    color: #ffffff !important;
    caret-color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    min-height: 42px !important;
    max-height: 42px !important;
    padding: 0.55rem 0.9rem !important;
    resize: none !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #888 !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ────────────────────────────────────────────────────────
if "agent" not in st.session_state:
    st.session_state.agent = build_agent()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "messages": [], "intent": "",
        "lead_name": "", "lead_email": "", "lead_platform": "",
        "lead_captured": False, "awaiting": ""
    }
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"inflx-{int(time.time())}"

intent        = st.session_state.agent_state.get("intent", "")
lead_captured = st.session_state.agent_state.get("lead_captured", False)
s             = st.session_state.agent_state

if intent == "casual_greeting":
    iv = '<div class="iv-greet">👋 Casual greeting</div>'
elif intent == "product_inquiry":
    iv = '<div class="iv-inquiry">🔍 Product inquiry</div>'
elif intent == "high_intent":
    iv = '<div class="iv-hot">🔥 High intent — ready to sign up!</div>'
else:
    iv = '<div class="iv-wait">Waiting for first message…</div>'

# ── Fixed left nav ───────────────────────────────────────────────────────
st.markdown(f"""
<div class="nav">
  <div class="nav-logo-wrap">
    <div class="nav-logo-icon">🎬</div>
    <div>
      <div class="nav-logo">AutoStream</div>
      <div class="nav-logo-sub">Inflx · ServiceHive</div>
    </div>
  </div>

  <hr class="nav-rule">

  <div>
    <div class="nav-section">💰 Pricing</div>
    <div class="nav-plan">
      <span class="nav-plan-n">📦 Basic</span>
      <span class="nav-plan-p">$29/mo</span>
    </div>
    <div class="nav-plan">
      <span class="nav-plan-n">⭐ Pro</span>
      <span class="nav-plan-p">$79/mo</span>
    </div>
  </div>

  <div>
    <div class="nav-section">✨ Pro includes</div>
    <div class="nav-feat"><span class="nav-feat-icon">♾️</span> Unlimited videos</div>
    <div class="nav-feat"><span class="nav-feat-icon">🎥</span> 4K resolution</div>
    <div class="nav-feat"><span class="nav-feat-icon">📝</span> AI auto-captions</div>
    <div class="nav-feat"><span class="nav-feat-icon">🛟</span> 24/7 support</div>
  </div>

  <div>
    <div class="nav-section">📋 Policy</div>
    <div class="nav-policy">⚠️ No refunds after 7 days of purchase</div>
  </div>

  <div class="nav-intent">
    <div class="nav-int-lbl">📡 Intent signal</div>
    {iv}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Main layout ──────────────────────────────────────────────────────────
_, right_col = st.columns([1, 3.8], gap="small")

with right_col:
    st.markdown("""
    <div class="main">
      <div class="topbar">
        <div class="tb-left">
          <div class="tb-avatar">🤖</div>
          <div>
            <div class="tb-name">AutoStream Assistant</div>
            <div class="tb-role">🎯 Lead qualification · Powered by Inflx · ServiceHive</div>
          </div>
        </div>
        <div class="tb-right">
          <div class="tb-online"><div class="tb-online-dot"></div>Online</div>
          <div class="tb-badge">🧠 NVIDIA NIM</div>
        </div>
      </div>
      <div class="msgs">
    """, unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.markdown("""
        <div class="welcome">
          <div class="w-eyebrow">🤖 AutoStream Agent</div>
          <div class="w-title">Hi there —<br><b>how can I help you?</b></div>
          <div class="w-sub">Ask about pricing, features, or get started with a plan.</div>
          <div class="chips">
            <div class="chip">💰 What plans do you offer?</div>
            <div class="chip">⭐ Tell me about Pro</div>
            <div class="chip">🚀 I want to sign up</div>
            <div class="chip">↩️ Refund policy</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    for entry in st.session_state.chat_history:
        if entry["role"] == "user":
            st.markdown(f"""
            <div class="msg-u">
              <div class="bub-u">{entry["content"]}</div>
            </div>""", unsafe_allow_html=True)
        else:
            if entry.get("is_lead_card"):
                st.markdown(f"""
                <div class="msg-a">
                  <div class="a-dot">🤖</div>
                  <div class="lead-card">
                    <div class="lc-top">✅ Lead captured successfully</div>
                    <div class="lc-row"><span class="lc-k">👤 Name</span><span class="lc-v">{s.get("lead_name","")}</span></div>
                    <div class="lc-row"><span class="lc-k">📧 Email</span><span class="lc-v">{s.get("lead_email","")}</span></div>
                    <div class="lc-row"><span class="lc-k">📱 Platform</span><span class="lc-v">{s.get("lead_platform","")}</span></div>
                  </div>
                </div>""", unsafe_allow_html=True)
            else:
                content = entry["content"].replace("\n", "<br>")
                st.markdown(f"""
                <div class="msg-a">
                  <div class="a-dot">🤖</div>
                  <div class="bub-a">{content}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

# ── Chat input ───────────────────────────────────────────────────────────
if not lead_captured:
    user_input = st.chat_input("💬 Ask me anything about AutoStream…")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        current_state = st.session_state.agent_state.copy()
        current_state["messages"] = [HumanMessage(content=user_input)]
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        with st.spinner(""):
            result = st.session_state.agent.invoke(current_state, config=config)
        ai_msgs = [m for m in result["messages"] if isinstance(m, AIMessage)]
        if ai_msgs:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": ai_msgs[-1].content,
                "intent": result.get("intent", ""),
                "is_lead_card": result.get("lead_captured", False)
            })
        st.session_state.agent_state = {
            "messages": [],
            "intent":        result.get("intent", ""),
            "lead_name":     result.get("lead_name", ""),
            "lead_email":    result.get("lead_email", ""),
            "lead_platform": result.get("lead_platform", ""),
            "lead_captured": result.get("lead_captured", False),
            "awaiting":      result.get("awaiting", "")
        }
        st.rerun()
else:
    if st.button("🔄 Start new conversation"):
        st.session_state.chat_history = []
        st.session_state.agent_state = {
            "messages": [], "intent": "", "lead_name": "",
            "lead_email": "", "lead_platform": "",
            "lead_captured": False, "awaiting": ""
        }
        st.session_state.thread_id = f"inflx-{int(time.time())}"
        st.rerun()