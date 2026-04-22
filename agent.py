import os
from typing import TypedDict, Annotated, Literal
import operator

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA

import streamlit as st


# ───────────────────────── STATE ─────────────────────────
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    intent: str
    lead_name: str
    lead_email: str
    lead_platform: str
    lead_captured: bool
    awaiting: str


# ───────────────────────── LOAD LLM SAFELY ─────────────────────────
def get_llm():
    api_key = os.getenv("NVIDIA_API_KEY") or st.secrets.get("NVIDIA_API_KEY")

    if not api_key:
        raise ValueError("❌ NVIDIA_API_KEY missing (env or Streamlit secrets)")

    return ChatNVIDIA(
        model="meta/llama-3.1-8b-instruct",
        api_key=api_key,
        temperature=0.3
    )


# ───────────────────────── INTENT CLASSIFIER ─────────────────────────
def classify_intent(state: AgentState):
    llm = get_llm()

    msg = state["messages"][-1].content

    prompt = f"""
Classify:
- casual_greeting
- product_inquiry
- high_intent

Message: {msg}

Return only label.
"""

    res = llm.invoke([HumanMessage(content=prompt)])
    intent = res.content.strip().lower()

    if intent not in ["casual_greeting", "product_inquiry", "high_intent"]:
        intent = "product_inquiry"

    return {"intent": intent}


# ───────────────────────── ROUTER ─────────────────────────
def route(state: AgentState) -> Literal["greet", "rag", "lead"]:
    if state.get("intent") == "casual_greeting":
        return "greet"
    if state.get("intent") == "high_intent":
        return "lead"
    return "rag"


# ───────────────────────── NODES ─────────────────────────
def greet(state: AgentState):
    llm = get_llm()

    res = llm.invoke([
        SystemMessage(content="You are a friendly SaaS assistant."),
        *state["messages"]
    ])

    return {"messages": [AIMessage(content=res.content)]}


def rag(state: AgentState):
    llm = get_llm()

    res = llm.invoke([
        SystemMessage(content="Answer based on SaaS product knowledge."),
        *state["messages"]
    ])

    return {"messages": [AIMessage(content=res.content)]}


def lead(state: AgentState):
    msg = state["messages"][-1].content

    return {
        "messages": [AIMessage(content=f"Got it! We'll contact you about: {msg}")]
    }


# ───────────────────────── GRAPH ─────────────────────────
def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("classify", classify_intent)
    graph.add_node("greet", greet)
    graph.add_node("rag", rag)
    graph.add_node("lead", lead)

    graph.set_entry_point("classify")

    graph.add_conditional_edges(
        "classify",
        route,
        {
            "greet": "greet",
            "rag": "rag",
            "lead": "lead"
        }
    )

    graph.add_edge("greet", END)
    graph.add_edge("rag", END)
    graph.add_edge("lead", END)

    return graph.compile(checkpointer=MemorySaver())
