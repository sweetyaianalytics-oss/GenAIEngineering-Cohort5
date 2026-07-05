# MCP, Agent Skills & Fine-tuning — hands-on

Three ways to give a model more capability than a plain prompt — **MCP** (tools),
**Agent Skills** (packaged know-how), and **fine-tuning** (teaching voice) — learned by
running small, real demos. This is the **continuation of the LangChain/RAG session** and
keeps the same **Kestrel Home** smart-thermostat support theme, so every example builds on
a world you already know. Assumes you're comfortable with LangChain, `@tool`, and RAG.

A 3-hour session. Runs on **macOS, Linux, and Windows**.

## The one idea — the capability ladder

Every technique for making a model more useful is a **rung** on one ladder. You climb only
as high as the problem needs — a higher rung costs more effort and is easy to over-reach for.

```text
   rung 5   Fine-tune   ── bake a VOICE / FORMAT into the weights themselves
              ^
   rung 4   Skills      ── package reusable know-how the model loads on demand
              ^
   rung 3   Tools/MCP   ── let the model DO things: call functions, hit systems
              ^
   rung 2   RAG         ── ground answers in YOUR documents (last session)
              ^
   rung 1   Prompt      ── just ask; instructions + context in the message

   Last session covered rungs 1-2.  TODAY covers rungs 3-5.
   Rule: climb only as high as the problem needs.
```

- **Prompt** and **RAG** you already have from the LangChain session.
- **Tools/MCP** is rung 3 — the same `@tool` idea, standardized so *any* app can use it.
- **Skills** is rung 4 — a folder of instructions the model pulls in only when relevant.
- **Fine-tune** is rung 5 — changing the weights so the behavior is built in.

## What's in here

| Path | What it is |
|---|---|
| `mcp/` | The **MCP demo** — off-the-shelf filesystem/GitHub servers for Claude Desktop, plus **two** bonus Kestrel servers and a LangGraph client (see below). Full walkthrough in [`mcp/README.md`](./mcp/README.md). |
| `mcp/kestrel_mcp_server.py` | The bonus **~30-line stdio** Kestrel MCP server, exposing all 3 primitives (2 tools, 1 resource, 1 prompt). |
| `mcp/kestrel_http_server.py` | The **same** server over MCP's **remote transport** (Streamable HTTP) — serves `http://127.0.0.1:8000/mcp`. |
| `mcp/langgraph_mcp_client.py` | Loads the MCP server's tools into a **LangGraph** ReAct agent via `langchain-mcp-adapters` — ties MCP back to the LangChain stack. |
| `skills/kestrel-support/` | A **Skills demo** — a `SKILL.md` support playbook + on-demand `reference.md`, for any skills-aware client. |
| `skills/kestrel-triage/` | A second, **executable** skill — a `SKILL.md` that has Claude *run* `scripts/classify.py` to triage a ticket into a tier (fire/smoke → Tier 3, >72h → Tier 2, else Tier 1). |
| `finetune/` | The **fine-tuning demo** — an Unsloth/QLoRA Colab notebook + a 118-example Kestrel dataset. See [`finetune/README.md`](./finetune/README.md). |
| `finetune/build_dataset.py` | Generates a **synthetic** dataset (`kestrel_support_dataset.synthetic.jsonl`) — shows how to manufacture format-consistent training data at scale. |
| `finetune/check_format.py` | **Evaluation** — scores format adherence (the five-part house format) over a dataset or real model outputs; the curated set scores ~100%. |
| `finetune/kestrel_preference_dataset.jsonl` | 24 **DPO** chosen/rejected pairs for the notebook's preference-tuning section. |
| `docs/` | Shared source material: `kestrel_home_faq.md` (the support FAQ the MCP servers and RAG both read) and a swap doc. |
| `GLOSSARY.md` | Plain-English definitions (~49 terms) across MCP, Skills, and fine-tuning. |
| `EXERCISES.md` | 16 hands-on exercises to climb the ladder yourself, ordered easy → harder. |
| `lesson.html` | The offline slide deck for the session — open it in any browser. |
| `requirements.txt` | Local Python deps for the runnable scripts: `mcp[cli]` (both bonus servers) plus `langchain-mcp-adapters`, `langchain`, `langgraph`, `langchain-openai` (the LangGraph × MCP client). |

## Setup

**There is no single `pip install` for this repo.** The three demos have deliberately
different requirements — set up only the one you're running.

| Demo | What it needs | Local install? |
|---|---|---|
| **MCP** | **Node.js / `npx`** + **Claude Desktop** (for the official filesystem/GitHub servers). Bonus server also needs **Python 3.10+**. | Only the bonus server (`pip install -r requirements.txt`). |
| **Skills** | **Claude Code** or another skills-aware client. | None — just point it at the folder. |
| **Fine-tuning** | A browser. Runs in **Google Colab** (free T4 GPU) or **Unsloth Studio**. | **Nothing local.** |

### Python for the bonus MCP server only

The MCP demo itself runs official servers over `npx` (no Python). The **bonus**
`mcp/kestrel_mcp_server.py` is the only piece that needs a local Python env — **Python
3.10+**.

> **⚠️ Python version matters — the #1 install failure.** The `mcp` SDK needs **Python
> ≥ 3.10**. If your `python3` is older (e.g. **3.9**, the macOS default), the install fails
> with a `No matching distribution found` error — pip is silently filtering out the package
> for your Python, not a broken package. Fix: install 3.11 and build the venv with it
> **explicitly** (`python3.11` / `py -3.11`), e.g. `brew install python@3.11`, or just use
> `uv`, which fetches 3.11 for you.

Pick **one** option, then run the block for your OS. All commands run from the repo root.

**Option A — [`uv`](https://docs.astral.sh/uv/) (fast, cross-platform):**

```bash
# macOS / Linux
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

```powershell
# Windows (PowerShell)
uv venv --python 3.11 .venv
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

**Option B — plain `venv`:** use `python3.11` / `py -3.11` **explicitly** — plain `venv`
can't fetch a Python for you, so a bare `python3` that happens to be 3.9 produces a broken
venv.

```bash
# macOS / Linux
python3.11 -m venv .venv          # or: python3 -m venv .venv  (only if python3 is >= 3.10)
source .venv/bin/activate
python --version                  # confirm 3.10+ BEFORE installing
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

```powershell
# Windows (PowerShell)
py -3.11 -m venv .venv            # the -3.11 selects Python 3.11 explicitly
.venv\Scripts\Activate.ps1
python --version                  # confirm 3.10+
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> **Heads-up on `pip`:** a `uv venv` (Option A) does **not** seed `pip` — install with
> `uv pip install ...` inside it. `python -m venv` (Option B) does include pip.

## The three demos

### 1. MCP — let the model *do* things

**MCP (Model Context Protocol)** is the `@tool` idea from LangChain, *standardized* so any
MCP-aware app can use it — "USB-C for AI". Claude Desktop and Claude Code are themselves MCP
clients. Full walkthrough in [`mcp/README.md`](./mcp/README.md).

**Off-the-shelf servers (no code):** copy [`mcp/claude_desktop_config.example.json`](./mcp/claude_desktop_config.example.json)
into your Claude Desktop config, set a real folder path for **filesystem** and a token for
**github**, then fully restart Claude Desktop and ask in plain English:

- *"Summarize the open issues in this repo."* → Claude calls the **GitHub** MCP tools.
- *"Organize the files in this folder by type."* → Claude calls the **filesystem** MCP tools.

**Bonus — build your own in ~30 lines.** A tiny FastMCP server exposing all 3 primitives for
Kestrel Home:

```bash
python mcp/kestrel_mcp_server.py        # runs over stdio
```

Register it for **Claude Code** via the project-scoped [`mcp/.mcp.json`](./mcp/.mcp.json)
(picked up automatically), or add the same `"kestrel"` block to your Claude Desktop config.

> **What you'll see:** ask *"What's the warranty on SKU KH-AR-GLD?"* or *"A customer wants to
> return a thermostat 60 days after delivery — what's the fee?"* and Claude calls your server:
> **2 tools** (`lookup_warranty`, `check_restocking_fee`), **1 resource**
> (`kestrel://faq`, the FAQ served as context), and **1 prompt** (`support_reply`, the house
> reply template). Tools *do* things, resources *are* things, prompts are *canned starting
> points* a user picks.

**Bonus — the same server over a *remote* transport.** The stdio server runs as a local
subprocess; **Streamable HTTP** is MCP's remote transport — the identical server becomes a
web service on one URL:

```bash
python mcp/kestrel_http_server.py     # serves http://127.0.0.1:8000/mcp
```

Leave it running and point a client at the URL instead of a command (e.g. a Claude Desktop
`"url"` entry). Streamable HTTP replaced the older SSE transport, so today "remote MCP
server" effectively means this.

> **What you'll see:** the same **2 tools / 1 resource / 1 prompt**, but reached over HTTP
> rather than stdin/stdout — every MCP message flows through that single `/mcp` endpoint.
> Localhost is fine for the demo; real deployments front it with HTTPS + OAuth.

**Bonus — load MCP tools into a LangGraph agent.** This ties MCP back to the LangChain stack:
`langchain-mcp-adapters` wraps each MCP tool as a normal LangChain tool so a LangGraph ReAct
agent can call it.

```bash
python mcp/langgraph_mcp_client.py    # spawns the stdio server automatically
```

> **What you'll see:** with **no key**, it still connects, loads the MCP tools, and prints
> their names (`lookup_warranty`, `check_restocking_fee`) — the MCP → LangGraph wiring runs
> fully offline. Set `OPENROUTER_API_KEY` and it builds a Kestrel ReAct agent that actually
> answers a warranty + restocking question end-to-end by calling those tools.

### 2. Skills — package reusable know-how

An **Agent Skill** is a folder the model loads on demand. Drop
[`skills/kestrel-support/`](./skills/kestrel-support/) where your client loads skills (for
Claude Code, a `skills/` or `.claude/skills/` directory), then ask a Kestrel support question
— *"A customer says their Nest-7 is making a burning smell, what do I tell them?"* — and watch
the skill activate and reply in the house format (greeting → answer → policy → next step →
`— Kestrel Home Support`).

> **What you'll see: progressive disclosure.** Until the question is relevant, only
> `SKILL.md`'s **name + description** sit in context — cheap. When it matches, the full
> `SKILL.md` playbook loads; the heavier `reference.md` (SKU-by-SKU warranty, SLA, and
> restocking tables) loads **only when the reply actually needs it**. You get deep know-how
> without paying for it on every turn.

**Skills can run code, not just prose.** Drop [`skills/kestrel-triage/`](./skills/kestrel-triage/)
alongside the first skill. When a ticket arrives, this skill has Claude **execute** its
bundled classifier instead of eyeballing rules by hand:

```bash
python scripts/classify.py "<the full ticket text>"     # what the skill runs for you
```

> **What you'll see:** ask Claude to triage a ticket and it runs `scripts/classify.py`, which
> prints a JSON verdict — `tier`, `urgency`, `reason`, `route`. A *"there's a burning smell"*
> ticket → **Tier 3 / IMMEDIATE** (Safety Response); *"still no reply after 4 days"* → **Tier
> 2 / HIGH** (Marcus Webb, ext 4471); anything else → **Tier 1 / NORMAL**. Because the verdict
> comes from code, it's **deterministic and identical every time** — the payoff of a skill that
> bundles a script rather than re-deriving rules in prose each turn.

### 3. Fine-tuning — bake in the voice

Open [`finetune/kestrel_finetune_unsloth.ipynb`](./finetune/kestrel_finetune_unsloth.ipynb)
in **Google Colab** (set **Runtime → Change runtime type → T4 GPU**), upload
`finetune/kestrel_support_dataset.jsonl` (**118 examples**), then **Runtime → Run all** —
about **~10 minutes** on a free T4. Prefer no-code? Use **Unsloth Studio** (`unsloth studio`),
upload the dataset, click **Train**, and compare in **Model Arena**. Details in
[`finetune/README.md`](./finetune/README.md).

Swap the base model with a one-line change in `FastLanguageModel.from_pretrained(...)`:
`unsloth/Llama-3.2-1B-Instruct` (default) → `unsloth/gemma-4-E4B-it` (a step up) or
`unsloth/gemma-3-270m` (lightest, fastest for a live demo).

> **What you'll see:** *before*, the base model answers a Kestrel question generically —
> formatless, no greeting, no `Answer:` / `Policy:` / `Next step:` markers, no sign-off.
> *After* 118 examples, it reliably emits the exact Kestrel five-part format. The punchline:
> ask it about a **made-up product** whose price was never in the data — it replies in
> flawless Kestrel voice and gets the **price wrong**.

> **Fine-tuning teaches the VOICE / FORMAT, not the FACTS.** For facts, use **RAG** (last
> session). **Production = fine-tune for voice + RAG for facts.**

**Where the data comes from — "the data is 80% of the job."** The curated
`kestrel_support_dataset.jsonl` is hand-written, but `build_dataset.py` shows how to
*manufacture* a format-consistent set at scale (rotate greetings, stamp every reply through
one five-part template):

```bash
python finetune/build_dataset.py            # writes kestrel_support_dataset.synthetic.jsonl
```

> **What you'll see:** a separate `.synthetic.jsonl` of byte-for-byte consistent replies, plus
> a printed sample row. The notebook still trains on the curated set — hand-written variety
> teaches a more natural voice — so treat this as the *method*, not a replacement.

**Did it work? Measure it.** Fine-tuning taught a *format*, so evaluate whether replies
actually follow it. `check_format.py` scores the five markers (greeting → `Answer:` →
`Policy:` → `Next step:` → `— Kestrel Home Support`):

```bash
python finetune/check_format.py             # scores the curated dataset — ~100%
python finetune/check_format.py --text generated_replies.txt   # score real model outputs
```

> **What you'll see:** a per-marker pass table and one **format-adherence score** — the
> fraction of replies containing all five markers. The curated set scores **~100%**; that
> same score run on the base model's outputs (before) vs the tuned model's (after) is the
> quantitative version of the before/after demo.

**Beyond SFT — DPO / preference tuning.** The notebook has a **DPO** (Direct Preference
Optimization) section that trains on `kestrel_preference_dataset.jsonl` — **24 chosen/rejected
pairs**, each pairing a correct five-part reply against a sloppy or wrong one.

> **SFT teaches the format; DPO teaches it to *prefer* good replies over bad.** Supervised
> fine-tuning shows the model what a good answer looks like; preference tuning sharpens the
> gap between good and bad so it reliably picks the former.

## Which rung when

| Rung | What it's for | Reach for it when... |
|---|---|---|
| **Prompt** | Instructions + context in the message. | The task fits in a well-written prompt; start here always. |
| **RAG** | Ground answers in *your* documents. | Answers depend on private/changing **facts** the model can't have memorized. |
| **Tools / MCP** | Let the model **do** things — call functions, hit live systems. | You need actions or fresh data: look something up, compute, write to a system. |
| **Skills** | Package reusable **know-how** the model loads on demand. | You have a repeatable procedure/format to apply, and want it loaded only when relevant. |
| **Fine-tune** | Bake a **voice / format** into the weights (SFT for the format; **DPO / GRPO** to prefer good over bad). | You need a consistent style/shape at scale that prompting won't reliably hold — and you accept it teaches behavior, **not facts**. |

## Glossary & exercises

- **[`GLOSSARY.md`](./GLOSSARY.md)** — plain-English definitions (~49 terms) across MCP,
  Agent Skills, and fine-tuning, tied to the Kestrel example. Skim it if a term ever snags.
- **[`EXERCISES.md`](./EXERCISES.md)** — 16 hands-on exercises (MCP → Skills → Fine-tuning →
  a capstone), each with a **Goal**, concrete **Steps** against this repo's files, and a
  **Done when** check. Ordered easy → harder — the fastest way to actually climb the ladder.

## Further reading

- **MCP** — the spec and server catalog: <https://modelcontextprotocol.io>
- **Agent Skills** — Anthropic docs: <https://platform.claude.com>
- **Unsloth** — fine-tuning docs and notebooks: <https://unsloth.ai/docs>
