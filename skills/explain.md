---
name: explain
description: Explain a function, class, or file in plain language with examples
args: <file_path_or_function>
---

Explain `{args}` clearly and completely.

## Steps

1. Use `read_file` or `grep` to locate and read the relevant code.
2. If `{args}` is a file path, explain the whole module.
   If `{args}` looks like a function or class name, use `grep` to find it first.

## Output format

### Purpose
What this code does and why it exists (1–3 sentences, no jargon).

### How it works
Step-by-step walkthrough of the logic. Use numbered steps. Reference line numbers with `file:line` notation.

### Parameters / Inputs
Table of inputs with types and what they mean.

### Return value / Output
What it produces and in what format.

### Example
A short, concrete usage example (code block).

### Edge cases & gotchas
Any non-obvious behaviour, known limitations, or things a caller must be careful about.

Keep the explanation precise. Avoid vague language like "handles", "manages", "deals with" — say exactly what the code does.
