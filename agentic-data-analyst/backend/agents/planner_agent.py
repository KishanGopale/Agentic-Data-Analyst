"""Planner Agent — understands the user question and creates an analysis plan."""
import logging
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

PLANNER_PROMPT = """\
You are a Planner Agent in a multi-agent data analysis system.

Your job is to understand the user's natural-language question about a sales dataset and
produce a structured analysis plan.

The dataset is stored in a SQLite table called `sales` with columns:
  id, date, product, region, quantity, unit_price, sales, profit

You must output a JSON object with these fields:
- "understanding": a brief restatement of what the user wants to know
- "sql_queries": a list of SQL SELECT queries needed (1-3 queries)
- "processing_ops": a list of pandas operations to run on results (use the operation DSL)
- "chart_specs": a list of chart specs, each with: chart_type, x_col, y_col, title, engine
- "focus_areas": key aspects the Insight Agent should analyze

Operation DSL examples:
  "group_by:region:sales:sum"
  "monthly_trend:date:sales"
  "sort:sales:desc"
  "describe"

Respond ONLY with valid JSON. No markdown fences.
"""


def run_planner(llm, question: str, memory_context: str = "") -> dict:
    """Run the planner agent and return the analysis plan."""
    logger.info("Planner Agent processing: %s", question)

    context_note = ""
    if memory_context:
        context_note = f"\n\nRelevant past analyses:\n{memory_context}"

    messages = [
        SystemMessage(content=PLANNER_PROMPT),
        HumanMessage(content=f"User question: {question}{context_note}"),
    ]
    response = llm.invoke(messages)
    import json
    try:
        plan = json.loads(response.content.strip())
    except json.JSONDecodeError:
        # Try to extract JSON from response
        text = response.content.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            plan = json.loads(text[start:end])
        else:
            plan = _fallback_plan(question)
    logger.info("Plan created: %s", plan.get("understanding", ""))
    return plan


def _fallback_plan(question: str) -> dict:
    """Fallback plan if LLM output is not parseable."""
    return {
        "understanding": question,
        "sql_queries": ["SELECT * FROM sales"],
        "processing_ops": ["describe", "group_by:region:sales:sum", "monthly_trend:date:sales"],
        "chart_specs": [
            {"chart_type": "bar", "x_col": "region", "y_col": "sales", "title": "Sales by Region", "engine": "matplotlib"},
            {"chart_type": "line", "x_col": "date", "y_col": "sales", "title": "Monthly Sales Trend", "engine": "matplotlib"},
        ],
        "focus_areas": ["trends", "regional differences", "anomalies"],
    }
