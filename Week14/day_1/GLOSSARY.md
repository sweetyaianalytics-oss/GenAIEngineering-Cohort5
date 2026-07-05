# Glossary

Plain-English definitions for the three topics in this session — **MCP**, **Agent
Skills**, and **Fine-tuning** — tied to the **Kestrel Home** smart-thermostat support
example wherever it helps. This is a continuation of the LangChain/RAG session, so a few
terms lean on ideas (prompting, RAG, `@tool`) you already have.

One rule worth keeping in your head the whole time: **fine-tuning changes the model's
weights; prompting and RAG do not.** Reach for fine-tuning to teach a *behavior or format*
(the Kestrel voice) and for RAG to supply *facts* (the current warranty table).

## MCP

**Model Context Protocol (MCP)** — An open standard for connecting AI apps to tools and
data. It is the LangChain `@tool` idea, standardized so *any* MCP-aware app can use a given
tool instead of everyone re-writing the same integration. Often called "USB-C for AI."

**Host** — The AI application the user actually runs — Claude Desktop, Claude Code, or an
IDE. The host launches and manages one or more clients. In this repo, Claude Desktop / Claude
Code is the host that talks to the Kestrel server.

**Client** — The connector inside the host that holds a single 1:1 connection to one server.
One host can run many clients (one per server it connects to).

**Server** — A program that exposes capabilities to the model over MCP. It offers up to three
primitives (tools, resources, prompts). `mcp/kestrel_mcp_server.py` is a ~30-line example
server named `kestrel-home`.

**Tool** — A primitive the **model** decides to call — an *action* that does something.
Kestrel's `lookup_warranty(sku)` and `check_restocking_fee(days_since_delivery)` are tools.
Rule of thumb: tools *do* things.

**Resource** — A primitive that is read-only *data / context* the app or model pulls in.
Kestrel's `kestrel://faq` serves the support FAQ text. Rule of thumb: resources *are* things.

**Prompt (primitive)** — A reusable template the **user** deliberately triggers (e.g. from a
menu), not something the model auto-invokes. Kestrel's `support_reply(question)` fills in the
house reply format. Rule of thumb: prompts are *canned starting points* a human picks.

**Transport** — How MCP messages travel between client and server. MCP defines two: **stdio**
(local subprocess) and **Streamable HTTP** (remote web service).

**stdio** — The local transport: the server runs as a subprocess and the client talks to it
over standard input/output. Great for local tools. `python mcp/kestrel_mcp_server.py` runs
over stdio.

**Streamable HTTP** — MCP's remote transport: the server is an ordinary web service on a
single HTTP endpoint (e.g. `http://127.0.0.1:8000/mcp`) through which every message flows,
with streaming responses delivered inline. `mcp/kestrel_http_server.py` serves the same
Kestrel server this way.

**SSE (legacy)** — The older, two-endpoint Server-Sent-Events remote transport that Streamable
HTTP replaced; it was deprecated and removed from the spec in November 2025. "Remote MCP
server" today effectively means Streamable HTTP.

**Sampling** — A capability that lets a *server* ask the *host's* model to complete something
mid-task — the server borrows the host's LLM instead of calling one itself.

**Elicitation** — A capability that lets a server pause and ask the *user* for input mid-task
(e.g. "which order number?") rather than guessing.

**MCP Gateway** — A proxy that sits in front of many MCP servers, presenting them through one
managed entry point (auth, routing, policy, logging). Part of where the ecosystem is heading
in 2026.

**OAuth 2.1** — The standard authorization framework MCP is adopting for remote servers, so a
hosted server can require proper user auth instead of an unguarded localhost URL. Expected to
land broadly in 2026.

**M×N problem** — The integration explosion MCP exists to kill: with **M** apps each needing
**N** tools, you write M×N one-off integrations. MCP turns that into **M + N** — each app
speaks MCP once, each tool exposes a server once, and everything interoperates.

**langchain-mcp-adapters** — A LangChain library that lets a LangChain/LangGraph agent consume
MCP servers as ordinary LangChain tools. Its `MultiServerMCPClient` connects to one or more
servers (e.g. `{"kestrel": {"transport": "streamable_http", "url": ".../mcp"}}`) — the bridge
used by `mcp/langgraph_mcp_client.py`.

## Agent Skills

**Agent Skill** — A folder of instructions (and optional files/scripts) that a model loads
**on demand** when a task matches it — packaged, reusable know-how. `skills/kestrel-support/`
is a skill that makes the model reply in the Kestrel house format.

**SKILL.md** — The one required file in a skill: a Markdown playbook with a YAML frontmatter
header on top. It holds the procedure the model follows (the Kestrel five-part reply format,
escalation rules, tone).

**YAML frontmatter** — The `---`-delimited metadata block at the top of `SKILL.md` carrying at
least `name` and `description`. It is the only part always in context; the body loads only when
the skill triggers.

**description (as trigger)** — The frontmatter sentence that tells the model *when* to use the
skill. It is effectively the trigger — write it around the situations the skill should fire on
(for Kestrel: warranty, returns, SLAs, promo codes, safety, escalation), because a vague
description means the skill won't activate at the right time.

**Progressive disclosure** — The three-tier loading that keeps skills cheap: (1) only
`name` + `description` sit in context always; (2) the full `SKILL.md` body loads when the task
matches; (3) heavier supplementary files (Kestrel's `reference.md`) load *only* when the reply
actually needs them. Deep know-how without paying for it every turn.

**Model-invoked** — Skills activate by the *model* deciding a task matches the description — no
explicit user command or hard-coded trigger. Contrast with an MCP *prompt*, which the user
picks.

**Supplementary files** — The optional extra files a skill bundles beyond `SKILL.md`:
reference docs (Kestrel's `reference.md` with the full SKU/SLA/restocking tables), scripts, or
templates, pulled in on demand under progressive disclosure.

**Executable skill** — A skill that bundles runnable code the model can call as part of its
procedure, not just prose. The planned `skills/kestrel-triage/` skill ships a
`scripts/classify.py` that categorizes an incoming ticket (safety / warranty / returns / …)
so the reply is routed correctly.

## Fine-tuning

**Fine-tuning** — Continuing to train an existing model on your own examples so new behavior
is baked into its **weights**. Unlike prompting or RAG, it actually changes the model. Use it
for *voice / format*; use RAG for *facts*.

**Weights** — The millions/billions of numbers that *are* the trained model — what it learned.
Fine-tuning adjusts these; prompting and RAG only change the input you feed a fixed set of
weights.

**In-context learning (vs fine-tuning)** — Getting new behavior purely from what you put in the
prompt (instructions, examples, retrieved docs) without changing weights. Cheap and instant,
but you pay for those tokens every call and the behavior isn't permanent — the opposite trade
from fine-tuning.

**SFT (Supervised Fine-Tuning)** — The most common kind: train on (input → desired output)
pairs so the model imitates the target replies. The Kestrel demo is SFT on 118 chat examples
whose assistant turns all follow the five-part format.

**Full fine-tuning** — Updating *all* of a model's weights. Most accurate in principle but
memory-hungry and expensive — usually overkill. LoRA is the practical alternative.

**LoRA (Low-Rank Adaptation)** — A parameter-efficient method that freezes the base weights and
trains a small set of new "adapter" weights instead. Far cheaper and faster than full
fine-tuning, with nearly the same effect for tasks like teaching a voice.

**Adapter** — The small trained add-on LoRA produces. You can keep the base model and swap
adapters in/out; a Kestrel voice adapter is a few megabytes versus a multi-gigabyte full model.

**Rank / alpha** — The two main LoRA knobs. **Rank** (`r`) sets the size/capacity of the
adapter (higher = more it can learn, but more to train and more overfit risk); **alpha** scales
how strongly the adapter's changes are applied.

**QLoRA** — LoRA on top of a **quantized** (4-bit) base model. It slashes memory enough to
fine-tune a small model on a free Colab T4 GPU — the method this repo's notebook uses.

**Quantization (4-bit / NF4)** — Storing the model's weights in fewer bits (here 4-bit, in the
**NF4** format) instead of 16/32-bit, so a model fits in far less GPU memory with minimal
quality loss. The "Q" in QLoRA.

**DPO (Direct Preference Optimization)** — A fine-tuning method that learns from *preference*
pairs — "response A is better than B" — to nudge the model toward preferred behavior, without a
separate reward model. Use it to refine *style/behavior* after SFT (a possible use for a
`kestrel_preference_dataset.jsonl`).

**GRPO (Group Relative Policy Optimization)** — A reinforcement-learning fine-tuning method that
scores a *group* of sampled answers against each other and pushes the model toward the
better-scoring ones. Popular for teaching reasoning; heavier machinery than SFT or DPO.

**Preference dataset** — Training data made of comparisons — for each prompt, a "chosen" and a
"rejected" response — the fuel DPO/GRPO consume (as opposed to the single-target pairs SFT
uses).

**Epoch** — One full pass over the training dataset. Train too few and the model underfits;
train too many and it starts memorizing (overfitting).

**Learning rate** — How big a step the optimizer takes on each update. Too high and training is
unstable; too low and it barely learns — one of the first knobs to tune.

**Overfitting** — When the model memorizes the training examples instead of learning the
general pattern, so it parrots the data and generalizes poorly. In the notebook, a training
loss diving toward **0** (healthy is ~**0.5–1.0**) is the tell.

**Catastrophic forgetting** — When fine-tuning on a narrow new task erodes the general
abilities the model already had. A reason to keep runs short, keep learning rates modest, and
prefer LoRA over full fine-tuning.

**Held-out / validation set** — Examples deliberately kept *out* of training so you can measure
whether the model actually generalizes rather than just fitting the training data. Your honest
gauge of overfitting.

**GGUF** — A portable file format for a finished (often quantized) model that runtimes like
Ollama and llama.cpp load. Exporting the tuned Kestrel model to GGUF lets you run it locally
after training.

**Unsloth** — An open-source library that makes LoRA/QLoRA fine-tuning of small models much
faster and lighter on memory — the engine behind this repo's Colab notebook.

**Unsloth Studio** — Unsloth's no-code browser UI: upload the dataset, pick a base model, click
**Train**, then compare base vs tuned in **Model Arena** and export to Ollama (GGUF). The
non-coder path for the demo.

**Base model** — The pretrained model you start from *before* fine-tuning. The demo defaults to
`unsloth/Llama-3.2-1B-Instruct`, swappable to `unsloth/gemma-4-E4B-it` (a step up) or
`unsloth/gemma-3-270m` (lightest, fastest for a live demo).
