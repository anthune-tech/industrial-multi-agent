from apscheduler.schedulers.background import BackgroundScheduler


scheduler = BackgroundScheduler()


def start_scheduler():
    """Start scheduled agent runs every 5 minutes."""
    from agents.reasoner import ReasonerAgent
    from agents.worker import WorkerAgent
    from tools.oee import calculate_oee
    from tools.data_io import read_plant_data
    from tools.analytics import analyze_trend as at
    from tools.knowledge import save_to_results_db as save

    def run_agent():
        machines = ["LINE-01", "LINE-02", "LINE-03", "LINE-04", "LINE-05"]
        for mid in machines:
            try:
                oee = calculate_oee(mid, "auto", "today")
                save("oee_snapshots", oee)
            except Exception:
                pass

    scheduler.add_job(run_agent, "interval", minutes=5, id="agent_oee")
    scheduler.start()
