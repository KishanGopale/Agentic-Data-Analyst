"""Tool for generating charts with matplotlib and plotly."""
import logging
import uuid
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
import pandas as pd
from langchain_core.tools import tool

from config import CHARTS_DIR

logger = logging.getLogger(__name__)


@tool
def generate_chart(
    data: dict,
    chart_type: str,
    x_col: str,
    y_col: str,
    title: str = "Chart",
    engine: str = "matplotlib",
) -> dict[str, Any]:
    """Generate a chart image from data.

    Args:
        data: dict with 'columns' and 'rows'.
        chart_type: "bar", "line", "pie", "scatter", "area".
        x_col: column for x-axis.
        y_col: column for y-axis.
        title: chart title.
        engine: "matplotlib" or "plotly".

    Returns:
        dict with 'chart_path' and 'chart_id'.
    """
    df = pd.DataFrame(data["rows"], columns=data["columns"])
    chart_id = str(uuid.uuid4())[:8]
    filename = f"chart_{chart_id}.png"
    filepath = CHARTS_DIR / filename

    try:
        if engine == "plotly":
            fig = _plotly_chart(df, chart_type, x_col, y_col, title)
            fig.write_image(str(filepath), width=900, height=500)
        else:
            _matplotlib_chart(df, chart_type, x_col, y_col, title, filepath)

        logger.info("Chart saved: %s", filepath)
        return {"chart_path": str(filepath), "chart_filename": filename, "chart_id": chart_id}

    except Exception as e:
        logger.error("Chart generation error: %s", e)
        return {"error": str(e)}


def _matplotlib_chart(df, chart_type, x, y, title, filepath):
    fig, ax = plt.subplots(figsize=(10, 5))

    if chart_type == "bar":
        ax.bar(df[x].astype(str), df[y].astype(float), color="#4A90D9")
    elif chart_type == "line":
        ax.plot(df[x].astype(str), df[y].astype(float), marker="o", color="#4A90D9")
    elif chart_type == "pie":
        ax.pie(df[y].astype(float), labels=df[x].astype(str), autopct="%1.1f%%", startangle=140)
        ax.set_title(title)
        fig.tight_layout()
        fig.savefig(str(filepath), dpi=150, bbox_inches="tight")
        plt.close(fig)
        return
    elif chart_type == "scatter":
        ax.scatter(df[x].astype(float), df[y].astype(float), color="#4A90D9", alpha=0.7)
    elif chart_type == "area":
        ax.fill_between(range(len(df)), df[y].astype(float), alpha=0.4, color="#4A90D9")
        ax.plot(range(len(df)), df[y].astype(float), color="#4A90D9")
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(df[x].astype(str), rotation=45, ha="right")

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(str(filepath), dpi=150, bbox_inches="tight")
    plt.close(fig)


def _plotly_chart(df, chart_type, x, y, title):
    funcs = {
        "bar": px.bar,
        "line": px.line,
        "scatter": px.scatter,
        "area": px.area,
        "pie": lambda **kw: px.pie(df, names=x, values=y, title=title),
    }
    fn = funcs.get(chart_type, px.bar)
    if chart_type == "pie":
        return fn()
    return fn(df, x=x, y=y, title=title)
