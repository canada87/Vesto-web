from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from app.database import get_db
from app.models.db import TripPlan, User
from app.auth import get_current_user
from app.schemas import TripPlanCreate, TripPlanResponse, TripItemsUpdate

router = APIRouter()


def _trip_to_response(trip: TripPlan) -> TripPlanResponse:
    return TripPlanResponse(
        id=trip.id,
        user_id=trip.user_id,
        name=trip.name,
        destination=trip.destination,
        start_date=trip.start_date,
        end_date=trip.end_date,
        trip_type=trip.trip_type,
        duration_only=trip.duration_only,
        custom_duration_days=trip.custom_duration_days,
        item_ids=json.loads(trip.item_ids),
        locked_item_ids=json.loads(trip.locked_item_ids or "[]"),
        created_at=trip.created_at,
    )


@router.get("", response_model=list[TripPlanResponse])
def list_trips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trips = (
        db.query(TripPlan)
        .filter(TripPlan.user_id == current_user.id)
        .order_by(TripPlan.created_at.desc())
        .all()
    )
    return [_trip_to_response(t) for t in trips]


@router.post("", response_model=TripPlanResponse, status_code=201)
def create_trip(
    body: TripPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = TripPlan(
        user_id=current_user.id,
        name=body.name,
        destination=body.destination,
        start_date=body.start_date,
        end_date=body.end_date,
        trip_type=body.trip_type,
        duration_only=body.duration_only,
        custom_duration_days=body.custom_duration_days,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return _trip_to_response(trip)


@router.get("/{trip_id}", response_model=TripPlanResponse)
def get_trip(
    trip_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = db.query(TripPlan).filter(
        TripPlan.id == trip_id,
        TripPlan.user_id == current_user.id,
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Viaggio non trovato")
    return _trip_to_response(trip)


@router.put("/{trip_id}", response_model=TripPlanResponse)
def update_trip(
    trip_id: str,
    body: TripPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = db.query(TripPlan).filter(
        TripPlan.id == trip_id,
        TripPlan.user_id == current_user.id,
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Viaggio non trovato")
    trip.name = body.name
    trip.destination = body.destination
    trip.start_date = body.start_date
    trip.end_date = body.end_date
    trip.trip_type = body.trip_type
    trip.duration_only = body.duration_only
    trip.custom_duration_days = body.custom_duration_days
    db.commit()
    db.refresh(trip)
    return _trip_to_response(trip)


@router.put("/{trip_id}/items", response_model=TripPlanResponse)
def update_trip_items(
    trip_id: str,
    body: TripItemsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = db.query(TripPlan).filter(
        TripPlan.id == trip_id,
        TripPlan.user_id == current_user.id,
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Viaggio non trovato")
    trip.item_ids = json.dumps(body.item_ids)
    trip.locked_item_ids = json.dumps(body.locked_item_ids)
    db.commit()
    db.refresh(trip)
    return _trip_to_response(trip)


@router.delete("/{trip_id}", status_code=204)
def delete_trip(
    trip_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = db.query(TripPlan).filter(
        TripPlan.id == trip_id,
        TripPlan.user_id == current_user.id,
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Viaggio non trovato")
    db.delete(trip)
    db.commit()
