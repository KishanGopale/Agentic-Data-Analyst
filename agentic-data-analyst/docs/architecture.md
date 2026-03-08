# Architecture

## System Overview

The Agentic Data Analyst uses a **multi-agent pipeline** orchestrated by LangGraph's StateGraph. Each agent has a specific role, its own prompt, and access to dedicated tools.

## Data Flow

```
1. User submits a natural language question via React UI
2. FastAPI receives the request at POST /analyze
3. LangGraph StateGraph executes the agent pipeline:

   Planner Agent
       ↓ (creates analysis plan)
   SQL Agent
       ↓ (executes queries, returns data)
   Data Agent
       ↓ (processes with pandas)
   Visualization Agent
       ↓ (generates charts)
   Insight Agent
       ↓ (LLM explains patterns)
   Report Agent
       ↓ (produces markdown report)

4. Results returned to frontend with charts, insights, and report
```

## State Schema

All agents share an `AnalysisState` TypedDict:

| Field | Type | Description |
|-------|------|-------------|
| question | str | Original user question |
| plan | dict | Planner output: queries, ops, chart specs |
| sql_results | list[dict] | Query results from SQL agent |
| processed_data | dict | Pandas processing results |
| charts | list[dict] | Chart file paths and metadata |
| insights | str | LLM-generated analysis text |
| report | dict | Report content and metadata |
| messages | list[str] | Agent communication log |
| error | str | Error message if any agent fails |

## Memory System

ChromaDB vector store persists analysis summaries. When a new question arrives, the Planner Agent retrieves similar past analyses to provide context and improve responses over time.

## Tool System

| Tool | Agent | Purpose |
|------|-------|---------|
| execute_sql | SQL Agent | Run SELECT queries on SQLite |
| process_data | Data Agent | Pandas operations (group, sort, trend) |
| generate_chart | Viz Agent | Create matplotlib/plotly charts |

## Error Handling

- Each agent node checks for prior errors in state and short-circuits
- All agent operations are wrapped in try/except
- Errors are logged and propagated through the state
- The API returns errors alongside any partial results

## Configuration

Environment-based configuration via `.env`:
- LLM provider and API key
- Model selection
- CORS origins
- Server host/port
