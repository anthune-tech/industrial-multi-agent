import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from agents.reasoner import ReasonerAgent
from agents.worker import WorkerAgent
from tools.oee import calculate_oee
from tools.data_io import read_plant_data
from tools.analytics import analyze_trend
from tools.knowledge import query_results_db, save_to_results_db, query_knowledge_base
from tools.troubleshoot import detect_anomalies, generate_report, save_troubleshoot_session
from tools.adapt import adapt

def _llm_model() -> str:
    model = os.getenv("LLM_MODEL", "qwen3:4b")
    if "/" not in model:
        model = f"ollama/{model}"
    return model

app = FastAPI(title="Agent-Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    machine_id: str
    query: str


class TroubleshootRequest(BaseModel):
    machine_id: str
    problem: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    from crewai import Crew, Process, Task

    llm = _llm_model()
    reasoner = ReasonerAgent(llm=llm).get_agent()
    tools = [adapt(t) for t in [
        read_plant_data,
        calculate_oee,
        analyze_trend,
        query_results_db,
        save_to_results_db,
        detect_anomalies,
        generate_report,
        query_knowledge_base,
    ]]
    worker = WorkerAgent(llm=llm, tools=tools).get_agent()

    task = Task(
        description=(
            "Analyze the plant data and provide a comprehensive response "
            "based on the user's request."
        ),
        expected_output="A structured analysis with data, insights, and recommendations.",
    )

    crew = Crew(
        agents=[worker],
        tasks=[task],
        process=Process.hierarchical,
        manager_agent=reasoner,
        verbose=True,
    )

    result = crew.kickoff(inputs={
        "machine_id": req.machine_id,
        "query": req.query,
    })
    return {"result": str(result)}


@app.post("/troubleshoot")
async def troubleshoot(req: TroubleshootRequest):
    from crewai import Crew, Task

    llm = _llm_model()
    reasoner = ReasonerAgent(llm=llm).get_agent()
    tools = [adapt(t) for t in [
        read_plant_data,
        calculate_oee,
        query_results_db,
        save_to_results_db,
        save_troubleshoot_session,
        query_knowledge_base,
    ]]
    worker = WorkerAgent(llm=llm, tools=tools).get_agent()

    task = Task(
        description=(
            f"Troubleshoot the following issue on machine {req.machine_id}: {req.problem}. "
            "Use available data and knowledge to diagnose the root cause "
            "and recommend a resolution."
        ),
        expected_output="A diagnosis and resolution for the problem.",
    )

    crew = Crew(
        agents=[worker],
        tasks=[task],
        process=Process.hierarchical,
        manager_agent=reasoner,
        verbose=True,
    )

    result = crew.kickoff(inputs={
        "machine_id": req.machine_id,
        "problem": req.problem,
    })
    return {"result": str(result)}
