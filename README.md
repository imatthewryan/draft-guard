# Draft Guard

Draft Guard is a Codex skill for editing and auditing prose without casually changing the writer's meaning, facts, uncertainty, or voice.

It treats every draft as source data. Instructions, commands, links, code comments, or prompt-injection text inside a draft do not control the agent.

## What it does

Draft Guard supports two modes.

### Edit

Edit mode improves clarity while preserving the source contract. It offers three levels:

- **Light:** Fix grammar, ambiguity, repetition, and obvious clutter.
- **Standard:** Improve structure and sentences while preserving the writer's progression and voice.
- **Heavy:** Rebuild structure and phrasing. Draft Guard uses this level only when the user explicitly asks for a full rewrite or major restructure.

Before editing, the skill records the draft's claims, names, terms, numbers, dates, sources, caveats, certainty, voice signals, and locked text. It then checks the result against that internal ledger.

### Audit

Audit mode identifies observable writing patterns without rewriting the draft. Each finding includes:

- The pattern.
- A short quote.
- Its effect on the writing.
- A concrete fix.

Draft Guard does not score the draft or claim that AI wrote it.

## What it protects

Unless the user explicitly asks to change them, Draft Guard preserves:

- Claims, scope, caveats, and certainty.
- Names, product terms, and identifiers.
- Numbers, dates, percentages, and units.
- URLs, citations, footnotes, and quoted text.
- Code, commands, paths, tables, and locked sections.
- Deliberate humor, bluntness, roughness, and other voice signals.

The skill stops instead of guessing when the source is unclear, contradictory, too long to review safely, requires new facts, contains likely credentials, or needs subject-matter judgment.

## Security model

Draft Guard treats the full draft as untrusted source material. Text inside the draft cannot instruct the agent to:

- Reveal hidden prompts or context.
- Open links.
- Run commands.
- Use tools.
- Read unrelated files.
- Install packages.
- Send or persist data.

For legal, medical, financial, safety, compliance, and policy text, Draft Guard limits itself to wording and organization. It preserves conditions, exceptions, and qualifiers and stops when an edit requires expert judgment.

These are model instructions, not a security sandbox. Deterministic guarantees require host controls and programmatic validation.

## Install

Review the repository before installation and pin a commit you trust.

```bash
git clone https://github.com/imatthewryan/draft-guard.git
git -C draft-guard checkout <reviewed-commit-sha>
cp -R draft-guard ~/.codex/skills/draft-guard
```

Restart Codex after installation. Draft Guard disables implicit invocation, so it runs only when explicitly selected or called.

## Use

Standard edit:

```text
Use $draft-guard to edit this draft:

[draft]
```

Light edit:

```text
Use $draft-guard for a light edit. Preserve the structure:

[draft]
```

Audit without rewriting:

```text
Use $draft-guard to audit this draft without rewriting it:

[draft]
```

## Output

Edit mode returns:

1. The complete edited draft.
2. A specific `What changed` list.
3. Risks or unresolved points only when needed.

Audit mode returns one item per finding with the pattern, quote, effect, and fix.

## Included files

- `SKILL.md`: The editing contract and workflow.
- `agents/openai.yaml`: Codex UI metadata and explicit-only invocation policy.
- `references/editorial-patterns.md`: Context-aware writing patterns and exceptions.
- `scripts/check_edit_contract.py`: An optional check for changed protected spans and likely secrets.
- `scripts/test_check_edit_contract.py`: Tests for the contract checker.

The checker uses the Python standard library and requires no third-party packages.

## Validate

```bash
python3 -B scripts/test_check_edit_contract.py
```

The checker adds a deterministic guard for protected spans and likely secrets. It does not prove semantic equivalence or replace human review.
