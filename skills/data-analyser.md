---
name: data-analyser
description: Analyse a CSV file — column types, stats, and unique values
args: <csv_file_path>
---

Analyse the CSV file at `{args}`.

## Instructions

Use the `shell` tool to run a Python one-shot analysis script. Do **not** install any packages — use only the Python standard library (`csv`, `collections`, `statistics`). Write and execute the script in a single `shell` call.

The script must:

1. **Read** the CSV file using the `csv` module.
2. **Infer column type** for each column using these rules (inspect all non-empty values):
   - `integer` — all non-empty values parse as `int`
   - `float` — all non-empty values parse as `float` (and at least one has a decimal)
   - `boolean` — all non-empty values are in `{true, false, yes, no, 0, 1}` (case-insensitive)
   - `date` — all non-empty values match `YYYY-MM-DD` or `DD/MM/YYYY` or `MM/DD/YYYY`
   - `text` — everything else
3. **Compute per-column statistics:**
   - Total rows, non-empty count, null/empty count, null %
   - For `integer` / `float`: min, max, mean, median
   - For `text`: avg character length, shortest value, longest value
   - For `boolean`: true count, false count
4. **List unique values** for any column that has **≤ 5 distinct non-empty values** (all types).
5. **Detect potential issues:**
   - Columns where null % > 20 % → flag as `⚠ high nulls`
   - Columns with only 1 unique value → flag as `⚠ constant column`
   - Columns whose name is empty or starts with `Unnamed` → flag as `⚠ unnamed column`

## Output format

After running the script, present the results in this exact markdown structure:

---

# Data Analysis: `{args}`

## Overview
| Metric | Value |
|--------|-------|
| File | `{args}` |
| Total rows | … |
| Total columns | … |
| Columns with nulls | … |
| Columns with ≤ 5 unique values | … |

---

## Column Profiles

Repeat the following block for **every** column:

### `<column_name>` · *<inferred_type>* <flags>

| Property | Value |
|----------|-------|
| Non-empty | … / … (…%) |
| Nulls | … (…%) |
| Unique values | … |
| … (type-specific stats) | … |

> **Unique values:** `val1`, `val2`, `val3`  ← only when ≤ 5 unique values

---

## Summary & Observations

- Bullet list of the most important findings (data quality issues, interesting distributions, columns that look like IDs, high-cardinality text columns, etc.)
- Flag any columns with `⚠` issues detected above.
- Suggest which columns are likely **categorical**, **continuous**, **identifier**, or **target** variables based on their profiles.

---

**Important rules:**
- If `{args}` is empty or the file does not exist, stop immediately and tell the user: "Please provide a valid CSV file path. Usage: `/data-analyser <path/to/file.csv>`"
- Do not modify the CSV file.
- Do not print raw CSV rows — only the structured analysis above.
- Keep numeric values rounded to 2 decimal places.
