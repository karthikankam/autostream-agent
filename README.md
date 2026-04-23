# AutoStream AI Agent
### Social-to-Lead Agentic Workflow | ServiceHive ML Intern Assignment

A conversational AI agent that qualifies leads from social media conversations using **LangGraph**, **RAG**, and **Claude 3 Haiku**.

---

## Demo Flow

```
User  → "Hi, tell me about your pricing"
Agent → [RAG] Retrieves pricing from knowledge base → responds accurately

User  → "I want to try the Pro plan for my YouTube channel"
Agent → [Intent: HIGH] Detects buying intent → starts lead collection

Agent → "What's your full name?"
User  → "Sarah"

Agent → "What's your email?"
User  → "sarah@gmail.com"

Agent → "Which creator platform do you use?"
User  → "YouTube"

Agent → ✅ Calls mock_lead_capture("Sarah", "sarah@gmail.com", "YouTube")
```

---

## How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/your-username/autostream-agent.git
cd autostream-agent
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set your API key
Get a free API key from [build.nvidia.com](https://build.nvidia.com) → Sign in → Get API Key

```bash
# Mac/Linux
export NVIDIA_API_KEY=your_key_here

# Windows (PowerShell)
$env:NVIDIA_API_KEY="your_key_here"
```

### 5. Run the agent

**With chat UI (recommended):**
```bash
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

**Terminal only:**
```bash
python agent.py
```

---

## Architecture Explanation (~200 words)

### Why LangGraph?

LangGraph was chosen over plain LangChain because this agent requires **stateful, multi-turn conversation** with **conditional branching** — things that LangChain chains alone don't handle cleanly. LangGraph models the agent as a directed graph where each node is a logical step (classify → route → answer/collect), making the control flow explicit and debuggable.

### How State is Managed

LangGraph uses a `TypedDict` called `AgentState` as the shared memory across all nodes. Every user turn, the graph passes the full state to each node, which reads from it and returns only the fields it wants to update. Persistent memory across turns is handled by `MemorySaver` (a RAM-based checkpointer). Each conversation is identified by a `thread_id`, ensuring separate sessions don't mix state. Fields like `awaiting`, `lead_name`, `lead_email`, and `lead_platform` act as a mini state machine that tracks lead collection progress across multiple turns — ensuring the tool is never triggered prematurely.

### Flow Summary

```
classify_intent → [conditional edge] → greet_user    (casual)
                                     → rag_answerer  (product inquiry)
                                     → lead_collector (high intent)
```

---

## WhatsApp Deployment via Webhooks

To deploy this agent on WhatsApp:

### Step 1 — WhatsApp Business API Setup
- Register on Meta for Developers and create a WhatsApp Business App
- Get a `PHONE_NUMBER_ID` and `ACCESS_TOKEN`

### Step 2 — Build a Webhook Server (FastAPI example)
```python
from fastapi import FastAPI, Request
from agent import build_agent
from langchain_core.messages import HumanMessage

app = FastAPI()
agent = build_agent()

@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    body = await request.json()
    
    # Extract message from WhatsApp payload
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    user_id = message["from"]           # WhatsApp phone number (unique per user)
    user_text = message["text"]["body"]
    
    # Use phone number as thread_id → each user gets their own memory
    config = {"configurable": {"thread_id": user_id}}
    
    state = {"messages": [HumanMessage(content=user_text)], ...}
    result = agent.invoke(state, config=config)
    
    # Send response back via WhatsApp API
    send_whatsapp_message(user_id, result["messages"][-1].content)
    return {"status": "ok"}
```

### Step 3 — Expose via ngrok (for testing)
```bash
ngrok http 8000
# Use the ngrok URL as your webhook in Meta developer console
```

### Step 4 — Verify Webhook
Meta sends a verification GET request with a `hub.challenge` token — your server must return it to activate the webhook.

### Key Insight
The `thread_id = user_id` (phone number) pattern means every WhatsApp user automatically gets their own isolated conversation memory. No session management code needed — LangGraph handles it.

---

## Project Structure

```
autostream-agent/
├── agent.py              # LangGraph agent — nodes, graph, runner
├── tools.py              # mock_lead_capture function
├── knowledge_base.md     # RAG data — pricing and policies
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## Tech Stack

| Component | Choice |
|---|---|
| Language | Python 3.10+ |
| Agent Framework | LangGraph 0.4 |
| LLM | Gemini 1.5 Flash (Google) |
| Memory | LangGraph MemorySaver |
| RAG | Context injection (local Markdown) |
| Lead Tool | Python function |

---

## Evaluation Checklist

- ✅ Intent classification (3 categories)
- ✅ RAG from local knowledge base
- ✅ Multi-turn state management (5–6 turns)
- ✅ Lead collection (name, email, platform)
- ✅ Tool execution only after all data collected
- ✅ WhatsApp deployment explanation
## check the app at https://autostream-agent-5scorh8a7bzkw5hztmnez7.streamlit.app/
