"""MCP × LangGraph — load an MCP server's tools into a LangGraph agent.

This ties MCP back to the stack you already know. An MCP server exposes tools in
a language-agnostic way; `langchain-mcp-adapters` wraps each MCP tool as a normal
LangChain tool, so a LangGraph agent can call them just like any other tool.

What it shows:
  1. MultiServerMCPClient points at the stdio Kestrel server (kestrel_mcp_server.py).
  2. .get_tools() launches that server and returns its tools as LangChain tools.
  3. create_react_agent builds a LangGraph ReAct agent over those tools + a model.

The adapter API is async, so everything runs inside asyncio.run(main()).

How to run:
    python langgraph_mcp_client.py
It needs the MCP server reachable — here that just means kestrel_mcp_server.py
exists next to this file (the adapter spawns it as a subprocess automatically).

Model access is optional and graceful:
  * Set OPENROUTER_API_KEY to actually ask a question end-to-end (uses OpenRouter's
    OpenAI-compatible endpoint via ChatOpenAI).
  * With no key, it still loads the MCP tools and prints their names, so the
    MCP-to-LangGraph wiring is demonstrated fully offline.

Requirements: pip install langchain-mcp-adapters langchain langgraph langchain-openai
"""

import asyncio
import os
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# Point the adapter at the stdio Kestrel server sitting next to this file.
SERVER_PATH = Path(__file__).resolve().parent / "kestrel_mcp_server.py"

MCP_SERVERS = {
    "kestrel": {
        "transport": "stdio",
        "command": "python",
        "args": [str(SERVER_PATH)],
    }
    # To target the REMOTE server instead, swap the block above for:
    #   {"transport": "streamable_http", "url": "http://127.0.0.1:8000/mcp"}
    # (start kestrel_http_server.py first).
}


def build_model():
    """Return a ChatOpenAI bound to OpenRouter, or None if no key is set."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return None
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model="openai/gpt-4o-mini",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
    )


async def main() -> None:
    # 1. Connect and pull the MCP tools as LangChain tools.
    client = MultiServerMCPClient(MCP_SERVERS)
    tools = await client.get_tools()
    print(f"Loaded {len(tools)} MCP tool(s): {[t.name for t in tools]}")

    # 2. Need a model to actually reason/act. Degrade gracefully if there isn't one.
    model = build_model()
    if model is None:
        print("\nOPENROUTER_API_KEY not set — skipping the live agent run.")
        print("The MCP tools above are already wired and ready for a LangGraph agent.")
        return

    # 3. Build a LangGraph ReAct agent over the MCP tools and ask a Kestrel question.
    agent = create_react_agent(model, tools)
    question = "What's the warranty on SKU KH-AR-GLD, and is there a restocking fee 60 days after delivery?"
    print(f"\nAsking: {question}")
    try:
        result = await agent.ainvoke({"messages": [("user", question)]})
        print("\nAgent answer:\n" + result["messages"][-1].content)
    except Exception as exc:  # never hard-crash the demo on a bad key / network
        print(f"\nAgent run failed ({type(exc).__name__}): {exc}")
        print("The MCP wiring still worked — the tools loaded fine above.")


if __name__ == "__main__":
    asyncio.run(main())
