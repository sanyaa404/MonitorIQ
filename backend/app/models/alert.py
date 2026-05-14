# backend/app/models/alert.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, func
from app.core.database import Base

class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    metric = Column(String, nullable=False)   # e.g. "cpu_percent_total"
    operator = Column(String, nullable=False) # "gt", "lt", "gte", "lte"
    threshold = Column(Float, nullable=False)
    hostname = Column(String, nullable=True)  # None means all hosts
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AlertEvent(Base):
    __tablename__ = "alert_events"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, nullable=False)
    rule_name = Column(String, nullable=False)
    hostname = Column(String, nullable=False)
    metric = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    acknowledged = Column(Boolean, default=False)
    fired_at = Column(DateTime(timezone=True), server_default=func.now())