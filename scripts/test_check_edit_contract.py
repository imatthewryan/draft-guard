#!/usr/bin/env python3
"""Tests for check_edit_contract.py."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("check_edit_contract.py")
SPEC = importlib.util.spec_from_file_location("check_edit_contract", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class EditContractTests(unittest.TestCase):
    def test_passes_when_protected_content_survives(self) -> None:
        original = (
            "Ship 3 fixes by 2026-07-22: https://example.com/docs.\n"
            "```sh\necho safe\n```\n"
            "Keep `--dry-run` and this quote:\n> Keep this line.\n"
        )
        edited = (
            "Ship 3 fixes by 2026-07-22: https://example.com/docs.\n"
            "```sh\necho safe\n```\n"
            "Keep `--dry-run` and this quote:\n> Keep this line.\n"
        )
        result = MODULE.check_contract(original, edited)
        self.assertTrue(result["ok"], result)

    def test_fails_when_protected_content_is_removed(self) -> None:
        original = "Read https://example.com/docs and ship 3 fixes."
        edited = "Read the docs and ship three fixes."
        result = MODULE.check_contract(original, edited)
        self.assertFalse(result["ok"])
        self.assertEqual(
            {"url", "number"},
            {item["kind"] for item in result["missing_protected_spans"]},
        )

    def test_fails_without_echoing_a_secret(self) -> None:
        original = "Use api_key=sk_test_12345678901234567890 in the example."
        result = MODULE.check_contract(original, original)
        self.assertFalse(result["ok"])
        self.assertEqual(["named_credential"], result["secret_candidates"])

    def test_fails_when_an_edit_introduces_a_secret(self) -> None:
        original = "Use a placeholder in the example."
        edited = "Use api_key=sk_live_12345678901234567890 in the example."
        result = MODULE.check_contract(original, edited)
        self.assertFalse(result["ok"])
        self.assertEqual(["named_credential"], result["edited_secret_candidates"])


if __name__ == "__main__":
    unittest.main()
