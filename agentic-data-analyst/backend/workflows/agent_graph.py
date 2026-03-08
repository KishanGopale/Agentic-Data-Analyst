"""LangGraph StateGraph workflow orchestrating all agents."""
import logging
import time
from typing import Any, TypedDict

from langgraph.graph import StateGraph, END

from agents.planner_agent import run_planner
from agents.sql_agent import run_sql_agent
from agents.data_agent import run_data_agent
from agents.visualization_agent import run_visualization_agent
from agents.insight_agent import run_insight_agent
from agents.report_agent import run_report_agent
from memory.vector_store import retrieve_similar, store_analysis

logger = logging.getLogger(__name__)


class AnalysisState(TypedDict):
    question: str
    plan: dict
    sql_results: list[dict]
    processed_data: dict
    charts: list[dict]
    insights: str
    report: dict
    messages: list[str]  # agent communication log
    error: str


def _log_msg(state: AnalysisState, agent: str, msg: str):
    state["messages"].append(f"[{agent}] {msg}")
    logger.info("[%s] %s", agent, msg)


def planner_node(state: AnalysisState, llm) -> AnalysisState:
    _log_msg(state, "Planner", f"Analyzing question: {state['question']}")

    # Retrieve memory context
    similar = retrieve_similar(state["question"])
    memory_ctx = ""
    if similar:
        memory_ctx = "\n".join(s["document"] for s in similar)
        _log_msg(state, "Planner", f"Found {len(similar)} similar past analyses")

    try:
        plan = run_planner(llm, state["question"], memory_ctx)
        state["plan"] = plan
        _log_msg(state, "Planner", f"Plan ready: {plan.get('understanding', '')}")
    except Exception as e:
        state["error"] = f"Planner failed: {e}"
        _log_msg(state, "Planner", f"ERROR: {e}")

    return state


def sql_node(state: AnalysisState, llm) -> AnalysisState:
    if state.get("error"):
        return state

    queries = state["plan"].get("sql_queries", ["SELECT * FROM sales"])
    _log_msg(state, "SQL", f"Executing {len(queries)} queries")

    try:
        results = run_sql_agent(llm, queries)
        state["sql_results"] = results
        total_rows = sum(r["result"].get("row_count", 0) for r in results if "error" not in r.get("result", {}))
        _log_msg(state, "SQL", f"Retrieved {total_rows} total rows")
    except Exception as e:
        state["error"] = f"SQL Agent failed: {e}"
        _log_msg(state, "SQL", f"ERROR: {e}")

    return state


def data_node(state: AnalysisState) -> AnalysisState:
    if state.get("error"):
        return state

    ops = state["plan"].get("processing_ops", ["describe"])
    _log_msg(state, "Data", f"Processing with {len(ops)} operations")

    try:
        processed = run_data_agent(state["sql_results"], ops)
        state["processed_data"] = processed
        _log_msg(state, "Data", f"Produced {len(processed)} analysis results")
    except Exception as e:
        state["error"] = f"Data Agent failed: {e}"
        _log_msg(state, "Data", f"ERROR: {e}")

    return state


def viz_node(state: AnalysisState) -> AnalysisState:
    if state.get("error"):
        return state

    specs = state["plan"].get("chart_specs", [])
    _log_msg(state, "Visualization", f"Generating {len(specs)} charts")

    try:
        charts = run_visualization_agent(state["sql_results"], specs)
        state["charts"] = charts
        _log_msg(state, "Visualization", f"Generated {len(charts)} charts")
    except Exception as e:
        state["error"] = f"Visualization Agent failed: {e}"
        _log_msg(state, "Visualization", f"ERROR: {e}")

    return state


def insight_node(state: AnalysisState, llm) -> AnalysisState:
    if state.get("error"):
        return state

    focus = state["plan"].get("focus_areas", ["general analysis"])
    _log_msg(state, "Insight", "Analyzing patterns and trends")

    try:
        insights = run_insight_agent(
            llm, state["question"], state["sql_results"],
            state["processed_data"], focus,
        )
        state["insights"] = insights
        _log_msg(state, "Insight", f"Generated {len(insights)} chars of insights")
    except Exception as e:
        state["error"] = f"Insight Agent failed: {e}"
        _log_msg(state, "Insight", f"ERROR: {e}")

    return state


def report_node(state: AnalysisState, llm) -> AnalysisState:
    if state.get("error"):
        return state

    _log_msg(state, "Report", "Generating final report")

    try:
        report = run_report_agent(
            llm, state["question"], state["insights"],
            state["charts"], state["processed_data"],
        )
        state["report"] = report
        _log_msg(state, "Report", f"Report saved: {report['report_filename']}")

        # Store in memory for future context
        store_analysis(
            state["question"],
            state["insights"][:500],
            {"report_id": report["report_id"]},
        )
    except Exception as e:
        state["error"] = f"Report Agent failed: {e}"
        _log_msg(state, "Report", f"ERROR: {e}")

    return state


def build_graph(llm):
    """Build and compile the LangGraph agent workflow."""

    graph = StateGraph(AnalysisState)

    # Add nodes with LLM binding
    graph.add_node("planner", lambda s: planner_node(s, llm))
    graph.add_node("sql", lambda s: sql_node(s, llm))
    graph.add_node("data", lambda s: data_node(s))
    graph.add_node("visualization", lambda s: viz_node(s))
    graph.add_node("insight", lambda s: insight_node(s, llm))
    graph.add_node("reporter", lambda s: report_node(s, llm))

    # Define edges: linear pipeline
    graph.set_entry_point("planner")
    graph.add_edge("planner", "sql")
    graph.add_edge("sql", "data")
    graph.add_edge("data", "visualization")
    graph.add_edge("visualization", "insight")
    graph.add_edge("insight", "reporter")
    graph.add_edge("reporter", END)

    return graph.compile()


def run_analysis(llm, question: str) -> AnalysisState:
    """Run the full analysis pipeline."""
    logger.info("Starting analysis for: %s", question)
    start = time.time()

    app = build_graph(llm)

    initial_state: AnalysisState = {
        "question": question,
        "plan": {},
        "sql_results": [],
        "processed_data": {},
        "charts": [],
        "insights": "",
        "report": {},
        "messages": [],
        "error": "",
    }

    result = app.invoke(initial_state)

    elapsed = time.time() - start
    logger.info("Analysis complete in %.2fs", elapsed)
    result["messages"].append(f"[System] Analysis completed in {elapsed:.2f}s")

    return result
