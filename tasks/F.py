import re
import pandas as pd
import numpy as np

class F:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def _replace_column_refs(self, formula: str) -> str:
        """Replace bare column names with @df['col']"""
        col_pattern = r'\b({})\b'.format('|'.join(map(re.escape, self.df.columns)))
        return re.sub(col_pattern, lambda m: f"@df[{repr(m.group(0))}]", formula)

    def _process_null_checks(self, formula: str) -> str:
        """Convert IsNull/IsNotNull"""
        formula = re.sub(r"IsNull\((@df\[['\"]?\w+['\"]?\])\)", r"\1.isnull()", formula)
        formula = re.sub(r"IsNotNull\((@df\[['\"]?\w+['\"]?\])\)", r"\1.notnull()", formula)
        return formula

    def _process_str_methods(self, formula: str) -> str:
        """
        Dynamically convert col.method(...) → col.str.method(...)
        For any method that exists in pandas.Series.str
        """
        str_methods = dir(pd.Series([]).str)
        method_pattern = r"(\@df\[['\"]?\w+['\"]?\])\.(%s)\(" % "|".join(map(re.escape, str_methods))
        return re.sub(method_pattern, r"\1.str.\2(", formula)

    def _convert_ifelse(self, formula: str) -> str:
        """
        Convert Python ternary:
        A if cond1 else B if cond2 else C
        → np.select([cond1, cond2], [A, B], default=C)
        """
        # This pattern only works for chained two-condition ternary; can be extended
        m = re.match(r"\s*(.+?)\s+if\s+(.+?)\s+else\s+(.+?)\s+if\s+(.+?)\s+else\s+(.+)", formula)
        if m:
            val1, cond1, val2, cond2, val3 = m.groups()
            return f"np.select([{cond1}, {cond2}], [{val1}, {val2}], default={val3})"
        return formula

    def evaluate(self, formula: str, output_col: str):
        safe_formula = self._replace_column_refs(formula)
        safe_formula = self._process_null_checks(safe_formula)
        safe_formula = self._process_str_methods(safe_formula)
        safe_formula = self._convert_ifelse(safe_formula)

        local_dict = {"df": self.df, "np": np}
        result = pd.eval(safe_formula, local_dict=local_dict, engine="python")
        self.df[output_col] = result
        return self.df


import pandas as pd
import numpy as np
import string
import random
from datetime import datetime, timedelta

def random_dataframe(schema: dict, nrows: int, seed: int = None) -> pd.DataFrame:
    """
    Generate a random DataFrame given column names, datatypes, and row count.
    
    Parameters:
        schema (dict): {col_name: dtype} where dtype is one of:
                       'int', 'float', 'str', 'bool', 'date', 'datetime'
        nrows (int): Number of rows
        seed (int): Optional random seed for reproducibility
        
    Returns:
        pd.DataFrame
    """
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
        
    df_data = {}
    
    for col, dtype in schema.items():
        if dtype == "int":
            df_data[col] = np.random.randint(0, 100, nrows)
        elif dtype == "float":
            df_data[col] = np.random.uniform(0, 100, nrows).round(2)
        elif dtype == "str":
            df_data[col] = [
                ''.join(random.choices(string.ascii_lowercase, k=5))
                for _ in range(nrows)
            ]
        elif dtype == "bool":
            df_data[col] = np.random.choice([True, False], nrows)
        elif dtype == "date":
            start_date = datetime(2000, 1, 1)
            df_data[col] = [
                (start_date + timedelta(days=random.randint(0, 7300))).date()
                for _ in range(nrows)
            ]
        elif dtype == "datetime":
            start_date = datetime(2000, 1, 1)
            df_data[col] = [
                start_date + timedelta(days=random.randint(0, 7300),
                                       seconds=random.randint(0, 86400))
                for _ in range(nrows)
            ]
        else:
            raise ValueError(f"Unsupported dtype: {dtype}")
    
    return pd.DataFrame(df_data)

df = pd.DataFrame({
    "col1": [1, None, None, 4],
    "col2": ["xa", "xb", "ya", "za"],
    "col3": [10, 20, 30, 40]
})

f = F(df)

formula_str = "1 if IsNotNull(col1) else 2 if col2.startswith('x') else col3"

result_df = f.evaluate(formula_str, "result")
print(result_df)

# Another example: using endswith + slice
formula_str2 = "100 if col2.endswith('a') else col3"
result_df2 = f.evaluate(formula_str2, "result2")
print(result_df2)
