import pandas as pd
import numexpr as ne
import numpy as np

df = pd.DataFrame({
    'a': ['Apple', 'Banana', 'fooBar', 'Apricot'],
    'b': [10, 3, 8, 2],
    'c': [1, 3, 3, 0]
})

# Conditions written as strings referencing df
conditions = [
    "df['a'].str.startswith('A')",
    "df['b'] > 5",
    "df['a'].str.contains('foo') & (df['c'] == 3)"
]

# Values can be constants or column names
values = [1, "df['b']", "df['c']"]
default = 0


def build_where_expr(conditions, values, default):
    expr = str(default)
    for cond, val in reversed(list(zip(conditions, values))):
        expr = f"where({cond}, {val}, {expr})"
    return expr


# Step 1 — create local_dict with precomputed masks
local_dict = {}
for i, cond in enumerate(conditions):
    mask = eval(cond).to_numpy()
    mask_name = f"_mask_{i}"
    local_dict[mask_name] = mask
    conditions[i] = mask_name  # replace in-place

# Step 2 — handle values (if column, convert to array)
for i, val in enumerate(values):
    if isinstance(val, str) and val.startswith("df["):
        col_array = eval(val).to_numpy()
        val_name = f"_val_{i}"
        local_dict[val_name] = col_array
        values[i] = val_name
    else:
        values[i] = str(val)

# Step 3 — build and evaluate expression
expr = build_where_expr(conditions, values, default)
df['new'] = ne.evaluate(expr, local_dict=local_dict)

print("Final Expr:", expr)
print(df)
import json

def flatten_json(obj, parent_key='', sep='.'):
    items = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.update(flatten_json(v, new_key, sep=sep))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.update(flatten_json(v, new_key, sep=sep))
    else:
        items[parent_key] = obj
    return items

# Load once
with open("data.json") as f:
    data = json.load(f)

# Flatten once
flat_data = flatten_json(data)

# Search is now just a dict lookup
print(flat_data.get("user.details.address.city"))
