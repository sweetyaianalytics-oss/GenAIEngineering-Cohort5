---
name: kestrel-triage
description: Triage and classify an incoming Kestrel Home support ticket by urgency and route it to the right tier. Use whenever a Kestrel Home support ticket, complaint, or customer message arrives and you need to decide how fast to act and who owns it — especially to catch safety hazards (fire/smoke/sparking) that must escalate immediately.
---

# Kestrel Home Ticket Triage

This skill classifies an incoming Kestrel Home support ticket into a tier and
routes it to the right owner. Unlike a prose-only skill, it **bundles an
executable script** — the classification rules run in code, so the verdict is
deterministic and identical every time.

## When to use

Use this the moment a Kestrel Home support ticket, email, chat, or complaint
comes in and you need to decide urgency and ownership — before drafting a reply.
The highest-value case is catching a safety hazard that must bypass the normal
queue.

## How to use it — RUN the script

Do not eyeball the rules by hand. Run the bundled classifier and use its output:

```
python scripts/classify.py "<the full ticket text>"
```

It prints JSON like:

```json
{
  "tier": 3,
  "urgency": "IMMEDIATE",
  "reason": "Mentions a fire/smoke/burning/sparking hazard — safety escalation.",
  "route": "Safety Response (auto-paged via on-call; do not route manually)."
}
```

Take the `tier`, `urgency`, and `route` from that output and act on them. Then
continue handling the ticket (e.g. draft the reply, open the ticket at that tier).

## Escalation rules (what the script encodes)

- **Tier 3 / IMMEDIATE** — the ticket mentions **fire, smoke, burning, or
  sparking**. This is a safety hazard: it auto-escalates to **Safety Response**
  (paged automatically via the on-call system — do NOT route it manually) and
  bypasses the normal SLA queue entirely.
- **Tier 2 / HIGH** — the ticket implies it has been **unresolved for more than
  72 hours** or is a **repeated contact** (e.g. "still no reply after 4 days",
  "third time I've written"). Route to **Marcus Webb**, Support Operations Lead,
  **ext 4471**.
- **Tier 1 / NORMAL** — everything else: a standard first-touch question with no
  safety or SLA-breach signals. Handle in the normal support queue per the
  customer's plan SLA.

These mirror the escalation policy in `docs/kestrel_home_faq.md`.

## Why a script (progressive disclosure)

The agent reads this short SKILL.md only when a ticket needs triage — and the
`scripts/classify.py` code loads and runs only at that moment. The heavier,
exact logic stays out of context until it's actually needed, and running it in
code (rather than re-deriving the rules in prose each time) keeps the verdict
deterministic and auditable.
