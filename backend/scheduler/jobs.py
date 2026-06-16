import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def start_scheduler():
    """Start scheduled agent runs every 5 minutes with immediate first run."""
    from tools.oee import calculate_oee
    from tools.knowledge import save_to_results_db

    def run_agent():
        machines = ["LINE-01", "LINE-02", "LINE-03", "LINE-04", "LINE-05"]
        for mid in machines:
            try:
                oee = calculate_oee.invoke({
                    "machine_id": mid,
                    "shift": "auto",
                    "date": "today",
                })
                save_to_results_db.invoke({"table": "oee_snapshots", "data": oee})
                logger.info(f"OEE snapshot saved for {mid}")
            except Exception as e:
                logger.error(f"OEE snapshot failed for {mid}: {e}")

    scheduler.add_job(
        run_agent, "interval", minutes=5, id="agent_oee",
        next_run_time=datetime.now(),
    )
    scheduler.start()
    logger.info("Scheduler started with immediate OEE run")