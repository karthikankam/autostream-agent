import os
import operator
from typing import TypedDict, Annotated, Literal

import streamlit as st
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    intent: str
    lead_name: str
    lead_email: str
    lead_platform: str
    lead_captured: bool
    awaiting: str


# ----------------------------
# Knowledge Base
# ----------------------------
def load_knowledge_base() -> str:
    kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.md")
    with open(kb_path, "r") as f:
        return f.read()


KNOWLEDGE_BASE = load_knowledge_base()


# ----------------------------
# LLM Setup (LOCAL + DEPLOY SAFE)
# ----------------------------
def get_llm():
    api_key = os.getenv("NVIDIA_API_KEY") or st.secrets.get("NVIDIA_API_KEY")

    if not api_key:
        raise ValueError("NVIDIA_API_KEY not set in .env or Streamlit secrets.")

    return ChatNVIDIA(
        model="meta/llama-3.1-8b-instruct",
        api_key=api_key,
        temperature=0.3
    )


# ----------------------------
# Intent Classifier
# ----------------------------
def classify_intent(state: AgentState) -> dict:
    llm = get_llm()
    latest_message = state["messages"][-1].content

    if state.get("awaiting"):
        return {"intent": "high_intent"}

    prompt = f"""
You are an intent classifier for AutoStream SaaS.

Classify into:
- casual_greeting
- product_inquiry
- high_intent

Message: "{latest_message}"

Return ONLY the label.
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    intent = response.content.strip().lower()

    if intent not in ["casual_greeting", "product_inquiry", "high_intent"]:
        intent = "product_inquiry"

    return {"intent": intent}


# ----------------------------
# Router
# ----------------------------
def route_by_intent(state: AgentState) -> Literal["greet_user", "rag_answerer", "lead_collector"]:
    if state.get("awaiting") or state.get("intent") == "high_intent":
        return "lead_collector"

    if state.get("intent") == "casual_greeting":
        return "greet_user"
    elif state.get("intent") == "high_intent":
        return "lead_collector"
    else:
        return "rag_answerer"


# ----------------------------
# Greeting Node
# ----------------------------
def greet_user(state: AgentState) -> dict:
    llm = get_llm()

    system = """
You are a friendly assistant for AutoStream SaaS.
Keep responses short and helpful.
"""

    response = llm.invoke([
        SystemMessage(content=system),
        *state["messages"]
    ])

    return {"messages": [AIMessage(content=response.content)]}


# ----------------------------
# RAG Node
# ----------------------------
def rag_answerer(state: AgentState) -> dict:
    llm = get_llm()

    system = f"""
Use ONLY this knowledge base:

{KNOWLEDGE_BASE}

If missing info, say you don't know.
"""

    response = llm.invoke([
        SystemMessage(content=system),
        *state["messages"]
    ])

    return {"messages": [AIMessage(content=response.content)]}


# ----------------------------
# Lead Collector
# ----------------------------
def lead_collector(state: AgentState) -> dict:
    from tools import mock_lead_capture

    latest_message = state["messages"][-1].content
    updates = {}
    awaiting = state.get("awaiting", "")

    if awaiting == "name":
        updates["lead_name"] = latest_message
    elif awaiting == "email":
        updates["lead_email"] = latest_message
    elif awaiting == "platform":
        updates["lead_platform"] = latest_message

    name = updates.get("lead_name") or state.get("lead_name")
    email = updates.get("lead_email") or state.get("lead_email")
    platform = updates.get("lead_platform") or state.get("lead_platform")

    if name and email and platform:
        result = mock_lead_capture(name, email, platform)

        return {
            "lead_captured": True,
            "awaiting": "",
            "messages": [AIMessage(content=f"""
🎉 You're all set!

{result}

Name: {name}
Email: {email}
Platform: {platform}
""")]
        }

    if not name:
        return {"awaiting": "name", "messages": [AIMessage("What is your full name?")]}
    elif not email:
        return {"awaiting": "email", "messages": [AIMessage(f"Thanks {name}! Your email?")]}
    else:
        return {"awaiting": "platform", "messages": [AIMessage("Which platform do you use?")]}


# ----------------------------
# Build Graph
# ----------------------------
def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("classify_intent", classify_intent)
    graph.add_node("greet_user", greet_user)
    graph.add_node("rag_answerer", rag_answerer)
    graph.add_node("lead_collector", lead_collector)

    graph.set_entry_point("classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "greet_user": "greet_user",
            "rag_answerer": "rag_answerer",
            "lead_collector": "lead_collector",
        }
    )

    graph.add_edge("greet_user", END)
    graph.add_edge("rag_answerer", END)
    graph.add_edge("lead_collector", END)

    return graph.compile(checkpointer=MemorySaver())


# ----------------------------
# Streamlit UI
# ----------------------------
def main():
    st.title("🎬 AutoStream AI Assistant")

    agent = build_agent()
    config = {"configurable": {"thread_id": "session-1"}}

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

    user_input = st.text_input("You:")

    if user_input:
        st.session_state.state["messages"] = [HumanMessage(content=user_input)]

        result = agent.invoke(st.session_state.state, config=config)

        messages = result.get("messages", [])
        if messages:
            st.write("**Agent:**", messages[-1].content)

        st.session_state.state = result


# ----------------------------
# Run App
# ----------------------------
if __name__ == "__main__":
    main()