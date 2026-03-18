---
name: scaffold
description: Generate a new file following existing project patterns
args: <description of what to create>
---

Scaffold a new file based on this description: {args}

## Steps

1. **Understand the request** — parse `{args}` to determine:
   - What kind of file (tool, skill, config, test, API route, component, etc.)
   - What it should be named
   - Where it should live

2. **Study existing patterns** — before writing anything, read 2–3 existing files of the same type to understand:
   - File structure and organisation
   - Naming conventions
   - Import style
   - Docstring/comment style
   - Any base classes or interfaces to extend

3. **Generate the file** — use `write_file` to create the new file. The output must:
   - Follow all patterns observed in step 2 exactly
   - Include all required boilerplate (base class, __init__ exports, etc.)
   - Leave TODO comments where the user needs to fill in logic
   - Not add unnecessary comments or padding

4. **Update registrations** — check if the file type needs to be registered somewhere (e.g. tools need adding to `__init__.py`). If so, make that edit too.

5. **Confirm** — tell the user:
   - The path of the created file
   - What TODOs they need to fill in
   - Any registration updates made
