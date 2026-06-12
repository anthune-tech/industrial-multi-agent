from fastapi import APIRouter
from pydantic import BaseModel

from agents.reasoner import ReasonerAgent
from agents.worker import WorkerAgent
from tools.oee import calculate_oee
from tools.data_io import read_plant_data
from tools.analytics import analyze_trend
from tools.knowledge import query_results_db, save_to_results_db
from tools.troubleshoot import detect_anomalies, generate_report, save_troubleshoot_session

router = APIRouter()


class AnalyzeRequest(BaseModel):
    machine_id: str
    query: str


class TroubleshootRequest(BaseModel):
    machine_id: str
    problem: str


def _build_crew(task_agent):
    from crewai import Crew, Process, Task

    reasoner = ReasonerAgent().get_agent()

    analysis_task = Task(
        description=(
            "Analyze the plant data and provide a comprehensive response "
            "based on the user's request."
        ),
        expected_output="A structured analysis with data, insights, and recommendations.",
        agent=reasoner,
    )

    crew = Crew(
        agents=[reasoner, task_agent],
        tasks=[analysis_task],
        process=Process.hierarchical,
        manager_agent=reasoner,
        verbose=True,
    )
    return crew


@router.post("/analyze")
async def analyze(req: AnalyzeRequest):
    tools = [
        read_plant_data,
        calculate_oee,
        analyze_trend,
        query_results_db,
        save_to_results_db,
        detect_anomalies,
        generate_report,
    ]

    worker = WorkerAgent(tools=tools).get_agent()
    crew = _build_crew(worker)

    result = crew.kickoff(inputs={
        "machine_id": req.machine_id,
        "query": req.query,
    })
    return {"result": str(result)}


@router.post("/troubleshoot")
async def troubleshoot(req: TroubleshootRequest):
    tools = [
        read_plant_data,
        calculate_oee,
        query_results_db,
        save_to_results_db,
        save_troubleshoot_session,
    ]

    worker = WorkerAgent(tools=tools).get_agent()
    reasoner = ReasonerAgent().get_agent()

    from crewai import Crew, Task

    task = Task(
        description=(
            f"Troubleshoot the following issue on machine {req.machine_id}: {req.problem}. "
            "Use available data and knowledge to diagnose the root cause "
            "and recommend a resolution."
        ),
        expected_output="A diagnosis and resolution for the problem.",
        agent=reasoner,
    )

    crew = Crew(
        agents=[reasoner, worker],
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
