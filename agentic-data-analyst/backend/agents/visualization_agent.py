"""Visualization Agent — generates charts based on the plan's chart specs."""
import logging

from tools.chart_tool import generate_chart

logger = logging.getLogger(__name__)


def run_visualization_agent(sql_results: list[dict], chart_specs: list[dict]) -> list[dict]:
    """Generate charts from SQL results using the chart specs from the planner.

    Returns list of chart result dicts with paths.
    """
    logger.info("Visualization Agent generating %d charts", len(chart_specs))

    charts = []

    # Find the best data source for each chart
    for spec in chart_specs:
        data = _find_matching_data(sql_results, spec)
        if data is None:
            logger.warning("No matching data for chart: %s", spec.get("title"))
            continue

        result = generate_chart.invoke({
            "data": data,
            "chart_type": spec.get("chart_type", "bar"),
            "x_col": spec["x_col"],
            "y_col": spec["y_col"],
            "title": spec.get("title", "Chart"),
            "engine": spec.get("engine", "matplotlib"),
        })

        if "error" not in result:
            charts.append(result)
        else:
            logger.error("Chart error: %s", result["error"])

    logger.info("Generated %d charts", len(charts))
    return charts


def _find_matching_data(sql_results: list[dict], spec: dict) -> dict | None:
    """Find the SQL result whose columns include the chart's x_col and y_col."""
    x = spec["x_col"]
    y = spec["y_col"]

    for sql_res in sql_results:
        result = sql_res.get("result", {})
        cols = result.get("columns", [])
        if x in cols and y in cols and result.get("rows"):
            return result

    # Fallback: return first result with data
    for sql_res in sql_results:
        result = sql_res.get("result", {})
        if result.get("rows"):
            return result

    return None
