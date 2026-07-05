"""Kestrel Home — a tiny MCP server demonstrating all 3 primitives.

This is the BONUS "build your own in ~30 lines" example. It exposes two Tools
(model-invoked actions), one Resource (read-only context), and one Prompt
(a user-invoked template), all built on the official MCP Python SDK's FastMCP.

Requirements:
    Python 3.10+  and   pip install "mcp[cli]"

Run it directly (stdio transport, the default):
    python kestrel_mcp_server.py

Register it in Claude Code (project-scoped) via a .mcp.json next to this file:
    { "mcpServers": { "kestrel": { "command": "python",
                                   "args": ["kestrel_mcp_server.py"] } } }

Register it in Claude Desktop by adding the same "kestrel" block to
    ~/Library/Application Support/Claude/claude_desktop_config.json   (macOS)
    %APPDATA%\\Claude\\claude_desktop_config.json                      (Windows)
then fully restart Claude Desktop.
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

mcp = FastMCP("kestrel-home")


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
    mcp.run()
