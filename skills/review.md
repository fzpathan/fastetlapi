---
name: review
description: Code review of current changes or a specific file/ref
args: <file_or_ref>
args_optional: true
---

Perform a thorough code review of {args}.

Use `git diff` (and `git diff --staged` if reviewing uncommitted changes) or `read_file` to examine the relevant code.

Structure your review as:

## Summary
What the changes do in 2–3 sentences.

## Issues
Bugs, logic errors, security concerns, or broken contracts — with `file:line` references. If none, write "None found."

## Suggestions
Improvements for readability, performance, or maintainability. Be specific and actionable.

## Verdict
One of: **Approve** / **Request Changes** / **Needs Discussion** — with a one-sentence rationale.

Be direct and specific. Reference exact line numbers. Do not pad with praise.
