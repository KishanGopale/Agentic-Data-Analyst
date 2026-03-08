"""Insight Agent — uses LLM reasoning to explain patterns and trends."""
import logging
import json
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

INSIGHT_PROMPT = """\
You are an Insight Agent — an expert data analyst AI.

You are given:
1. The user's original question
2. SQL query results (raw data)
3. Processed data analysis results
4. Focus areas to analyze

Your task:
- Identify key patterns, trends, and anomalies
- Explain WHY the patterns exist (hypothesize with data support)
- Highlight important numbers and percentages
- Be specific with data references
- Structure your response clearly

Provide your insights as a well-structured analysis with clear sections.
Do NOT use markdown fences. Use plain text with clear headings.
"""


def run_insight_agent(
    llm,
    question: str,
    sql_results: list[dict],
    processed_data: dict,
    focus_areas: list[str],
) -> str:
    """Generate insights from the analysis results."""
    logger.info("Insight Agent analyzing with focus: %s", focus_areas)

    # Summarize data for context (truncate large results)
    sql_summary = _summarize_sql_results(sql_results)
    proc_summary = _summarize_processed(processed_data)

    messages = [
        SystemMessage(content=INSIGHT_PROMPT),
        HumanMessage(content=f"""
User Question: {question}

SQL Results Summary:
{sql_summary}

Processed Data:
{proc_summary}

Focus Areas: {', '.join(focus_areas)}

Provide detailed, data-backed insights.
"""),
    ]

    response = llm.invoke(messages)
    insight = response.content.strip()
    logger.info("Insight Agent produced %d chars of analysis", len(insight))
    return insight


def _summarize_sql_results(sql_results: list[dict], max_rows: int = 30) -> str:
    lines = []
    for i, res in enumerate(sql_results):
        r = res.get("result", {})
        if "error" in r:
            lines.append(f"Query {i+1}: ERROR - {r['error']}")
            continue
        cols = r.get("columns", [])
        rows = r.get("rows", [])[:max_rows]
        lines.append(f"Query {i+1} ({r.get('row_count', 0)} rows): {res.get('query', '')}")
        lines.append(f"  Columns: {cols}")
        for row in rows[:10]:
            lines.append(f"  {row}")
        if len(rows) > 10:
            lines.append(f"  ... ({len(rows) - 10} more rows)")
    return "\n".join(lines)


def _summarize_processed(processed_data: dict) -> str:
    parts = []
    for key, val in processed_data.items():
        val_str = json.dumps(val, default=str) if not isinstance(val, str) else val
        if len(val_str) > 500:
            val_str = val_str[:500] + "..."
        parts.append(f"{key}: {val_str}")
    return "\n".join(parts)
