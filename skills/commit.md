---
name: commit
description: Generate and create a conventional commit for staged changes
args_optional: true
---

Generate a git commit for the currently staged changes.

First run `git status` and use the `git` tool with `operation: "diff"` and `ref: "--staged"` to see what is staged.
If nothing is staged, tell the user and stop.

Write a commit message following the Conventional Commits format:
- Type prefix: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`, `perf:`, `style:`
- Subject line must be under 72 characters, written in the imperative mood ("add X" not "added X")
- If the diff is substantial or touches multiple concerns, add a concise body paragraph after a blank line

Then use the `git` tool with `operation: "commit"` to create the commit.
Do **not** stage or unstage any files — only commit what is already staged.

{args}
