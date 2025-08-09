import re
import pandas as pd
import numpy as np

class Formula:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    # ----------- NULL CHECKS -----------
    @staticmethod
    def is_null(series: pd.Series) -> pd.Series:
        """Custom null detection"""
        return (
            series.isna()
            | (series.astype(str).str.strip() == "")
            | (series.astype(str).str.lower() == "null")
        )

    @staticmethod
    def is_not_null(series: pd.Series) -> pd.Series:
        """Custom not-null detection"""
        return ~Formula.is_null(series)

    # ----------- COLUMN REPLACEMENT -----------
    def _replace_column_refs(self, formula: str) -> str:
        """Replace bare column names with df['col']"""
        col_pattern = r'\b({})\b'.format('|'.join(map(re.escape, self.df.columns)))
        return re.sub(col_pattern, lambda m: f"df[{repr(m.group(0))}]", formula)

    # ----------- SLICE HANDLING -----------
    def _process_slices(self, formula: str) -> str:
        """
        Convert (df['col'])[:3] or (df['col'])[1:5] to df['col'].str.slice(start, stop)
        """
        slice_pattern = re.compile(r"(df\[['\"]?\w+['\"]?\])\s*\[\s*(\d*)\s*:\s*(\d*)\s*\]")
        
        def repl(match):
            col_ref = match.group(1)
            start = match.group(2) if match.group(2) != "" else "None"
            stop = match.group(3) if match.group(3) != "" else "None"
            return f"{col_ref}.str.slice({start}, {stop})"
        
        return slice_pattern.sub(repl, formula)

    # ----------- NULL CHECKS REPLACEMENT -----------
    def _process_null_checks(self, formula: str) -> str:
        """Replace IsNull / IsNotNull with custom calls"""
        formula = re.sub(
            r"IsNull\((df\[['\"]?\w+['\"]?\])\)",
            r"Formula.is_null(\1)",
            formula
        )
        formula = re.sub(
            r"IsNotNull\((df\[['\"]?\w+['\"]?\])\)",
            r"Formula.is_not_null(\1)",
            formula
        )
        return formula

    # ----------- STRING METHODS HANDLING -----------
    def _process_str_methods(self, formula: str) -> str:
        """Ensure string methods and __contains__ are prefixed with .str."""
        str_methods = set(dir(pd.Series([], dtype="object").str))

        # Handle __contains__ → .str.contains
        formula = re.sub(
            r"(df\[['\"]?\w+['\"]?\])\.__contains__\(",
            r"\1.str.contains(",
            formula
        )

        # Handle standard string methods
        method_pattern = re.compile(r"(df\[['\"]?\w+['\"]?\])\.(\w+)\(")

        def repl(match):
            col_ref = match.group(1)
            method = match.group(2)
            if method in str_methods:
                return f"{col_ref}.str.{method}("
            else:
                return match.group(0)

        return method_pattern.sub(repl, formula)

    # ----------- INLINE IF-ELSE TO np.select -----------
    def _convert_ifelse(self, formula: str) -> str:
        """Convert any nested inline if-else to np.select"""
        # Tokenize inline if-else
        pattern = re.compile(r"(.+?)\s+if\s+(.+?)\s+else\s+(.+)")
        conds, vals = [], []
        while True:
            m = pattern.fullmatch(formula)
            if not m:
                default_val = formula.strip()
                break
            val, cond, rest = m.groups()
            conds.append(cond.strip())
            vals.append(val.strip())
            formula = rest.strip()
        return f"np.select([{', '.join(conds)}], [{', '.join(vals)}], default={default_val})"

    # ----------- MAIN EVALUATOR -----------
    def evaluate(self, formula: str, output_col: str):
        safe_formula = self._replace_column_refs(formula)
        safe_formula = self._process_slices(safe_formula)
        safe_formula = self._process_null_checks(safe_formula)
        safe_formula = self._process_str_methods(safe_formula)
        if " if " in safe_formula:
            safe_formula = self._convert_ifelse(safe_formula)

        local_dict = {
            "df": self.df,
            "np": np,
            "Formula": Formula
        }
        self.df[output_col] = eval(safe_formula, {}, local_dict)
        return self.df
