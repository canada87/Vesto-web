from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import json
from app.database import get_db
from app.models.db import OutfitLog, User
from app.auth import get_current_user
from app.schemas import OutfitLogCreate, OutfitLogResponse

router = APIRouter()


def _log_to_response(log: OutfitLog) -> OutfitLogResponse:
    return OutfitLogResponse(
        id=log.id,
        user_id=log.user_id,
        date=log.date,
        item_ids=json.loads(log.item_ids),
        occasion=log.occasion,
        weather=log.weather,
        notes=log.notes,
        created_at=log.created_at,
    )


@router.get("", response_model=list[OutfitLogResponse])
def list_logs(
    days: Optional[int] = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cutoff = datetime.utcnow() - timedelta(days=days)
    logs = (
        db.query(OutfitLog)
        .filter(OutfitLog.user_id == current_user.id, OutfitLog.date >= cutoff)
        .order_by(OutfitLog.date.desc())
        .all()
    )
    return [_log_to_response(l) for l in logs]


@router.post("", response_model=OutfitLogResponse, status_code=201)
def create_log(
    body: OutfitLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = OutfitLog(
        user_id=current_user.id,
        date=body.date,
        item_ids=json.dumps(body.item_ids),
        occasion=body.occasion,
        weather=body.weather,
        notes=body.notes,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return _log_to_response(log)


@router.get("/{log_id}", response_model=OutfitLogResponse)
def get_log(
    log_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = db.query(OutfitLog).filter(
        OutfitLog.id == log_id,
        OutfitLog.user_id == current_user.id,
    ).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log non trovato")
    return _log_to_response(log)


@router.delete("/{log_id}", status_code=204)
def delete_log(
    log_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = db.query(OutfitLog).filter(
        OutfitLog.id == log_id,
        OutfitLog.user_id == current_user.id,
    ).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log non trovato")
    db.delete(log)
    db.commit()
