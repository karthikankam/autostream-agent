import os
import time
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from agent import build_agent

st.set_page_config(page_title="AutoStream Agent", page_icon="🎬", layout="centered")

# ── Session state ─────────────────────────────────────────────────────────
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

# ── Header ────────────────────────────────────────────────────────────────
st.title("🎬 AutoStream Agent")
st.caption("Social-to-Lead Agentic Workflow · Powered by Inflx · ServiceHive")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📋 AutoStream Info")

    st.subheader("💰 Pricing")
    st.markdown("- **Basic** — $29/mo · 10 videos · 720p")
    st.markdown("- **Pro** — $79/mo · Unlimited · 4K · AI captions")

    st.subheader("✨ Pro Includes")
    st.markdown("- ♾️ Unlimited videos/month")
    st.markdown("- 🎥 4K resolution export")
    st.markdown("- 📝 AI auto-captions")
    st.markdown("- 🛟 24/7 priority support")

    st.subheader("📋 Policy")
    st.warning("No refunds after 7 days of purchase.")

    st.divider()
    st.subheader("📡 Intent Signal")
    intent = st.session_state.agent_state.get("intent", "")
    if intent == "casual_greeting":
        st.success("👋 Greeting")
    elif intent == "product_inquiry":
        st.info("🔍 Product inquiry")
    elif intent == "high_intent":
        st.error("🔥 High intent — ready to sign up!")
    else:
        st.caption("Waiting for first message…")

    if st.session_state.agent_state.get("lead_captured"):
        st.divider()
        st.subheader("✅ Lead Captured")
        s = st.session_state.agent_state
        st.markdown(f"**Name:** {s.get('lead_name', '')}")
        st.markdown(f"**Email:** {s.get('lead_email', '')}")
        st.markdown(f"**Platform:** {s.get('lead_platform', '')}")

# ── Chat messages ─────────────────────────────────────────────────────────
for entry in st.session_state.chat_history:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])

# ── Chat input ────────────────────────────────────────────────────────────
lead_captured = st.session_state.agent_state.get("lead_captured", False)

if not lead_captured:
    user_input = st.chat_input("Ask me anything about AutoStream…")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        current_state = st.session_state.agent_state.copy()
        current_state["messages"] = [HumanMessage(content=user_input)]
        config = {"configurable": {"thread_id": st.session_state.thread_id}}

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                result = st.session_state.agent.invoke(current_state, config=config)

            ai_msgs = [m for m in result["messages"] if isinstance(m, AIMessage)]
            if ai_msgs:
                response = ai_msgs[-1].content
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

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
    st.success("🎉 Lead captured successfully! Check the sidebar for details.")
    if st.button("↺ Start new conversation"):
        st.session_state.chat_history = []
        st.session_state.agent_state = {
            "messages": [], "intent": "", "lead_name": "",
            "lead_email": "", "lead_platform": "",
            "lead_captured": False, "awaiting": ""
        }
        st.session_state.thread_id = f"inflx-{int(time.time())}"
        st.rerun()
