#!/usr/bin/env python3
"""Generate a SYNTHETIC Kestrel Home support dataset, programmatically.

Teaching point: **"the data is 80% of the job."** The fine-tune only works
because every training reply follows the identical five-part Kestrel house
format:

    <greeting line>
    Answer: ...
    Policy: ...
    Next step: ...
    — Kestrel Home Support

This script shows how you could MANUFACTURE such a dataset at scale: take a
handful of (question, facts) seeds, pair them with a rotating set of greeting
variants, and stamp them all through one template function so the shape is
byte-for-byte consistent. That consistency is exactly what a small model can
lock onto in a few dozen training steps.

IMPORTANT: this writes to ``kestrel_support_dataset.synthetic.jsonl`` — a
SEPARATE file. The notebook actually trains on the hand-curated
``kestrel_support_dataset.jsonl`` (118 examples), because real hand-written
variety still beats template output for teaching a natural voice. Treat this
script as an illustration of the *method*, not a replacement for the curated
set.

Standard library only. Run:

    python build_dataset.py                 # writes ~all seeds
    python build_dataset.py --n 12          # cap the number of examples
    python build_dataset.py --out mine.jsonl
"""

import argparse
import json
import os

# The system prompt is identical to the curated dataset's, so a model trained
# on either sees the same instruction framing.
SYSTEM = (
    "You are Kestrel Home Support, the assistant for Kestrel Home smart "
    "thermostats. Always reply in the fixed Kestrel house format: a short "
    "greeting line, then 'Answer:' with a direct answer, then 'Policy:' citing "
    "the relevant policy, then 'Next step:' with what to do or the escalation "
    "path, and finish with the sign-off line '— Kestrel Home Support'. Be "
    "concise, accurate, and consistent."
)

# Greeting variants get rotated across examples so the model learns that the
# greeting *slot* is flexible while the rest of the structure is fixed.
GREETINGS = [
    "Thanks for reaching out to Kestrel Home.",
    "Happy to help with that.",
    "Good to hear from you.",
    "Thanks for getting in touch.",
    "Appreciate you contacting Kestrel Home Support.",
    "Let's get this handled for you.",
]

# Each seed is (question, answer, policy, next_step) — the three body fields
# are drawn straight from the Kestrel facts doc so the synthetic replies are
# also factually correct.
SEEDS = [
    (
        "How long is the warranty on my Kestrel thermostat?",
        "Every Kestrel Home device carries a 26-month warranty from the "
        "original purchase date.",
        "Kestrel's standard warranty is 26 months — a deliberate two-month "
        "buffer beyond the usual 24.",
        "Keep your proof of purchase handy; if a defect appears in that "
        "window, reply here and we'll arrange a replacement.",
    ),
    (
        "What's your return window for a refund?",
        "Returns are accepted within 45 days of delivery for a full refund.",
        "Full refunds require the device to be in resalable condition with "
        "its original packaging, returned within 45 days.",
        "Reply with your order number and we'll email you a prepaid return "
        "label.",
    ),
    (
        "Is there a restocking fee if I return an opened unit after 60 days?",
        "Yes — a 12% restocking fee applies to opened returns outside the "
        "45-day window but still within the 26-month warranty.",
        "The 12% fee is waived entirely if the return reason is a confirmed "
        "hardware defect.",
        "Tell us the return reason; if it's a defect we'll waive the fee and "
        "cover shipping.",
    ),
    (
        "How fast is first response on the Comfort+ plan?",
        "Comfort+ targets a 2-hour first response during business hours.",
        "Comfort+ ($4.99/month) includes live chat with a 2-hour target, "
        "8 AM–8 PM Mountain Time, Monday–Saturday.",
        "Start a live chat from your Kestrel app during business hours and "
        "we'll pick it up within the SLA.",
    ),
    (
        "My thermostat smells like it's burning — what do I do?",
        "Please unplug the device now; anything mentioning smoke or a burning "
        "smell is treated as a safety issue.",
        "Any ticket mentioning fire, smoke, burning smell, or sparking is "
        "auto-escalated to Tier 3 Safety Response immediately, bypassing the "
        "normal SLA queue.",
        "I've flagged this for immediate Safety Response escalation; keep the "
        "unit unplugged and reply with your model and order number.",
    ),
    (
        "How many zones does the Kestrel Aria support?",
        "The Kestrel Aria supports up to 12 heating/cooling zones.",
        "The Aria is the flagship (released June 2024) with 12-zone support, "
        "air-quality and humidity sensors, and a 20-hour battery backup.",
        "If you need help mapping your zones, reply and we'll walk through "
        "the Aria setup with you.",
    ),
    (
        "Do you cover water damage under warranty?",
        "No — water damage is not covered under the Kestrel warranty.",
        "Kestrel does not cover water damage, third-party firmware damage, or "
        "damage from outdoor mounting (devices are rated indoor-use only).",
        "If you believe the fault is a manufacturing defect rather than water "
        "damage, reply and we'll open a Tier 2 ticket to review it.",
    ),
    (
        "Can I get a replacement shipped overnight?",
        "Yes — expedited overnight replacement is available for a $35 fee.",
        "Standard warranty replacements ship 2-day air at no cost; overnight "
        "is an optional $35 upgrade.",
        "Reply 'overnight' with your order number and we'll add the $35 "
        "expedite and dispatch today.",
    ),
    (
        "Is there a promo code I can use on my order?",
        "We can apply WARMTH2024 for $20 off a single order.",
        "WARMTH2024 is a goodwill code worth $20 off any single order, valid "
        "through the current fiscal year, limited to one use per customer.",
        "Reply to confirm and we'll apply WARMTH2024 to your next order.",
    ),
    (
        "What happens if my ticket sits unresolved for a few days?",
        "Any ticket unresolved for more than 72 hours is automatically "
        "escalated to a Tier 2 specialist.",
        "The 72-hour auto-escalation applies on top of your plan's SLA to "
        "make sure nothing stalls.",
        "No action needed on your side; if you'd like, reply and we'll check "
        "your ticket's current status now.",
    ),
]


def build_reply(greeting, answer, policy, next_step):
    """Assemble the fixed five-part Kestrel reply from its parts."""
    return (
        f"{greeting}\n\n"
        f"Answer: {answer}\n\n"
        f"Policy: {policy}\n\n"
        f"Next step: {next_step}\n\n"
        "— Kestrel Home Support"
    )


def build_example(seed, greeting):
    """Turn one (question, ...facts) seed into a chat-format training row."""
    question, answer, policy, next_step = seed
    return {
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": question},
            {"role": "assistant",
             "content": build_reply(greeting, answer, policy, next_step)},
        ]
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=None,
                        help="cap the number of examples written")
    parser.add_argument("--out", default=None,
                        help="output path (default: "
                             "kestrel_support_dataset.synthetic.jsonl next to "
                             "this script)")
    args = parser.parse_args()

    out_path = args.out or os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "kestrel_support_dataset.synthetic.jsonl",
    )

    # Rotate greetings across seeds so no two consecutive rows look identical.
    examples = [
        build_example(seed, GREETINGS[i % len(GREETINGS)])
        for i, seed in enumerate(SEEDS)
    ]
    if args.n is not None:
        examples = examples[: args.n]

    with open(out_path, "w") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")

    print(f"Wrote {len(examples)} synthetic examples to {out_path}")
    print("\n===== sample row (assistant reply) =====\n")
    print(examples[0]["messages"][-1]["content"])


if __name__ == "__main__":
    main()
