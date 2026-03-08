"""SQL Agent — generates and executes SQL queries against the sales database."""
import logging
from langchain_core.messages import SystemMessage, HumanMessage

from tools.sql_tool import execute_sql, get_schema, get_sample_rows

logger = logging.getLogger(__name__)

SQL_AGENT_PROMPT = """\
You are a SQL Agent. You receive SQL queries to execute against a SQLite database.

Database schema:
{schema}

Sample rows:
{sample}

Your job:
1. Validate each query for correctness and safety (SELECT only).
2. Fix any syntax issues.
3. Return the corrected queries as a JSON list of strings.

Respond ONLY with a JSON list of SQL query strings. No markdown fences.
"""


def run_sql_agent(llm, queries: list[str]) -> list[dict]:
    """Validate queries with LLM, then execute them. Returns list of result dicts."""
    logger.info("SQL Agent executing %d queries", len(queries))

    schema = get_schema()
    sample = get_sample_rows()

    messages = [
        SystemMessage(content=SQL_AGENT_PROMPT.format(schema=schema, sample=sample)),
        HumanMessage(content=f"Queries to validate and fix:\n{queries}"),
    ]
    response = llm.invoke(messages)

    import json
    try:
        validated = json.loads(response.content.strip())
        if not isinstance(validated, list):
            validated = queries
    except json.JSONDecodeError:
        validated = queries

    results = []
    for q in validated:
        logger.info("Executing: %s", q)
        result = execute_sql.invoke({"query": q})
        results.append({"query": q, "result": result})

    return results
