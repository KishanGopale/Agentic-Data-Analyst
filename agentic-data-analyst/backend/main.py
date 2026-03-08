"""FastAPI server for the Agentic Data Analyst."""
import logging
import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure backend dir is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))
load_dotenv()

import config
from workflows.agent_graph import run_analysis

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("server")

# --- LLM setup ---
_llm = None


def get_llm():
    global _llm
    if _llm is not None:
        return _llm

    if config.LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        _llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=config.GEMINI_API_KEY,
            temperature=0.2,
        )
    else:
        from langchain_community.chat_models import ChatOpenAI
        _llm = ChatOpenAI(
            model="gpt-4o",
            api_key=config.OPENAI_API_KEY,
            temperature=0.2,
        )
    return _llm


# --- Database init ---
def init_database():
    if not config.DATABASE_PATH.exists():
        logger.info("Database not found, generating sample data...")
        from data.generate_data import generate_rows, write_csv, load_sqlite
        rows = generate_rows()
        write_csv(rows)
        load_sqlite(rows)
        logger.info("Sample data generated.")
    else:
        logger.info("Database found at %s", config.DATABASE_PATH)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


# --- App ---
app = FastAPI(
    title="Agentic Data Analyst",
    description="Multi-agent AI data analysis system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve chart images
app.mount("/charts", StaticFiles(directory=str(config.CHARTS_DIR)), name="charts")
app.mount("/reports", StaticFiles(directory=str(config.REPORTS_DIR)), name="reports")


# --- Models ---
class AnalyzeRequest(BaseModel):
    question: str


class AnalyzeResponse(BaseModel):
    question: str
    understanding: str
    insight: str
    charts: list[dict]
    report_filename: str
    report_content: str
    messages: list[str]
    error: str


# --- Endpoints ---
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    if not req.question.strip():
        raise HTTPException(400, "Question cannot be empty")

    logger.info("Received analysis request: %s", req.question)

    try:
        llm = get_llm()
        result = run_analysis(llm, req.question)
    except Exception as e:
        logger.error("Analysis failed: %s", e, exc_info=True)
        raise HTTPException(500, f"Analysis failed: {e}")

    # Build chart URLs
    chart_list = []
    for c in result.get("charts", []):
        chart_list.append({
            "url": f"/charts/{c['chart_filename']}",
            "id": c.get("chart_id", ""),
            "filename": c.get("chart_filename", ""),
        })

    report = result.get("report", {})

    return AnalyzeResponse(
        question=req.question,
        understanding=result.get("plan", {}).get("understanding", ""),
        insight=result.get("insights", ""),
        charts=chart_list,
        report_filename=report.get("report_filename", ""),
        report_content=report.get("report_content", ""),
        messages=result.get("messages", []),
        error=result.get("error", ""),
    )


@app.get("/reports/{filename}")
async def get_report(filename: str):
    filepath = config.REPORTS_DIR / filename
    if not filepath.exists():
        raise HTTPException(404, "Report not found")
    return FileResponse(str(filepath), media_type="text/markdown", filename=filename)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=True)
