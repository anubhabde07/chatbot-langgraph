# LangGraph ChatBot

A modular, production-ready AI chatbot built with **LangGraph** and **LangChain**, featuring multiple backend configurations — from basic tool use to RAG, MCP integration, and human-in-the-loop workflows. A Streamlit frontend provides a polished chat UI with conversation history.

---

## Features

- Multi-turn conversation with persistent memory (SQLite checkpointing)
- Tool-augmented responses: web search, calculator, stock price lookup
- RAG (Retrieval-Augmented Generation) with per-thread PDF upload and FAISS indexing
- MCP (Model Context Protocol) support for external tool servers
- Human-in-the-loop (HITL) approval before the model responds
- Async graph execution for non-blocking I/O
- Subgraph composition (e.g., answer in English, translate to Hindi)
- Streamlit UI with chat history, thread management, and streaming responses

---

## Project Structure

```
.
├── main.py                          # FastMCP math server (add, sub, mul, div, mod, sqrt, power)
├── backend_tools.py                 # Basic LangGraph graph with tools (no persistence)
├── chatbot_async.py                 # Async graph with Calculator tool
├── chatbot_mcp.py                   # Async graph wired to a local MCP server
├── hitl.py                          # Human-in-the-loop approval flow
├── subgraph.py                      # Parent/subgraph: answer in English + translate to Hindi
├── rag.py                           # Standalone RAG pipeline over a local PDF
│
├── langgraph_database_backend.py    # Persistent chatbot with SQLite checkpointer
├── langgraph_tool_backend.py        # Persistent chatbot with tools + SQLite
├── langgraph_rag_backend.py         # Persistent RAG chatbot with tools + SQLite
├── langgraph_mcp_backend.py         # Async persistent chatbot with MCP + tools
│
├── streamlit_frontend_database.py   # Streamlit UI for database backend
├── streamlit_frontend_mcp.py        # Streamlit UI for MCP backend
├── streamlit_rag_frontend.py        # Streamlit UI for RAG backend
│
├── chatbot.db                       # SQLite database (auto-created)
└── requirements.txt
```

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd <repo-folder>
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
ALPHAVANTAGE_API_KEY=your_alpha_vantage_key   # optional, for stock prices
GITHUB_TOKEN=your_github_token                # optional, for GitHub PR tool
```

---

## Running the App

### Streamlit UI (recommended)

Pick the backend that matches your use case:

```bash
# Basic chatbot with tool use and conversation history
streamlit run streamlit_frontend_database.py

# Chatbot with MCP server tools
streamlit run streamlit_frontend_mcp.py

# RAG chatbot with PDF upload
streamlit run streamlit_rag_frontend.py
```

### Backend scripts (standalone)

```bash
# Run the async chatbot directly
python chatbot_async.py

# Run the MCP chatbot (requires main.py MCP server)
python chatbot_mcp.py

# Run the subgraph (English answer + Hindi translation)
python subgraph.py

# Run the HITL approval flow
python hitl.py
```

### MCP Math Server

The `main.py` file is a standalone FastMCP server that exposes arithmetic tools over stdio. It is launched automatically by `chatbot_mcp.py` and `langgraph_mcp_backend.py` — no manual startup required.

To run it independently:

```bash
python main.py
```

---

## Backend Overview

### `langgraph_database_backend.py`
Simple persistent chatbot. No tools. Uses `SqliteSaver` for thread-level memory.

### `langgraph_tool_backend.py`
Extends the database backend with DuckDuckGo web search, a Calculator tool, and stock price lookup via Alpha Vantage.

### `langgraph_rag_backend.py`
Full RAG pipeline. Upload a PDF per chat thread; the backend chunks it, embeds it with OpenAI embeddings, and stores it in a FAISS index. The `rag_tool` retrieves relevant context at query time. Also includes web search, calculator, and stock price tools.

### `langgraph_mcp_backend.py`
Async backend that connects to external MCP servers (local stdio and remote HTTP) using `langchain-mcp-adapters`. Runs on a dedicated event loop to stay compatible with Streamlit's synchronous execution model.

### `hitl.py`
Demonstrates LangGraph's interrupt/resume pattern. The graph pauses before the LLM responds and waits for a human approval signal (`yes`/`no`) before continuing.

### `subgraph.py`
Shows parent/subgraph composition. A parent graph generates an English answer, then delegates to a subgraph that translates it to Hindi using GPT-4o.

---

## Tools

| Tool | Description |
|---|---|
| `DuckDuckGoSearchRun` | Live web search |
| `Calculator` | Basic arithmetic (add, sub, mul, div) |
| `get_stock_price` | Latest stock quote via Alpha Vantage |
| `rag_tool` | Semantic search over uploaded PDF (per thread) |
| MCP tools | Arithmetic server: add, subtract, multiply, divide, modulus, power, sqrt |

The `codes.txt` file contains a ready-to-use `list_github_prs` tool that fetches open/closed pull requests from any GitHub repository.

---

## Tech Stack

| Component | Library |
|---|---|
| Graph orchestration | `langgraph` |
| LLM | `langchain-openai` (GPT-4o-mini / GPT-4o) |
| Web search | `langchain-community` (DuckDuckGo) |
| Embeddings | `langchain-openai` (text-embedding-3-small) |
| Vector store | `faiss-cpu` |
| PDF loading | `pypdf`, `langchain-community` |
| MCP client | `langchain-mcp-adapters` |
| Persistence | `langgraph-checkpoint-sqlite`, `aiosqlite` |
| Frontend | `streamlit` |
| Env management | `python-dotenv` |

---

## Notes

- The SQLite database (`chatbot.db`) is created automatically on first run. Thread IDs are UUIDs displayed in the sidebar.
- RAG retrievers are stored in-memory per thread; restarting the server clears them. Re-upload PDFs after a restart.
- The MCP backend spins up a background asyncio event loop to bridge async graph execution with Streamlit's sync model.
- HITL interrupts require `MemorySaver` (in-memory checkpointer) — not SQLite — because interrupt state must survive across two `invoke` calls within the same process.
