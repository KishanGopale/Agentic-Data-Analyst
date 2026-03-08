"""Tool for pandas-based data processing on query result sets."""
import logging
from typing import Any

import pandas as pd
import numpy as np
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


def _df_from_result(data: dict) -> pd.DataFrame:
    return pd.DataFrame(data["rows"], columns=data["columns"])


@tool
def process_data(data: dict, operations: list[str]) -> dict[str, Any]:
    """Process data returned from SQL with pandas operations.

    Args:
        data: dict with 'columns' and 'rows' from SQL results.
        operations: list of operation strings. Supported:
            - "describe" — summary statistics
            - "group_by:<col>:<agg_col>:<func>" — e.g. "group_by:region:sales:sum"
            - "sort:<col>:<asc|desc>"
            - "monthly_trend:<date_col>:<value_col>"
            - "pct_change:<col>"
            - "corr:<col1>:<col2>"
    """
    df = _df_from_result(data)
    results: dict[str, Any] = {}

    for op in operations:
        try:
            if op == "describe":
                results["describe"] = df.describe().to_dict()

            elif op.startswith("group_by:"):
                _, col, agg_col, func = op.split(":")
                grouped = df.groupby(col)[agg_col].agg(func).reset_index()
                results[f"group_{col}_{func}"] = {
                    "columns": list(grouped.columns),
                    "rows": grouped.values.tolist(),
                }

            elif op.startswith("sort:"):
                parts = op.split(":")
                col = parts[1]
                ascending = parts[2] == "asc" if len(parts) > 2 else True
                df = df.sort_values(col, ascending=ascending)
                results["sorted"] = {
                    "columns": list(df.columns),
                    "rows": df.values.tolist(),
                }

            elif op.startswith("monthly_trend:"):
                _, date_col, value_col = op.split(":")
                df[date_col] = pd.to_datetime(df[date_col])
                monthly = df.groupby(df[date_col].dt.to_period("M"))[value_col].sum().reset_index()
                monthly[date_col] = monthly[date_col].astype(str)
                results["monthly_trend"] = {
                    "columns": list(monthly.columns),
                    "rows": monthly.values.tolist(),
                }

            elif op.startswith("pct_change:"):
                _, col = op.split(":")
                df["pct_change"] = df[col].pct_change().fillna(0)
                results["pct_change"] = df[["pct_change"]].values.tolist()

            elif op.startswith("corr:"):
                _, c1, c2 = op.split(":")
                corr = float(np.corrcoef(df[c1].astype(float), df[c2].astype(float))[0, 1])
                results[f"corr_{c1}_{c2}"] = corr

            else:
                results[op] = f"Unknown operation: {op}"

        except Exception as e:
            logger.error("Data processing error for '%s': %s", op, e)
            results[op] = f"Error: {e}"

    return results
