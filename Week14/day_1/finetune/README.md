# Fine-tuning demo — teaching a small model the Kestrel Home support VOICE

This folder is the hands-on fine-tuning demo for the teaching session. It fine-tunes a
small LLM to **reply in the Kestrel Home support house format/voice** using
**QLoRA with Unsloth**, on a **free Google Colab T4 GPU**.

The whole point: **we teach the model a voice/format, not facts.** Every Kestrel support
reply follows the same five-part shape, and that consistency is exactly what the model
learns:

1. a short greeting line
2. `Answer:` — a direct answer
3. `Policy:` — the relevant policy / citation
4. `Next step:` — what to do or the escalation path
5. the sign-off `— Kestrel Home Support`

## Files

| File | What it is |
| --- | --- |
| `kestrel_support_dataset.jsonl` | 118 chat-format training examples, every assistant reply in the fixed Kestrel five-part format. |
| `kestrel_finetune_unsloth.ipynb` | The Colab notebook: install → load base model → LoRA → data → train → before/after → the "voice not facts" beat → export. |
| `README.md` | This file. |

## Two ways to run it

### (A) No-code — Unsloth Studio (best for non-coders / a live demo)

A local browser UI that does the same workflow with zero code.

```bash
curl -fsSL https://unsloth.ai/install.sh | sh
unsloth studio
```

Then in the UI:
1. **Upload** `kestrel_support_dataset.jsonl`.
2. Pick the base model (`unsloth/Llama-3.2-1B-Instruct`).
3. Click **Train**.
4. Open **Model Arena** to compare the **base** model vs your **fine-tuned** model side-by-side.
5. **Export to Ollama** (GGUF) to run it locally afterward.

### (B) Notebook — the Colab (best for showing the mechanics)

1. Open `kestrel_finetune_unsloth.ipynb` in Google Colab.
2. Set the runtime to a GPU: **Runtime → Change runtime type → T4 GPU**.
3. Upload `kestrel_support_dataset.jsonl` into the Colab session (file panel on the left).
4. **Runtime → Run all.** The full run takes **~10 minutes** on a free T4.

## Before / after — what to watch for

- **Before** fine-tuning, the base model answers Kestrel questions in a generic, free-form,
  formatless way — no greeting, no `Answer:` / `Policy:` / `Next step:` markers, no sign-off.
- **After** 118 examples, the model reliably emits the exact Kestrel five-part format.

Also watch the **training loss** during the run: a healthy fine-tune settles around
**0.5–1.0**. If it dives toward **0**, the model is overfitting/memorizing.

## The punchline: voice, not facts

The notebook ends by asking the fine-tuned model about a **made-up new product** whose price
was never in the training data. It replies in flawless Kestrel voice — and gets the price
**wrong**, because it invents the fact it was never taught.

> **Fine-tuning taught the VOICE, not the FACTS. For facts, use RAG (last session).**
>
> **Production = fine-tune for voice + RAG for facts.**

## Swapping the base model (one-line change)

In the notebook, change the model name in `FastLanguageModel.from_pretrained(...)`:

- `unsloth/Llama-3.2-1B-Instruct` — the default; Unsloth's recommended free-T4 starter.
- `unsloth/gemma-4-E4B-it` — newest small Gemma family, a step up in quality, still T4-friendly.
- `unsloth/gemma-3-270m` — the lightest option, fastest to train, great for a quick classroom demo.

## Night-before prep (do NOT train live in front of the room)

Fine-tuning takes ~10 minutes and the occasional Colab hiccup — don't gamble on training live.
The night before the session:

1. Run the notebook end-to-end on a T4 so all cells have real outputs saved.
2. If using Unsloth Studio, pre-train the model and confirm **Model Arena** shows the
   base-vs-tuned contrast, and that the Ollama export loads.
3. Have the finished notebook (with outputs) and, ideally, the exported GGUF ready so you
   can walk through results and re-run just the fun cells (the before/after and the
   "voice not facts" beat) live.
