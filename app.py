import os
import time
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from agent import build_agent

st.set_page_config(page_title="AutoStream", page_icon="🎬", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif;
    background: #0e0e0e !important;
    color: #e0e0e0;
}
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stSidebar"], footer, #MainMenu { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stMain"] > div { padding-top: 0 !important; }

/* NAV */
.nav {
    position: fixed; top: 0; left: 0;
    width: 220px; height: 100vh;
    background: #0e0e0e;
    border-right: 1px solid #1c1c1c;
    padding: 2rem 1.4rem;
    display: flex; flex-direction: column; gap: 2rem;
    z-index: 100; overflow-y: auto;
}
.nav-brand { font-size: 0.95rem; font-weight: 600; color: #fff; letter-spacing: -0.2px; }
.nav-brand-sub { font-size: 0.62rem; color: #3a3a3a; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 3px; }
.nav-sep { border: none; border-top: 1px solid #1c1c1c; }
.nav-lbl { font-size: 0.58rem; text-transform: uppercase; letter-spacing: 0.14em; color: #3a3a3a; font-weight: 500; margin-bottom: 0.8rem; }
.nav-plan { display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #1a1a1a; font-size: 0.78rem; }
.nav-plan:last-child { border-bottom: none; }
.nav-plan-n { color: #555; }
.nav-plan-p { color: #e0e0e0; font-weight: 600; }
.nav-feat { font-size: 0.74rem; color: #444; padding: 0.25rem 0; display: flex; align-items: center; gap: 0.45rem; }
.nav-note { font-size: 0.72rem; color: #333; line-height: 1.5; padding: 0.6rem 0.7rem; border: 1px solid #1c1c1c; border-radius: 6px; }
.nav-intent { margin-top: auto; padding-top: 1.2rem; border-top: 1px solid #1c1c1c; }
.nav-int-lbl { font-size: 0.58rem; text-transform: uppercase; letter-spacing: 0.14em; color: #3a3a3a; margin-bottom: 0.4rem; }
.iv-wait    { font-size: 0.76rem; color: #333; font-style: italic; }
.iv-greet   { font-size: 0.76rem; color: #4ade80; font-weight: 500; }
.iv-inquiry { font-size: 0.76rem; color: #60a5fa; font-weight: 500; }
.iv-hot     { font-size: 0.76rem; color: #f87171; font-weight: 600; }

/* TOPBAR */
.topbar {
    position: fixed; top: 0; left: 220px; right: 0;
    height: 52px;
    background: #0e0e0e;
    border-bottom: 1px solid #1c1c1c;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 2rem;
    z-index: 99;
}
.tb-name { font-size: 0.84rem; font-weight: 500; color: #c0c0c0; }
.tb-role { font-size: 0.66rem; color: #3a3a3a; margin-top: 1px; }
.tb-right { display: flex; align-items: center; gap: 0.8rem; }
.tb-dot { width: 6px; height: 6px; background: #4ade80; border-radius: 50%; }
.tb-online { font-size: 0.68rem; color: #4ade80; display: flex; align-items: center; gap: 0.35rem; }
.tb-nim { font-size: 0.62rem; color: #333; border: 1px solid #1c1c1c; border-radius: 4px; padding: 2px 7px; }

/* MESSAGES */
.msgs {
    position: fixed;
    top: 52px; left: 220px; right: 0;
    bottom: 64px;
    overflow-y: auto;
    padding: 2rem 4rem;
    display: flex; flex-direction: column; gap: 1rem;
}
.welcome { padding: 1rem 0 1.5rem; max-width: 500px; }
.w-hi    { font-size: 1.5rem; font-weight: 300; color: #888; letter-spacing: -0.3px; line-height: 1.3; }
.w-hi b  { font-weight: 600; color: #e8e8e8; }
.w-sub   { font-size: 0.78rem; color: #333; margin-top: 0.5rem; line-height: 1.6; }
.chips   { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 1rem; }
.chip    { border: 1px solid #1c1c1c; border-radius: 20px; padding: 0.3rem 0.8rem; font-size: 0.72rem; color: #444; background: transparent; font-family: 'Inter', sans-serif; }

.msg-u { display: flex; justify-content: flex-end; }
.msg-a { display: flex; align-items: flex-start; gap: 0.6rem; }
.a-icon { width: 24px; height: 24px; background: #1a1a1a; border: 1px solid #242424; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; flex-shrink: 0; margin-top: 3px; }
.bub-u  { background: #e8e8e8; color: #111; padding: 0.6rem 1rem; border-radius: 16px 16px 3px 16px; max-width: 55%; font-size: 0.83rem; line-height: 1.6; }
.bub-a  { background: #161616; border: 1px solid #1e1e1e; color: #bbb; padding: 0.6rem 1rem; border-radius: 3px 16px 16px 16px; max-width: 65%; font-size: 0.83rem; line-height: 1.6; }

/* LEAD CARD */
.lead-card { background: #111; border: 1px solid #1e1e1e; border-radius: 10px; padding: 1rem 1.2rem; max-width: 65%; }
.lc-top  { font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.12em; color: #4ade80; font-weight: 600; margin-bottom: 0.75rem; }
.lc-row  { display: flex; justify-content: space-between; padding: 0.35rem 0; border-bottom: 1px solid #1a1a1a; font-size: 0.78rem; }
.lc-row:last-child { border-bottom: none; }
.lc-k { color: #444; }
.lc-v { color: #ccc; font-weight: 500; }

/* INPUT */
[data-testid="stChatInputContainer"] {
    position: fixed !important;
    bottom: 0 !important; left: 220px !important; right: 0 !important;
    height: 64px !important;
    background: #0e0e0e !important;
    border-top: 1px solid #1c1c1c !important;
    padding: 0.7rem 4rem !important;
    z-index: 99 !important;
    width: calc(100vw - 220px) !important;
}
[data-testid="stChatInput"] > div {
    background: #161616 !important;
    border: 1px solid #242424 !important;
    border-radius: 8px !important;
    width: 100% !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #e0e0e0 !important;
    caret-color: #e0e0e0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #333 !important; }
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
    iv = '<div class="iv-greet">👋 Greeting</div>'
elif intent == "product_inquiry":
    iv = '<div class="iv-inquiry">🔍 Product inquiry</div>'
elif intent == "high_intent":
    iv = '<div class="iv-hot">🔥 High intent</div>'
else:
    iv = '<div class="iv-wait">Waiting…</div>'

# ── Left nav ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="nav">
  <div>
    <div class="nav-brand">AutoStream</div>
    <div class="nav-brand-sub">Inflx · ServiceHive</div>
  </div>
  <hr class="nav-sep">
  <div>
    <div class="nav-lbl">Pricing</div>
    <div class="nav-plan"><span class="nav-plan-n">Basic</span><span class="nav-plan-p">$29/mo</span></div>
    <div class="nav-plan"><span class="nav-plan-n">Pro</span><span class="nav-plan-p">$79/mo</span></div>
  </div>
  <div>
    <div class="nav-lbl">Pro includes</div>
    <div class="nav-feat">∞ Unlimited videos</div>
    <div class="nav-feat">▲ 4K resolution</div>
    <div class="nav-feat">✦ AI auto-captions</div>
    <div class="nav-feat">◎ 24/7 support</div>
  </div>
  <div>
    <div class="nav-lbl">Policy</div>
    <div class="nav-note">No refunds after 7 days of purchase.</div>
  </div>
  <div class="nav-intent">
    <div class="nav-int-lbl">Intent signal</div>
    {iv}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Topbar ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div>
    <div class="tb-name">AutoStream Assistant</div>
    <div class="tb-role">Lead qualification · Inflx by ServiceHive</div>
  </div>
  <div class="tb-right">
    <div class="tb-online"><div class="tb-dot"></div>Online</div>
    <div class="tb-nim">NVIDIA NIM</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Messages ──────────────────────────────────────────────────────────────
st.markdown('<div class="msgs">', unsafe_allow_html=True)

if not st.session_state.chat_history:
    st.markdown("""
    <div class="welcome">
      <div class="w-hi">Hi there —<br><b>how can I help you?</b></div>
      <div class="w-sub">Ask about pricing, features, or get started.</div>
      <div class="chips">
        <div class="chip">What plans do you offer?</div>
        <div class="chip">Tell me about Pro</div>
        <div class="chip">I want to sign up</div>
        <div class="chip">Refund policy</div>
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
              <div class="a-icon">✦</div>
              <div class="lead-card">
                <div class="lc-top">✓ Lead captured</div>
                <div class="lc-row"><span class="lc-k">Name</span><span class="lc-v">{s.get("lead_name","")}</span></div>
                <div class="lc-row"><span class="lc-k">Email</span><span class="lc-v">{s.get("lead_email","")}</span></div>
                <div class="lc-row"><span class="lc-k">Platform</span><span class="lc-v">{s.get("lead_platform","")}</span></div>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            content = entry["content"].replace("\n", "<br>")
            st.markdown(f"""
            <div class="msg-a">
              <div class="a-icon">✦</div>
              <div class="bub-a">{content}</div>
            </div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Chat input ────────────────────────────────────────────────────────────
if not lead_captured:
    user_input = st.chat_input("Ask me anything…")
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
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("↺ New conversation", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.agent_state = {
                "messages": [], "intent": "", "lead_name": "",
                "lead_email": "", "lead_platform": "",
                "lead_captured": False, "awaiting": ""
            }
            st.session_state.thread_id = f"inflx-{int(time.time())}"
            st.rerun()
