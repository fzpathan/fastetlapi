---
name: xlsx-analyser
description: Analyse an Excel (.xlsx/.xls) or CSV file — sheets, column types, stats, and data quality
args: <file_path>
---

Analyse the spreadsheet file at `{args}`.

## Step 1 — Validate the file

Check that `{args}` is not empty and the file exists using the `glob` or `shell` tool.
If the file does not exist or no path was given, stop immediately and tell the user:

> "Please provide a valid file path. Usage: `/xlsx-analyser <path/to/file.xlsx>`"

Supported formats: `.xlsx`, `.xls`, `.xlsm`, `.csv`

---

## Step 2 — Run the analysis script

Use the `shell` tool to execute:

```bash
python {skill_dir}/scripts/analyse.py "{args}"
```

The script outputs a JSON report to stdout. Capture this output — it is the source of truth for everything below.

### If openpyxl is missing

If the script exits with `"openpyxl is not installed"`, install it first:

```bash
pip install openpyxl
```

Then re-run the analysis script.

### If the file has multiple sheets

The JSON will contain a `sheet_names` array listing all sheets. Analyse all sheets by default.
If the user specified a particular sheet, re-run with the `--sheet` flag:

```bash
python {skill_dir}/scripts/analyse.py "{args}" --sheet "SheetName"
```

---

## Step 3 — Format and present the results

Parse the JSON and present the analysis in the following markdown structure. **Do not show raw JSON to the user.**

---

# Spreadsheet Analysis: `{args}`

## Overview

| Metric | Value |
|--------|-------|
| File | `{args}` |
| Format | *(from JSON: format)* |
| Sheets | *(count and names)* |
| Total rows | *(sum across all sheets)* |
| Total columns | *(per sheet if multiple)* |

---

For **each sheet** in the workbook, render the following sections:

## Sheet: `<sheet_name>`

> *<dimensions from JSON>*

### Column Profiles

For **every column**, render:

#### `<column_name>` · *<inferred_type>* <flags>

| Property | Value |
|----------|-------|
| Non-empty | X / Y (Z%) |
| Nulls | X (Z%) |
| Unique values | N |
| *(type-specific stats)* | *(see rules below)* |

**Type-specific stat rows to add:**

- `integer` / `float`: Min, Max, Mean, Median, Std Dev
- `boolean`: True count, False count
- `text`: Avg length, Min length, Max length, Top values
- `date`: Earliest, Latest

**If unique_values is not null** (≤ 5 unique values), add after the table:

> **Distinct values:** `val1`, `val2`, `val3`

**Flag rendering:**
- `high_nulls` → append `⚠ high nulls` after the type
- `constant_column` → append `⚠ constant` after the type
- `unnamed_column` → append `⚠ unnamed` after the type

---

### Data Quality Issues

If the sheet has entries in `issues`, list them as bullet points under this heading.
If no issues, write: *No issues detected.*

---

## Summary & Recommendations

After all sheets are profiled:

1. **Data quality** — highlight the most critical issues across all sheets (nulls, constants, unnamed columns)
2. **Column roles** — classify each column as likely: `identifier`, `categorical`, `continuous`, `boolean`, `datetime`, or `text`
3. **Recommendations** — concrete next steps (e.g. "Column 'age' has 35% nulls — consider imputation or removal before modelling")
4. **Sheet relationships** — if multiple sheets exist, note any columns that appear to be foreign keys or shared identifiers

---

## Rules

- Round all numeric values to 2 decimal places
- Do not modify the source file
- Do not show raw Python output or JSON to the user — only the formatted report above
- If `error` is set in the JSON, report the error clearly and suggest a fix
