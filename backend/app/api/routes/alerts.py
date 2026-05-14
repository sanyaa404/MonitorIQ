# backend/app/api/routes/alerts.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.alert import AlertRule, AlertEvent
from app.schemas.alert import AlertRuleCreate, AlertRuleResponse, AlertEventResponse
from typing import List

router = APIRouter()

@router.post("/rules", response_model=AlertRuleResponse, status_code=201)
def create_rule(rule_in: AlertRuleCreate, db: Session = Depends(get_db)):
    rule = AlertRule(**rule_in.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

@router.get("/rules", response_model=List[AlertRuleResponse])
def list_rules(db: Session = Depends(get_db)):
    return db.query(AlertRule).filter(AlertRule.is_active == True).all()

@router.get("/events", response_model=List[AlertEventResponse])
def list_events(db: Session = Depends(get_db)):
    return db.query(AlertEvent).order_by(AlertEvent.fired_at.desc()).limit(50).all()

@router.patch("/events/{event_id}/acknowledge")
def acknowledge_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(AlertEvent).filter(AlertEvent.id == event_id).first()
    if not event:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Event not found")
    event.acknowledged = True
    db.commit()
    return {"status": "acknowledged"}