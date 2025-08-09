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

    # ----------- STRING TRANSFORMATIONS -----------
    def _replace_column_refs(self, formula: str) -> str:
        """Replace bare column names with df['col']"""
        col_pattern = r'\b({})\b'.format('|'.join(map(re.escape, self.df.columns)))
        return re.sub(col_pattern, lambda m: f"df[{repr(m.group(0))}]", formula)

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

    def _process_str_methods(self, formula: str) -> str:
        """Ensure string methods are .str.<method> for Series"""
        str_methods = dir(pd.Series([], dtype="object").str)
        method_pattern = r"(df\[['\"]?\w+['\"]?\])\.(%s)\(" % "|".join(map(re.escape, str_methods))
        return re.sub(method_pattern, r"\1.str.\2(", formula)

    def _process_slices(self, formula: str) -> str:
        """Convert (colname)[start:stop] to .str.slice(start, stop)"""
        slice_pattern = r"\(?(df\[['\"]?\w+['\"]?\])\)?\[(?:(\d*)?:(\d*)?)\]"
        def repl(m):
            col_ref = m.group(1)
            start = m.group(2) if m.group(2) else "None"
            stop = m.group(3) if m.group(3) else "None"
            return f"{col_ref}.str.slice({start}, {stop})"
        return re.sub(slice_pattern, repl, formula)

    # ----------- IF-ELSE CONVERSION -----------
    def _convert_ifelse(self, formula: str) -> str:
        """Convert chained if-else to np.select robustly"""
        tokens = self._tokenize_ifelse(formula)
        conds = []
        vals = []
        for cond, val in tokens[:-1]:
            conds.append(cond)
            vals.append(val)
        default_val = tokens[-1][1]
        return f"np.select([{', '.join(conds)}], [{', '.join(vals)}], default={default_val})"

    def _tokenize_ifelse(self, formula: str):
        """
        Parse nested inline if/else into list of (condition, value) pairs + default.
        Robust against parentheses.
        """
        tokens = []
        remaining = formula.strip()
        while " if " in remaining:
            parts = self._split_if(remaining)
            value, condition, remaining = parts
            tokens.append((condition.strip(), value.strip()))
        tokens.append(("default", remaining.strip()))
        return tokens

    def _split_if(self, expr: str):
        """
        Split 'val if cond else rest' into (val, cond, rest), respecting parentheses.
        """
        # Find the ' if ' that is outside parentheses
        depth = 0
        for i in range(len(expr)):
            if expr[i] == "(":
                depth += 1
            elif expr[i] == ")":
                depth -= 1
            elif depth == 0 and expr[i:i+4] == " if ":
                before = expr[:i]
                after = expr[i+4:]
                # Now find matching else
                depth2 = 0
                for j in range(len(after)):
                    if after[j] == "(":
                        depth2 += 1
                    elif after[j] == ")":
                        depth2 -= 1
                    elif depth2 == 0 and after[j:j+6] == " else ":
                        cond = after[:j]
                        rest = after[j+6:]
                        return before, cond, rest
        raise ValueError("Invalid inline if expression")

    # ----------- MAIN EVALUATOR -----------
    def evaluate(self, formula: str, output_col: str):
        safe_formula = self._replace_column_refs(formula)
        safe_formula = self._process_null_checks(safe_formula)
        safe_formula = self._process_slices(safe_formula)
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
