import os
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import operator


class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    intent: str
    lead_name: str
    lead_email: str
    lead_platform: str
    lead_captured: bool
    awaiting: str


def load_knowledge_base() -> str:
    kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.md")
    with open(kb_path, "r") as f:
        return f.read()

KNOWLEDGE_BASE = load_knowledge_base()


def get_llm():
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY environment variable not set.")
    return ChatNVIDIA(model="meta/llama-3.1-8b-instruct", api_key=api_key, temperature=0.3)


def classify_intent(state: AgentState) -> dict:
    llm = get_llm()
    latest_message = state["messages"][-1].content

    if state.get("awaiting"):
        return {"intent": "high_intent"}

    classification_prompt = f"""You are an intent classifier for AutoStream, a video editing SaaS.

Classify the user message into EXACTLY ONE of these intents:
- casual_greeting: Simple greetings, hi, hello, how are you, thanks, bye
- product_inquiry: Questions about pricing, features, plans, refunds, support
- high_intent: User clearly wants to sign up, try, buy, start, subscribe, get access

User message: "{latest_message}"

Reply with ONLY the intent label, nothing else."""

    response = llm.invoke([HumanMessage(content=classification_prompt)])
    intent = response.content.strip().lower()

    valid_intents = ["casual_greeting", "product_inquiry", "high_intent"]
    if intent not in valid_intents:
        intent = "product_inquiry"

    print(f"[Intent]: {intent}")
    return {"intent": intent}


def route_by_intent(state: AgentState) -> Literal["greet_user", "rag_answerer", "lead_collector"]:
    if state.get("awaiting") or state.get("intent") == "high_intent":
        return "lead_collector"

    intent = state.get("intent", "product_inquiry")

    if intent == "casual_greeting":
        return "greet_user"
    elif intent == "high_intent":
        return "lead_collector"
    else:
        return "rag_answerer"


def greet_user(state: AgentState) -> dict:
    llm = get_llm()

    system = """You are a friendly assistant for AutoStream, an AI-powered video editing SaaS for content creators.
Keep greetings warm, brief, and naturally mention you can help with pricing or getting started."""

    response = llm.invoke([
        SystemMessage(content=system),
        *state["messages"]
    ])

    return {"messages": [AIMessage(content=response.content)]}


def rag_answerer(state: AgentState) -> dict:
    llm = get_llm()

    system = f"""You are a helpful sales assistant for AutoStream, an AI-powered video editing SaaS.

Answer questions ONLY using the information in the knowledge base below.
If something is not in the knowledge base, say you don't have that information.
Be concise, friendly, and helpful. If the user seems interested, gently mention they can sign up.

=== KNOWLEDGE BASE ===
{KNOWLEDGE_BASE}
======================"""

    response = llm.invoke([
        SystemMessage(content=system),
        *state["messages"]
    ])

    return {"messages": [AIMessage(content=response.content)]}


def lead_collector(state: AgentState) -> dict:
    from tools import mock_lead_capture

    latest_message = state["messages"][-1].content
    updates = {}
    awaiting = state.get("awaiting", "")

    if awaiting == "name":
        updates["lead_name"] = latest_message.strip()
    elif awaiting == "email":
        updates["lead_email"] = latest_message.strip()
    elif awaiting == "platform":
        updates["lead_platform"] = latest_message.strip()

    current_name = updates.get("lead_name") or state.get("lead_name")
    current_email = updates.get("lead_email") or state.get("lead_email")
    current_platform = updates.get("lead_platform") or state.get("lead_platform")

    if current_name and current_email and current_platform:
        result = mock_lead_capture(current_name, current_email, current_platform)

        response_message = f"""🎉 **You're all set!**

{result}

Here's a summary of what we captured:
- **Name:** {current_name}
- **Email:** {current_email}
- **Platform:** {current_platform}

Welcome to AutoStream! You'll love the Pro plan's 4K resolution and AI captions for your content. 🚀"""

        updates["lead_captured"] = True
        updates["awaiting"] = ""
        updates["messages"] = [AIMessage(content=response_message)]
        return updates

    if not current_name:
        response = "I'd love to get you set up with AutoStream! To get started, could you share your **full name**?"
        updates["awaiting"] = "name"
    elif not current_email:
        response = f"Thanks {current_name}! What's your **email address** so we can set up your account?"
        updates["awaiting"] = "email"
    elif not current_platform:
        response = "Almost there! Which **creator platform** do you mainly use? (e.g., YouTube, Instagram, TikTok)"
        updates["awaiting"] = "platform"

    updates["messages"] = [AIMessage(content=response)]
    return updates


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
            "lead_collector": "lead_collector"
        }
    )

    graph.add_edge("greet_user", END)
    graph.add_edge("rag_answerer", END)
    graph.add_edge("lead_collector", END)

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


def run_conversation():
    print("\n" + "="*60)
    print("  🎬 AutoStream AI Assistant")
    print("  Powered by LangGraph + Gemini 1.5 Flash")
    print("="*60)
    print("  Type 'quit' or 'exit' to end the conversation")
    print("="*60 + "\n")

    agent = build_agent()
    config = {"configurable": {"thread_id": "autostream-session-1"}}

    current_state = {
        "messages": [],
        "intent": "",
        "lead_name": "",
        "lead_email": "",
        "lead_platform": "",
        "lead_captured": False,
        "awaiting": ""
    }

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["quit", "exit", "bye"]:
            print("\nAgent: Thanks for chatting! Have a great day! 👋\n")
            break

        if not user_input:
            continue

        current_state["messages"] = [HumanMessage(content=user_input)]

        result = agent.invoke(current_state, config=config)

        ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
        if ai_messages:
            print(f"\nAgent: {ai_messages[-1].content}\n")

        current_state = {
            "messages": [],
            "intent": result.get("intent", ""),
            "lead_name": result.get("lead_name", ""),
            "lead_email": result.get("lead_email", ""),
            "lead_platform": result.get("lead_platform", ""),
            "lead_captured": result.get("lead_captured", False),
            "awaiting": result.get("awaiting", "")
        }

        if result.get("lead_captured"):
            print("="*60)
            print("  ✅ Lead capture complete! Session ended.")
            print("="*60 + "\n")
            break


if __name__ == "__main__":
    run_conversation()