"""Data Agent — performs pandas-based data processing on SQL results."""
import logging

from tools.pandas_tool import process_data

logger = logging.getLogger(__name__)


def run_data_agent(sql_results: list[dict], operations: list[str]) -> dict:
    """Process SQL results with specified pandas operations.

    Picks the first successful SQL result that has data and processes it.
    Returns combined processing results.
    """
    logger.info("Data Agent processing with ops: %s", operations)

    all_processed = {}

    for i, sql_res in enumerate(sql_results):
        result = sql_res.get("result", {})
        if "error" in result or not result.get("rows"):
            logger.warning("Skipping SQL result %d (error or empty)", i)
            continue

        processed = process_data.invoke({"data": result, "operations": operations})
        for key, value in processed.items():
            all_processed[f"q{i}_{key}"] = value

    if not all_processed:
        # Fallback: try describe on first result with data
        for sql_res in sql_results:
            result = sql_res.get("result", {})
            if result.get("rows"):
                all_processed = process_data.invoke({"data": result, "operations": ["describe"]})
                break

    logger.info("Data Agent produced %d result keys", len(all_processed))
    return all_processed
