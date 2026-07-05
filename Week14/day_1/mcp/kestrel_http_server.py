"""Kestrel Home — the SAME MCP server, but served over a REMOTE transport.

The bonus stdio server (kestrel_mcp_server.py) runs as a subprocess on the same
machine as the client: the client speaks to it over stdin/stdout. That is great
for local tools, but it can't be shared over a network.

STREAMABLE HTTP is MCP's remote transport. Instead of a subprocess, the server
is a normal web service listening on a single HTTP endpoint (here:
    http://127.0.0.1:8000/mcp
). Every MCP message — tool calls, resource reads, prompts — flows through that
one URL (streaming responses are delivered inline). It REPLACED the older
two-endpoint SSE transport, which was deprecated and removed from the spec in
November 2025. So today "remote MCP server" effectively means Streamable HTTP.

How a client / Claude connects to a remote server:
  * Claude Desktop / Claude Code: point at the URL instead of a command, e.g.
        { "mcpServers": { "kestrel-http": { "url": "http://127.0.0.1:8000/mcp" } } }
    (Real deployments front this with HTTPS + OAuth; localhost is fine for demos.)
  * Any MCP client library connects with a "streamable_http" connection to the URL.
  * langchain-mcp-adapters: MultiServerMCPClient({"kestrel": {"transport":
    "streamable_http", "url": "http://127.0.0.1:8000/mcp"}}).

Requirements:
    Python 3.10+  and   pip install "mcp[cli]"

Run it directly (Streamable HTTP transport; serves on 127.0.0.1:8000/mcp):
    python kestrel_http_server.py
Then leave it running and connect a client to the URL above (Ctrl-C to stop).
"""

from pathlib import Path
from mcp.server.fastmcp import FastMCP

# The FAQ lives one directory up, in docs/. Read it lazily for the Resource.
FAQ_PATH = Path(__file__).resolve().parent.parent / "docs" / "kestrel_home_faq.md"

# Warranty facts pulled from the FAQ. All Kestrel devices carry a 26-month warranty.
WARRANTIES = {
    "KH-N7-BLK": "Kestrel Nest-7 (Black) — 26-month warranty, indoor use only.",
    "KH-N7-WHT": "Kestrel Nest-7 (White) — 26-month warranty, indoor use only.",
    "KH-N7P-SLV": "Kestrel Nest-7 Pro (Silver) — 26-month warranty, indoor use only.",
    "KH-AR-GLD": "Kestrel Aria (Gold) — 26-month warranty, indoor use only.",
}

# host/port/streamable_http_path are FastMCP settings; the default path is "/mcp".
# We set host/port explicitly so the served URL is obvious: http://127.0.0.1:8000/mcp
mcp = FastMCP("kestrel-http", host="127.0.0.1", port=8000)


@mcp.tool()
def lookup_warranty(sku: str) -> str:
    """Return the warranty status for a Kestrel Home product SKU."""
    return WARRANTIES.get(sku.upper().strip(), f"Unknown SKU '{sku}'. Open a Tier 2 ticket to confirm.")


@mcp.tool()
def check_restocking_fee(days_since_delivery: int) -> str:
    """Compute the return/restocking outcome given days since delivery (45-day / 12% policy)."""
    if days_since_delivery <= 45:
        return "Within the 45-day window: full refund, no restocking fee (resalable condition + original packaging)."
    return ("Outside 45 days but within the 26-month warranty: 12% restocking fee applies to opened returns "
            "— WAIVED entirely if the return reason is a confirmed hardware defect.")


@mcp.resource("kestrel://faq")
def faq() -> str:
    """The full Kestrel Home internal support & product FAQ (read-only context)."""
    return FAQ_PATH.read_text(encoding="utf-8")


@mcp.prompt()
def support_reply(question: str) -> str:
    """Kestrel Home house reply template for a customer support question."""
    return (
        "Draft a Kestrel Home support reply to the customer question below. Use exactly this format:\n"
        "  Greeting -> Answer -> Policy (cite the rule) -> Next step -> sign off with '— Kestrel Home Support'.\n"
        "Escalate: >72h unresolved -> Tier 2; any fire/smoke/burning/sparking -> immediate Tier 3.\n\n"
        f"Customer question: {question}"
    )


if __name__ == "__main__":
    # The one line that makes this a REMOTE server instead of a local subprocess.
    mcp.run(transport="streamable-http")
