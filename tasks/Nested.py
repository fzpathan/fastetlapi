from collections import defaultdict
from typing import Dict, List, Any, Iterable, Tuple, Optional

# ---------------------------
# 1) Flatten: lists -> rows
# ---------------------------
def flatten_json_multirows(obj: Any, parent_key: str = '', sep: str = '.') -> List[Dict[str, Any]]:
    """
    Recursively flattens JSON into multiple rows.
    Any list at any depth generates multiple rows (cartesian expansion).
    Returns: list of flat dict rows.
    """
    if isinstance(obj, dict):
        rows = [{}]
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            sub_rows = flatten_json_multirows(v, new_key, sep)
            # cartesian merge
            merged = []
            for r in rows:
                for sr in sub_rows:
                    if r:
                        nr = r.copy()
                        nr.update(sr)
                        merged.append(nr)
                    else:
                        merged.append(sr.copy())
            rows = merged
        return rows

    elif isinstance(obj, list):
        all_rows = []
        for item in obj:
            all_rows.extend(flatten_json_multirows(item, parent_key, sep))
        return all_rows

    else:
        return [{parent_key: obj}]


# --------------------------------------
# 2) Fast multi-column equality indexer
# --------------------------------------
class MultiColumnIndex:
    """
    Builds O(1) lookup indexes for equality searches on multiple columns.
    - indexes[col_search][search_value] -> list of rows (or target values, but we’ll keep rows for flexibility)
    You can then pull any target column's value fast.
    """
    __slots__ = ("_indexes", "_search_columns")

    def __init__(self, records: List[Dict[str, Any]], search_columns: Iterable[str]):
        # index maps: search_col -> (value -> list of row dicts)
        self._indexes: Dict[str, Dict[Any, List[Dict[str, Any]]]] = {
            col: defaultdict(list) for col in search_columns
        }
        self._search_columns = tuple(search_columns)

        # Tight loop; localize for speed
        idx = self._indexes
        scs = self._search_columns

        for row in records:
            # Only index present columns; skip missing to avoid KeyErrors
            for col in scs:
                if col in row:
                    idx[col][row[col]].append(row)

    def find_first(
        self,
        search_col: str,
        search_value: Any,
        target_col: str,
        default: Any = None
    ) -> Dict[str, Any]:
        """
        Return {target_col: value or None} for the FIRST matching row.
        """
        rows = self._indexes.get(search_col, {}).get(search_value)
        if not rows:
            return {target_col: default}
        r0 = rows[0]
        return {target_col: r0.get(target_col, default)}

    def find_all_values(
        self,
        search_col: str,
        search_value: Any,
        target_col: str
    ) -> Dict[str, List[Any]]:
        """
        Return {target_col: [all matching values]} (deduplicated, order preserved).
        """
        rows = self._indexes.get(search_col, {}).get(search_value, [])
        seen = set()
        out: List[Any] = []
        for r in rows:
            if target_col in r:
                val = r[target_col]
                if val not in seen:
                    seen.add(val)
                    out.append(val)
        return {target_col: out}

    def find_many_first(
        self,
        specs: Iterable[Tuple[str, Any, str]],
        default: Any = None
    ) -> Dict[str, Any]:
        """
        Batch queries. specs is an iterable of (search_col, search_value, target_col).
        Returns a dict aggregating {target_col: value_or_None} for each spec.
        If multiple specs use the same target_col, the later one wins (intentional & fast).
        """
        out: Dict[str, Any] = {}
        idx = self._indexes
        for s_col, s_val, t_col in specs:
            rows = idx.get(s_col, {}).get(s_val)
            if not rows:
                out[t_col] = default
                continue
            r0 = rows[0]
            out[t_col] = r0.get(t_col, default)
        return out


# ------------------------------------------------------
# 3) Glue: process one API response end-to-end, fast
# ------------------------------------------------------
def process_api_response(
    api_response: Any,
    specs: Iterable[Tuple[str, Any, str]],
    # Optional: pass search columns explicitly (faster if specs are constant)
    search_columns: Optional[Iterable[str]] = None
) -> Dict[str, Any]:
    """
    End-to-end:
      - flatten nested JSON into rows
      - build multi-column index over equality columns
      - run multiple equality lookups, return {target_col: value_or_None}

    specs: iterable of (search_col, search_value, target_col)
    search_columns: if None, derived from specs (unique search_col values)
    """
    # 1) Flatten once
    rows = flatten_json_multirows(api_response)

    # 2) Determine which columns to index
    if search_columns is None:
        # derive unique search columns from specs
        search_columns = tuple({s_col for (s_col, _, _) in specs})
    else:
        search_columns = tuple(search_columns)

    # 3) Build indexes once per API call
    index = MultiColumnIndex(rows, search_columns)

    # 4) Execute all lookups in O(1) each
    return index.find_many_first(specs, default=None)


# --------------------------
# Example usage
# --------------------------
if __name__ == "__main__":
    api_response = {
        "id": 1,
        "profile": {"name": "John", "age": 30},
        "orders": [
            {"order_id": 100, "items": [{"sku": "A1", "qty": 2}, {"sku": "B2", "qty": 1}]},
            {"order_id": 101, "items": [{"sku": "C3", "qty": 1}]}
        ],
        "tags": ["vip", "beta"]
    }

    # What do we want to check?
    #   - equality on different columns (after flattening, columns include: id, profile.name, profile.age, order_id, items.sku, qty, tags, etc.)
    # For equality matching, you supply the flattened column name and value to match.
    lookups = [
        ("id", 1, "profile.name"),          # find profile.name where id == 1
        ("profile.age", 30, "order_id"),    # find first order_id where profile.age == 30
        ("items.sku", "C3", "qty"),         # find qty for the row where items.sku == "C3"
        ("profile.name", "Alice", "order_id")  # not found -> None
    ]

    result = process_api_response(api_response, lookups)
    print(result)
    # Example output:
    # {'profile.name': 'John', 'order_id': 100, 'qty': 1, 'order_id': None}
