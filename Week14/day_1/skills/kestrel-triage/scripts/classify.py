#!/usr/bin/env python3
"""Kestrel Home support-ticket triage classifier (stdlib only, deterministic).

Usage:
    python classify.py "<ticket text>"

Prints a small JSON verdict with the tier, a one-line reason, and the routed
contact. Escalation rules mirror docs/kestrel_home_faq.md:
  * Tier 3 / IMMEDIATE  — text mentions fire / smoke / burning / sparking.
  * Tier 2              — implies >72h unresolved OR repeated contact.
  * Tier 1              — everything else (normal first-touch support).
"""

import json
import re
import sys

# Keywords that force an immediate Tier 3 safety escalation.
SAFETY_TERMS = ("fire", "smoke", "burning", "spark")  # "spark" matches sparking/sparks

# Phrases that imply the ticket is stale (>72h) or a repeat contact -> Tier 2.
STALE_TERMS = (
    "still no", "no reply", "no response", "no answer", "days ago", "a week",
    "week ago", "weeks", "haven't heard", "have not heard", "third time",
    "second time", "again", "follow up", "follow-up", "following up",
    "escalate", "unresolved", "still waiting", "no one has",
)

# Regexes for an explicit age that exceeds the 72-hour SLA window.
HOURS_RE = re.compile(r"(\d+)\s*(?:hours|hrs|hr)\b")
DAYS_RE = re.compile(r"(\d+)\s*days?\b")


def _exceeds_sla(text: str) -> bool:
    """True if the text states an age > 72 hours (i.e. > 3 days)."""
    for n in HOURS_RE.findall(text):
        if int(n) > 72:
            return True
    for n in DAYS_RE.findall(text):
        if int(n) > 3:
            return True
    return False


def classify(text: str) -> dict:
    lowered = text.lower()

    if any(term in lowered for term in SAFETY_TERMS):
        return {
            "tier": 3,
            "urgency": "IMMEDIATE",
            "reason": "Mentions a fire/smoke/burning/sparking hazard — safety escalation.",
            "route": "Safety Response (auto-paged via on-call; do not route manually).",
        }

    if _exceeds_sla(lowered) or any(term in lowered for term in STALE_TERMS):
        return {
            "tier": 2,
            "urgency": "HIGH",
            "reason": "Implies >72h unresolved or repeated contact — past the SLA window.",
            "route": "Marcus Webb, Support Operations Lead, ext 4471.",
        }

    return {
        "tier": 1,
        "urgency": "NORMAL",
        "reason": "Standard first-touch question with no safety or SLA-breach signals.",
        "route": "Standard support queue (first-response per plan SLA).",
    }


def main(argv: list) -> int:
    if len(argv) < 2 or not argv[1].strip():
        print('Usage: python classify.py "<ticket text>"', file=sys.stderr)
        return 2
    verdict = classify(argv[1])
    print(json.dumps(verdict, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
