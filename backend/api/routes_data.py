from fastapi import APIRouter, Query
from sqlalchemy import text

from db.connection import SessionLocal

router = APIRouter()


@router.get("/oee/latest")
async def get_latest_oee():
    db = SessionLocal()
    try:
        rows = db.execute(
            text("SELECT DISTINCT ON (machine_id) * FROM oee_snapshots ORDER BY machine_id, timestamp DESC")
        ).fetchall()
        return [dict(r._mapping) for r in rows]
    finally:
        db.close()


@router.get("/oee/history")
async def get_oee_history(machine_id: str = Query(...), limit: int = 100):
    db = SessionLocal()
    try:
        rows = db.execute(
            text("SELECT * FROM oee_snapshots WHERE machine_id = :mid ORDER BY timestamp DESC LIMIT :lim"),
            {"mid": machine_id, "lim": limit},
        ).fetchall()
        return [dict(r._mapping) for r in rows]
    finally:
        db.close()


@router.get("/machines")
async def get_machine_status():
    db = SessionLocal()
    try:
        rows = db.execute(text("SELECT * FROM machine_status")).fetchall()
        return [dict(r._mapping) for r in rows]
    finally:
        db.close()


@router.get("/alarms")
async def get_alarms(limit: int = 50):
    db = SessionLocal()
    try:
        rows = db.execute(
            text("SELECT * FROM alarms ORDER BY triggered_at DESC LIMIT :lim"),
            {"lim": limit},
        ).fetchall()
        return [dict(r._mapping) for r in rows]
    finally:
        db.close()


@router.get("/analytics")
async def get_analytics_results(limit: int = 50):
    db = SessionLocal()
    try:
        rows = db.execute(
            text("SELECT * FROM analytics_results ORDER BY created_at DESC LIMIT :lim"),
            {"lim": limit},
        ).fetchall()
        return [dict(r._mapping) for r in rows]
    finally:
        db.close()
