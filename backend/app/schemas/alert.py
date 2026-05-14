# backend/app/schemas/alert.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlertRuleCreate(BaseModel):
    name: str
    metric: str
    operator: str  # gt, lt, gte, lte
    threshold: float
    hostname: Optional[str] = None

class AlertRuleResponse(BaseModel):
    id: int
    name: str
    metric: str
    operator: str
    threshold: float
    hostname: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AlertEventResponse(BaseModel):
    id: int
    rule_name: str
    hostname: str
    metric: str
    value: float
    threshold: float
    acknowledged: bool
    fired_at: datetime

    class Config:
        from_attributes = True