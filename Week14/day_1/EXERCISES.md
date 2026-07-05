# Hands-on exercises

Work through these during (and after) the session to climb the capability ladder yourself:
**MCP** (rung 3), **Agent Skills** (rung 4), **Fine-tuning** (rung 5), then a **Putting it
together** capstone. Everything stays in the **Kestrel Home** smart-thermostat support world
from the LangChain/RAG session, so each exercise builds on a world you already know.

Each exercise has a **Goal**, concrete **Steps** (pointing at the repo's real files and
commands), and a **Done when** success check. They are ordered easy → harder within each
group — do them in order. All commands run from the repo root unless noted.

> tip: set up only the demo you're on. The three have deliberately different requirements —
> MCP needs Node/`npx` + Claude Desktop (and Python 3.10+ for the bonus server), Skills needs
> a skills-aware client, and Fine-tuning needs only a browser. See the root `README.md`.

---

## MCP

> tip: MCP is the LangChain `@tool` idea, standardized. If you can write a `@tool`, you can
> write an MCP tool — the new part is the *host/client/server* wiring around it.

### 1. Run the bonus Kestrel server and call it (easiest)
**Goal:** See a real MCP server expose all three primitives and watch Claude call it.
**Steps:**
1. Set up the Python 3.10+ env (`README.md` → "Python for the bonus MCP server only").
2. Register the server for Claude Code via the project-scoped `mcp/.mcp.json` (picked up
   automatically), or add the same `"kestrel"` block to your Claude Desktop config and fully
   restart it.
3. Ask, in plain English: *"What's the warranty on SKU KH-AR-GLD?"* and *"A customer wants to
   return a thermostat 60 days after delivery — what's the fee?"*
**Done when:** Claude calls `lookup_warranty` (returns the 26-month status) and
`check_restocking_fee` (returns the 12% / waived-for-defect answer) and uses the results.

### 2. Connect an off-the-shelf server in Claude Desktop
**Goal:** Prove MCP is a standard — run official servers with *zero* new code.
**Steps:**
1. Copy `mcp/claude_desktop_config.example.json` into your Claude Desktop config
   (`mcp/README.md` has the per-OS path).
2. Set a real folder path for the **filesystem** server (it can only touch paths you list).
3. Fully quit and reopen Claude Desktop, then ask: *"Organize the files in this folder by
   type."*
**Done when:** Claude asks permission and calls the filesystem MCP tools to act on your folder.

> tip: the **github** server in that same file needs a Personal Access Token. Skip it if you
> don't want to mint one — filesystem alone makes the point.

### 3. Add a new tool: `get_promo_code`
**Goal:** Extend the server yourself — the "aha" moment.
**Steps:**
1. In `mcp/kestrel_mcp_server.py`, add a new `@mcp.tool()` function
   `get_promo_code(reason: str) -> str` that returns the goodwill code `WARMTH2024`
   ($20 off, one use per customer) — matching `skills/kestrel-support/SKILL.md`.
2. Restart the server (and the client, so it re-reads the tool list).
3. Ask Claude: *"A customer's order was delayed — can I offer them anything?"*
**Done when:** Claude discovers and calls `get_promo_code` and surfaces `WARMTH2024` in its
reply.

### 4. Serve the same server over Streamable HTTP
**Goal:** Feel the difference between a **local (stdio)** and a **remote (HTTP)** server.
**Steps:**
1. Run `python mcp/kestrel_http_server.py` — it serves on `http://127.0.0.1:8000/mcp` and
   stays running (Ctrl-C to stop).
2. Point a client at the **URL** instead of a command, e.g. a Claude config block
   `{ "mcpServers": { "kestrel-http": { "url": "http://127.0.0.1:8000/mcp" } } }`.
3. Ask the same warranty question and confirm it still works.
**Done when:** the warranty/restocking tools answer through the HTTP endpoint, and you can
articulate why Streamable HTTP (not legacy SSE) is the remote transport.

### 5. Wire the server into a LangGraph agent (hardest)
**Goal:** Consume an MCP server from LangChain, closing the loop with last session.
**Steps:**
1. Open `mcp/langgraph_mcp_client.py` (the `langchain-mcp-adapters` bridge).
2. Confirm it builds a `MultiServerMCPClient` pointed at the Kestrel server (stdio or
   `streamable_http`) and hands the tools to a LangGraph agent.
3. Run it and ask a warranty/restocking question through the agent.
**Done when:** the LangGraph agent answers by calling the Kestrel MCP tools — the same tools,
now driven from your own LangChain code instead of Claude Desktop.

---

## Agent Skills

> tip: a skill is just a folder with a `SKILL.md`. The magic is **progressive disclosure** —
> watch *when* each layer loads.

### 1. Activate the Kestrel support skill (easiest)
**Goal:** See a skill fire on its own and reply in the house format.
**Steps:**
1. Put `skills/kestrel-support/` where your client loads skills (for Claude Code, a `skills/`
   or `.claude/skills/` directory).
2. Ask a Kestrel support question, e.g. *"A customer says their Nest-7 has a burning smell —
   what do I tell them?"*
**Done when:** the reply follows the five parts (greeting → answer → policy → next step →
`— Kestrel Home Support`) and escalates the burning-smell case to Tier 3 Safety Response.

### 2. Observe progressive disclosure
**Goal:** See the three tiers load only as needed.
**Steps:**
1. Ask a simple question the `SKILL.md` body fully answers (e.g. the return window).
2. Then ask something that needs the SKU-by-SKU / SLA tables in
   `skills/kestrel-support/reference.md` (e.g. *"exact warranty details for KH-N7P-SLV"*).
3. Note when `reference.md` gets pulled in versus when only `SKILL.md` was enough.
**Done when:** you can explain the three tiers — always-loaded `name`+`description`, then the
`SKILL.md` body on match, then `reference.md` only when the reply needs it.

### 3. Tune the `description` trigger
**Goal:** Learn that the frontmatter `description` *is* the trigger.
**Steps:**
1. Read the `description` in `skills/kestrel-support/SKILL.md`'s YAML frontmatter.
2. Temporarily narrow it (e.g. drop "warranty, returns … safety … escalation" down to just
   "returns"), then ask a *warranty* question and see whether the skill still fires.
3. Restore the full, situation-rich description.
**Done when:** you've seen the skill fail to activate on the narrowed description and reliably
activate on the full one — proving the description drives triggering.

### 4. Write a new skill: `kestrel-triage`
**Goal:** Author your own skill from scratch, including a bundled script.
**Steps:**
1. Create `skills/kestrel-triage/SKILL.md` with a YAML `name` + a trigger-shaped
   `description` (e.g. "categorize an incoming Kestrel ticket into safety / warranty /
   returns / billing / other").
2. Add a bundled `scripts/classify.py` that takes a ticket string and prints the category
   (an **executable skill**), and reference it from the `SKILL.md` body.
3. Load the folder and paste in a sample ticket.
**Done when:** the skill activates on a raw ticket, runs `classify.py`, and returns a category
that routes the reply (safety → Tier 3, unresolved >72h → Tier 2, etc.).

> tip: keep the `SKILL.md` body short and push the heavy detail (full category rules, tables)
> into a supplementary file so progressive disclosure keeps it cheap.

---

## Fine-tuning

> tip: the mantra for this whole section — **fine-tuning teaches the VOICE / FORMAT, not the
> FACTS.** Facts are RAG's job (last session).

### 1. Score the dataset with `check_format.py` (easiest)
**Goal:** Measure format adherence — the programmatic "did fine-tuning work?"
**Steps:**
1. Run `python finetune/check_format.py` (it defaults to the curated
   `kestrel_support_dataset.jsonl`).
2. Read the per-marker table (greeting, `Answer:`, `Policy:`, `Next step:`,
   `— Kestrel Home Support`) and the overall **format-adherence score**.
**Done when:** you see a score near **100%** on the curated set and can explain that the score
is the fraction of replies containing all five markers.

### 2. Generate synthetic data and inspect it
**Goal:** See how a byte-consistent dataset is manufactured ("the data is 80% of the job").
**Steps:**
1. Run `python finetune/build_dataset.py` — it writes
   `kestrel_support_dataset.synthetic.jsonl` (a *separate* file) and prints a sample row.
2. Open the file and confirm every assistant reply follows the identical five-part shape.
3. Score it: `python finetune/check_format.py finetune/kestrel_support_dataset.synthetic.jsonl`.
**Done when:** the synthetic file scores ~100% and you can point to the greeting-rotation +
template trick that makes the shape byte-for-byte consistent.

### 3. Add 10 examples and re-check
**Goal:** Practice extending a dataset without breaking the format.
**Steps:**
1. Add 10 new `(question, answer, policy, next_step)` seeds to the `SEEDS` list in
   `build_dataset.py` (drawn from real Kestrel facts — 26-month warranty, 45-day / 12% policy,
   SLAs).
2. Regenerate, then run `check_format.py` on the output.
3. Deliberately break one example (drop its `Policy:` line) and re-run to watch the score drop.
**Done when:** your additions keep the score at ~100%, and the broken example makes the score
fall — so you trust the check.

### 4. Run the SFT cells in Colab
**Goal:** Do the real fine-tune and see before/after.
**Steps:**
1. Open `finetune/kestrel_finetune_unsloth.ipynb` in Google Colab; set **Runtime → Change
   runtime type → T4 GPU**.
2. Upload `finetune/kestrel_support_dataset.jsonl` and **Runtime → Run all** (~10 min).
3. Compare the base model's formatless answer to the tuned model's five-part reply; watch the
   training loss settle around **0.5–1.0** (diving toward 0 = overfitting).
**Done when:** the tuned model reliably emits the Kestrel format, and the "made-up product"
cell replies in flawless voice while getting the **price wrong** — voice, not facts.

> tip: prefer no-code? Do the same run in **Unsloth Studio** (`unsloth studio`): upload,
> **Train**, compare in **Model Arena**, export to Ollama (GGUF).

### 5. Read the DPO/preference section and reason about it (hardest)
**Goal:** Know when to reach past SFT for **DPO** (and where **GRPO** fits).
**Steps:**
1. Read the DPO / preference-dataset section of `finetune/README.md` (and, if present, peek at
   `finetune/kestrel_preference_dataset.jsonl` — "chosen" vs "rejected" reply pairs).
2. In a sentence or two, describe a Kestrel scenario where SFT isn't enough and you'd want DPO
   (e.g. two format-correct replies where one has the *right tone* and one doesn't).
**Done when:** you can explain that SFT imitates single target replies while DPO learns from
*preference pairs*, and name a Kestrel case that calls for it.

---

## Putting it together

### 1. Design the full Kestrel agent (capstone)
**Goal:** Combine every rung into one coherent Kestrel Home support agent.
**Steps:**
1. Sketch (on paper or in a doc) an agent that uses **all five rungs**:
   - **Prompt** — a system prompt setting the Kestrel support role.
   - **RAG** — retrieve current facts from `docs/kestrel_home_faq.md` (last session's job).
   - **MCP** — call `lookup_warranty` / `check_restocking_fee` (and your `get_promo_code`) for
     live actions.
   - **Skill** — `kestrel-support` for the house format + escalation procedure, and
     `kestrel-triage` to route the ticket.
   - **Fine-tuned voice model** — the SFT'd small model that emits the five-part voice
     reliably.
2. For each rung, write one line on *why it's there* — and where you'd stop if the problem
   were simpler (climb only as high as the problem needs).
**Done when:** your diagram shows facts coming from RAG, actions from MCP, procedure from the
Skill, and voice from fine-tuning — and you can defend why each rung earns its place.

### 2. Pick the right rung for five tickets
**Goal:** Internalize the "which rung when" table under pressure.
**Steps:**
1. Take five Kestrel requests, e.g.: (a) "what's today's warranty policy?", (b) "issue this
   customer a refund", (c) "reply in our house format", (d) "answer 10,000 tickets in a
   consistent voice", (e) "what zones does the Aria support right now?".
2. For each, name the *lowest* rung that solves it (Prompt / RAG / MCP / Skill / Fine-tune) and
   say why a higher rung would be over-reaching.
**Done when:** your answers match the `README.md` "Which rung when" table — facts → RAG,
actions → MCP, repeatable procedure/format → Skill, voice-at-scale → Fine-tune, and simplest
cases → Prompt.
