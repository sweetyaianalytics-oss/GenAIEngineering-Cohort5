#!/usr/bin/env python3
"""Evaluate Kestrel format adherence — the programmatic "did fine-tuning work?"

Fine-tuning taught the model a *format*, so the natural way to measure success
is: **do the replies actually follow the five-part Kestrel house format?**

    <greeting line>          (a non-empty first line that isn't one of the markers)
    Answer: ...
    Policy: ...
    Next step: ...
    — Kestrel Home Support   (the sign-off)

For each reply we check those five markers, then report:
  * a per-marker pass rate (what fraction of replies had each piece), and
  * an overall "format-adherence score" — the fraction of replies that had
    ALL FIVE. That overall score is the stand-in for "the fine-tuned model now
    reliably emits the format."

Usage
-----
    # score the curated training set (default) — should be ~100%
    python check_format.py

    # score any jsonl of chat examples, checking the assistant turn
    python check_format.py path/to/data.jsonl

    # score the USER turns instead (rarely useful; here for symmetry)
    python check_format.py data.jsonl --field user

    # score real MODEL OUTPUTS: a plain-text file where replies are separated
    # by a blank-line "----" delimiter (or just given one per file)
    python check_format.py --text generated_replies.txt

Standard library only. Exits 0.
"""

import argparse
import json
import os
import sys

# The five things every compliant Kestrel reply must contain.
MARKERS = ["greeting", "Answer:", "Policy:", "Next step:", "— Kestrel Home Support"]

DEFAULT_DATASET = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "kestrel_support_dataset.jsonl",
)


def check_reply(text):
    """Return a dict {marker: bool} for one reply string."""
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    first = lines[0] if lines else ""

    # A valid greeting is a non-empty first line that is NOT itself one of the
    # body markers (i.e. the reply didn't skip the greeting and open with
    # "Answer:").
    body_prefixes = ("Answer:", "Policy:", "Next step:", "—")
    has_greeting = bool(first) and not first.startswith(body_prefixes)

    return {
        "greeting": has_greeting,
        "Answer:": "Answer:" in text,
        "Policy:": "Policy:" in text,
        "Next step:": "Next step:" in text,
        "— Kestrel Home Support": "— Kestrel Home Support" in text,
    }


def load_from_jsonl(path, field):
    """Yield reply strings from a chat-format jsonl file."""
    replies = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            for msg in obj.get("messages", []):
                if msg.get("role") == field:
                    replies.append(msg.get("content", ""))
    return replies


def load_from_text(path):
    """Yield reply strings from a plain-text file.

    Replies may be separated by a line of dashes ('----' or more); if no such
    delimiter is present the whole file is treated as a single reply.
    """
    with open(path) as f:
        raw = f.read()
    chunks, current = [], []
    for line in raw.splitlines():
        if set(line.strip()) == {"-"} and len(line.strip()) >= 4:
            if current:
                chunks.append("\n".join(current))
                current = []
        else:
            current.append(line)
    if current:
        chunks.append("\n".join(current))
    # Drop empties.
    return [c for c in chunks if c.strip()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=DEFAULT_DATASET,
                        help="jsonl file to evaluate (default: curated dataset)")
    parser.add_argument("--field", default="assistant",
                        choices=["assistant", "user", "system"],
                        help="which chat role to score (default: assistant)")
    parser.add_argument("--text", metavar="FILE",
                        help="score a plain-text file of model outputs instead "
                             "of a jsonl dataset")
    args = parser.parse_args()

    if args.text:
        replies = load_from_text(args.text)
        source = args.text
    else:
        replies = load_from_jsonl(args.path, args.field)
        source = f"{args.path} ({args.field} turns)"

    total = len(replies)
    if total == 0:
        print(f"No replies found in {source}.")
        return 0

    # Tally per-marker hits and count fully-compliant replies.
    marker_hits = {m: 0 for m in MARKERS}
    fully_ok = 0
    for reply in replies:
        result = check_reply(reply)
        if all(result.values()):
            fully_ok += 1
        for m in MARKERS:
            if result[m]:
                marker_hits[m] += 1

    # Print a small table.
    print(f"\nFormat check: {source}")
    print(f"Replies evaluated: {total}\n")
    print(f"  {'marker':<26} {'pass':>6} {'rate':>8}")
    print(f"  {'-' * 26} {'-' * 6} {'-' * 8}")
    for m in MARKERS:
        hits = marker_hits[m]
        print(f"  {m:<26} {hits:>6} {hits / total:>7.1%}")

    score = fully_ok / total
    print(f"\n  {'FORMAT-ADHERENCE SCORE':<26} {fully_ok:>6} {score:>7.1%}")
    print(f"  ({fully_ok}/{total} replies contain all five markers)\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
