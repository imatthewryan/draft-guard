#!/usr/bin/env python3
"""Check that an edit keeps protected text and contains no obvious secrets."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path


PROTECTED_PATTERNS = {
    "fenced_code": re.compile(r"```[^\n]*\n.*?```", re.DOTALL),
    "inline_code": re.compile(r"`[^`\n]+`"),
    "url": re.compile(r"\b(?:https?://|mailto:)[^\s<>()]+"),
    "number": re.compile(r"\b\d+(?:[.,]\d+)?%?\b"),
    "date": re.compile(r"\b(?:\d{4}-\d{1,2}-\d{1,2}|\d{1,2}/\d{1,2}/\d{2,4})\b"),
    "quote_block": re.compile(r"(?m)^>.*(?:\n>.*)*$"),
}

SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    re.compile(r"\b(?:sk|pk|rk)-[A-Za-z0-9_-]{20,}\b"),
    re.compile(
        r"\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9/+=._-]{16,}"
    ),
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_secrets(text: str) -> list[str]:
    """Return secret classes, never the matching values."""
    found: list[str] = []
    labels = (
        "private_key",
        "aws_access_key",
        "github_token",
        "slack_token",
        "service_key",
        "named_credential",
    )
    for label, pattern in zip(labels, SECRET_PATTERNS):
        if pattern.search(text):
            found.append(label)
    return found


def protected_items(text: str) -> collections.Counter[tuple[str, str]]:
    items: collections.Counter[tuple[str, str]] = collections.Counter()
    for kind, pattern in PROTECTED_PATTERNS.items():
        for match in pattern.finditer(text):
            items[(kind, match.group(0))] += 1
    return items


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def check_contract(original: str, edited: str) -> dict[str, object]:
    source_secret_classes = find_secrets(original)
    edited_secret_classes = find_secrets(edited)
    expected = protected_items(original)
    actual = protected_items(edited)
    missing: list[dict[str, object]] = []

    for item, count in (expected - actual).items():
        kind, value = item
        missing.append({"kind": kind, "count": count, "digest": digest(value)})

    return {
        "ok": not source_secret_classes and not edited_secret_classes and not missing,
        "secret_candidates": source_secret_classes,
        "edited_secret_candidates": edited_secret_classes,
        "missing_protected_spans": sorted(
            missing, key=lambda entry: (str(entry["kind"]), str(entry["digest"]))
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", required=True, type=Path)
    parser.add_argument("--edited", required=True, type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    result = check_contract(read_text(args.original), read_text(args.edited))
    if args.as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["ok"]:
        print("Edit contract passed.")
    else:
        print("Edit contract failed.")
        if result["secret_candidates"]:
            print("Secret candidates: " + ", ".join(result["secret_candidates"]))
        if result["edited_secret_candidates"]:
            print(
                "Secret candidates introduced by edit: "
                + ", ".join(result["edited_secret_candidates"])
            )
        for item in result["missing_protected_spans"]:
            print(
                f"Missing {item['kind']} span "
                f"(digest {item['digest']}, count {item['count']})."
            )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
