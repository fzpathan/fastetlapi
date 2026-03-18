---
name: simplify
description: Simplify and improve code quality in a file
args: <file_path>
---

Review `{args}` for opportunities to simplify and improve code quality.

Read the file first using `read_file`. Then look for:
- Dead code or unreachable branches
- Overly complex logic that can be simplified (nested conditionals, redundant checks)
- Duplicated code that can be extracted into a helper
- Unnecessary abstractions or indirection
- Variable or function names that could be clearer

Make the changes using the `edit` tool. Keep changes minimal and focused — do not refactor working logic just for style, and do not add new features.

After editing, briefly summarize:
- What you changed and why
- What you intentionally left alone and why
