from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func

from db.connection import Base


class OeeSnapshot(Base):
    __tablename__ = "oee_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    shift = Column(String)
    availability = Column(Float)
    performance = Column(Float)
    quality = Column(Float)
    oee = Column(Float)
    run_minutes = Column(Integer)
    downtime_minutes = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MachineStatus(Base):
    __tablename__ = "machine_status"

    machine_id = Column(String, primary_key=True)
    status = Column(String)
    last_seen = Column(DateTime(timezone=True))
    error_code = Column(String)
    oee_current = Column(Float)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class AnalyticsResult(Base):
    __tablename__ = "analytics_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_type = Column(String)
    machine_id = Column(String)
    parameters = Column(JSON)
    result = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Alarm(Base):
    __tablename__ = "alarms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String)
    severity = Column(String)
    message = Column(String)
    details = Column(JSON)
    triggered_at = Column(DateTime(timezone=True))
    acknowledged = Column(Boolean, default=False)


class TroubleshootSession(Base):
    __tablename__ = "troubleshoot_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String)
    problem = Column(Text)
    diagnosis = Column(Text)
    resolution = Column(Text)
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
