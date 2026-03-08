"""Tool for executing SQL queries against the sales SQLite database."""
import sqlite3
import logging
from typing import Any

import pandas as pd
from langchain_core.tools import tool

from config import DATABASE_PATH

logger = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(str(DATABASE_PATH))


def get_schema() -> str:
    """Return the database schema as a string for LLM context."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table'")
    schemas = [row[0] for row in cur.fetchall() if row[0]]
    conn.close()
    return "\n".join(schemas)


def get_sample_rows(table: str = "sales", n: int = 5) -> str:
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT {n}", conn)
    conn.close()
    return df.to_string(index=False)


@tool
def execute_sql(query: str) -> dict[str, Any]:
    """Execute a read-only SQL query against the sales database and return the results.
    Only SELECT statements are allowed. Returns a dict with 'columns' and 'rows' keys."""
    query = query.strip().rstrip(";")
    if not query.upper().startswith("SELECT"):
        return {"error": "Only SELECT queries are allowed."}
    logger.info("Executing SQL: %s", query)
    try:
        conn = get_connection()
        df = pd.read_sql_query(query, conn)
        conn.close()
        return {
            "columns": list(df.columns),
            "rows": df.values.tolist(),
            "row_count": len(df),
        }
    except Exception as e:
        logger.error("SQL error: %s", e)
        return {"error": str(e)}
