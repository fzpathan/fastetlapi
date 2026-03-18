---
name: debug
description: Diagnose an error or stack trace and propose a targeted fix
args: <error_message_or_description>
---

Debug this error: {args}

## Steps

1. **Parse the error** — identify: error type, message, file, line number, and any relevant variable values from the trace.

2. **Locate the source** — use `read_file` to read the file at the line referenced in the stack trace. Read 20 lines before and after for context.

3. **Trace the call chain** — if the error originates in a called function, use `grep` to find that function and read it too. Follow the chain up to 3 levels deep.

4. **Identify the root cause** — explain in one sentence what is actually wrong (not just what the error message says).

5. **Propose a fix** — show the exact change needed using a code block. Be surgical — change only what's necessary.

6. **Verify** — after applying the fix with `edit`, re-run the failing command/test to confirm it's resolved.

## Report format

### Error Summary
- **Type**: `ExceptionType`
- **Message**: the error message
- **Location**: `file:line`

### Root Cause
One clear sentence explaining WHY this error occurs.

### Fix
```python
# before
...
# after
...
```

### Verification
Result of re-running after the fix.
