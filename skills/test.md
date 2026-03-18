---
name: test
description: Run the project test suite and report failures with file and line references
args: <file_or_pattern>
args_optional: true
---

Run the test suite for this project. {args}

## Steps

1. **Discover the test runner** — check for these in order:
   - `pytest.ini`, `pyproject.toml` (look for `[tool.pytest]`), `setup.cfg` → use `pytest`
   - `package.json` with a `test` script → use `npm test`
   - `Makefile` with a `test` target → use `make test`
   - If nothing found, tell the user and stop.

2. **Run the tests** using the `shell` tool with the discovered command.
   - If `{args}` is provided, pass it as a filter/path argument to the test runner.
   - Capture full output including stdout and stderr.

3. **Report results** in this structure:

## Test Results

| Metric | Value |
|--------|-------|
| Passed | … |
| Failed | … |
| Errors | … |
| Skipped | … |
| Duration | … |

### Failures

For each failing test, provide:
- **Test name** with `file:line` reference
- The **assertion error** or exception message
- A brief **diagnosis** of what likely went wrong

### Next Steps
- If all tests pass: "All tests passed ✓"
- If failures exist: suggest the most likely root cause and whether it looks like a pre-existing failure or something related to recent changes
