import os
from fastapi import APIRouter
from pydantic import BaseModel

from agents.reasoner import ReasonerAgent
from agents.worker import WorkerAgent
from tools.oee import calculate_oee
from tools.data_io import read_plant_data
from tools.analytics import analyze_trend
from tools.knowledge import query_results_db, save_to_results_db
from tools.knowledge_base_tool import query_knowledge_base
from tools.troubleshoot import detect_anomalies, generate_report, save_troubleshoot_session

router = APIRouter()


class AnalyzeRequest(BaseModel):
    machine_id: str
    query: str


class TroubleshootRequest(BaseModel):
    machine_id: str
    problem: str


def _llm_config(provider: str) -> dict:
    if provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            return {
                "provider": "anthropic",
                "api_key": api_key,
                "model": "claude-sonnet-4-20250514",
            }
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return {
                "provider": "openai",
                "api_key": api_key,
                "model": "gpt-4o-mini",
            }
    return {}


def _build_crew(task_agent):
    from crewai import Crew, Process, Task

    reasoner = ReasonerAgent(llm_config=_llm_config("anthropic")).get_agent()

    analysis_task = Task(
        description=(
            "Analyze the plant data for machine {{machine_id}} and provide "
            "a comprehensive response based on the user's query: {{query}}.\n\n"
            "Use the worker agent to fetch data, calculate OEE, detect anomalies, "
            "and query the knowledge base as needed.\n\n"
            "Provide a structured analysis with data, insights, and recommendations."
        ),
        expected_output="A structured analysis with data, insights, and recommendations.",
        agent=reasoner,
    )

    crew = Crew(
        agents=[task_agent],
        tasks=[analysis_task],
        process=Process.hierarchical,
        manager_agent=reasoner,
        verbose=True,
    )
    return crew


ALL_TOOLS = [
    read_plant_data,
    calculate_oee,
    analyze_trend,
    query_results_db,
    save_to_results_db,
    query_knowledge_base,
    detect_anomalies,
    generate_report,
    save_troubleshoot_session,
]


@router.post("/analyze")
async def analyze(req: AnalyzeRequest):
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        return {"error": "No LLM API key configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env"}
    worker = WorkerAgent(
        tools=ALL_TOOLS,
        llm_config=_llm_config("openai"),
    ).get_agent()

    crew = _build_crew(worker)
    result = crew.kickoff(inputs={
        "machine_id": req.machine_id,
        "query": req.query,
    })
    return {"result": str(result)}


@router.post("/troubleshoot")
async def troubleshoot(req: TroubleshootRequest):
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        return {"error": "No LLM API key configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env"}
    from crewai import Crew, Task

    worker = WorkerAgent(
        tools=ALL_TOOLS,
        llm_config=_llm_config("openai"),
    ).get_agent()
    reasoner = ReasonerAgent(llm_config=_llm_config("anthropic")).get_agent()

    task = Task(
        description=(
            "Troubleshoot the following issue on machine {{machine_id}}: {{problem}}.\n\n"
            "Use the worker agent to:\n"
            "1. Query the knowledge base for relevant troubleshooting guides\n"
            "2. Check machine status and recent OEE data\n"
            "3. Detect anomalies in the machine's metrics\n"
            "4. Generate a report with diagnosis and resolution\n\n"
            "Provide a structured diagnosis and resolution."
        ),
        expected_output="A diagnosis and resolution for the problem.",
        agent=reasoner,
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
