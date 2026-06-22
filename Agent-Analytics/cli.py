"""CLI for Agent-Analytics: analyze plant data, troubleshoot, seed data, serve API."""
import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def cmd_seed(args):
    from db.connection import init_db
    from ingestion.ingest import seed_sample_data

    init_db()
    count = seed_sample_data()
    print(f"Seeded {count} rows of sample data.")


def _llm_model() -> str:
    model = os.getenv("LLM_MODEL", "qwen3:4b")
    if "/" not in model:
        model = f"ollama/{model}"
    return model


def cmd_analyze(args):
    from agents.reasoner import ReasonerAgent
    from agents.worker import WorkerAgent
    from crewai import Crew, Process, Task
    from tools.analytics import analyze_trend
    from tools.data_io import read_plant_data
    from tools.knowledge import query_knowledge_base, query_results_db, save_to_results_db
    from tools.oee import calculate_oee
    from tools.troubleshoot import detect_anomalies, generate_report
    from tools.adapt import adapt

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
        verbose=args.verbose,
    )

    result = crew.kickoff(inputs={
        "machine_id": args.machine_id,
        "query": args.query,
    })
    print(result)


def cmd_troubleshoot(args):
    from agents.reasoner import ReasonerAgent
    from agents.worker import WorkerAgent
    from crewai import Crew, Process, Task
    from tools.data_io import read_plant_data
    from tools.knowledge import query_knowledge_base, query_results_db, save_to_results_db
    from tools.oee import calculate_oee
    from tools.troubleshoot import save_troubleshoot_session
    from tools.adapt import adapt

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
            f"Troubleshoot the following issue on machine {args.machine_id}: {args.problem}. "
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
        verbose=args.verbose,
    )

    result = crew.kickoff(inputs={
        "machine_id": args.machine_id,
        "problem": args.problem,
    })
    print(result)


def cmd_serve(args):
    import uvicorn

    uvicorn.run("main:app", host=args.host, port=args.port, reload=args.reload)


def main():
    parser = argparse.ArgumentParser(
        description="Agent-Analytics — standalone industrial data analytics agent"
    )
    sub = parser.add_subparsers(dest="command")

    p_seed = sub.add_parser("seed", help="Seed database with 7 days of sample plant data")

    p_ana = sub.add_parser("analyze", help="Run a natural-language data analysis")
    p_ana.add_argument("machine_id", help="e.g. LINE-01")
    p_ana.add_argument("query", help="e.g. 'Show me OEE trend for last 7 days'")
    p_ana.add_argument("-v", "--verbose", action="store_true", help="Show CrewAI logs")

    p_tr = sub.add_parser("troubleshoot", help="Troubleshoot a machine problem")
    p_tr.add_argument("machine_id", help="e.g. LINE-03")
    p_tr.add_argument("problem", help="e.g. 'Conveyor motor overheating'")
    p_tr.add_argument("-v", "--verbose", action="store_true", help="Show CrewAI logs")

    p_sv = sub.add_parser("serve", help="Start the FastAPI server")
    p_sv.add_argument("--host", default="0.0.0.0")
    p_sv.add_argument("--port", type=int, default=8000)
    p_sv.add_argument("--reload", action="store_true", help="Auto-reload on code changes")

    args = parser.parse_args()

    if args.command == "seed":
        cmd_seed(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "troubleshoot":
        cmd_troubleshoot(args)
    elif args.command == "serve":
        cmd_serve(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
