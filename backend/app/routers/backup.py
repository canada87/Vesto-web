from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import json
from datetime import datetime
from app.database import get_db
from app.models.db import ClothingItem, OutfitLog, TripPlan, AppSetting, User
from app.auth import get_current_user

router = APIRouter()


@router.get("/export")
def export_backup(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = db.query(ClothingItem).filter(ClothingItem.user_id == current_user.id).all()
    logs = db.query(OutfitLog).filter(OutfitLog.user_id == current_user.id).all()
    trips = db.query(TripPlan).filter(TripPlan.user_id == current_user.id).all()
    settings = db.query(AppSetting).filter(AppSetting.user_id == current_user.id).all()

    def serialize_dt(dt):
        return dt.isoformat() if dt else None

    data = {
        "version": "2.0",
        "exported_at": datetime.utcnow().isoformat(),
        "username": current_user.username,
        "items": [
            {
                "id": i.id, "name": i.name, "category": i.category,
                "age_years": i.age_years, "weight": i.weight,
                "condition": i.condition, "like_score": i.like_score,
                "usage_type": i.usage_type, "seasons": json.loads(i.seasons),
                "status": i.status, "location": i.location,
                "color": i.color, "notes": i.notes,
                "local_photo_path": i.local_photo_path,
                "created_at": serialize_dt(i.created_at),
                "updated_at": serialize_dt(i.updated_at),
            }
            for i in items
        ],
        "outfit_logs": [
            {
                "id": l.id, "date": serialize_dt(l.date),
                "item_ids": json.loads(l.item_ids),
                "occasion": l.occasion, "weather": l.weather,
                "notes": l.notes, "created_at": serialize_dt(l.created_at),
            }
            for l in logs
        ],
        "trips": [
            {
                "id": t.id, "name": t.name, "destination": t.destination,
                "start_date": serialize_dt(t.start_date),
                "end_date": serialize_dt(t.end_date),
                "trip_type": t.trip_type,
                "item_ids": json.loads(t.item_ids),
                "duration_only": t.duration_only,
                "custom_duration_days": t.custom_duration_days,
                "created_at": serialize_dt(t.created_at),
            }
            for t in trips
        ],
        "settings": [
            {"key": s.key, "value": s.value}
            for s in settings
        ],
    }
    return JSONResponse(
        content=data,
        headers={"Content-Disposition": "attachment; filename=vesto-backup.json"},
    )


@router.post("/import", status_code=200)
async def import_backup(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = await file.read()
    data = json.loads(content)

    # Cancella tutti i dati attuali dell'utente
    db.query(ClothingItem).filter(ClothingItem.user_id == current_user.id).delete()
    db.query(OutfitLog).filter(OutfitLog.user_id == current_user.id).delete()
    db.query(TripPlan).filter(TripPlan.user_id == current_user.id).delete()
    db.query(AppSetting).filter(AppSetting.user_id == current_user.id).delete()
    db.commit()

    def parse_dt(s):
        if not s:
            return None
        return datetime.fromisoformat(s)

    for i in data.get("items", []):
        item = ClothingItem(
            id=i.get("id"),
            user_id=current_user.id,
            name=i["name"],
            category=i["category"],
            age_years=i.get("age_years", 0),
            weight=i.get("weight", "medium"),
            condition=i.get("condition", "good"),
            like_score=i.get("like_score", 3),
            usage_type=i.get("usage_type", "both"),
            seasons=json.dumps(i.get("seasons", [])),
            status=i.get("status", "inWardrobe"),
            location=i.get("location", "Casa"),
            color=i.get("color"),
            notes=i.get("notes"),
            local_photo_path=i.get("local_photo_path"),
            created_at=parse_dt(i.get("created_at")),
            updated_at=parse_dt(i.get("updated_at")),
        )
        db.add(item)

    for l in data.get("outfit_logs", []):
        log = OutfitLog(
            id=l.get("id"),
            user_id=current_user.id,
            date=parse_dt(l["date"]),
            item_ids=json.dumps(l.get("item_ids", [])),
            occasion=l["occasion"],
            weather=l.get("weather"),
            notes=l.get("notes"),
            created_at=parse_dt(l.get("created_at")),
        )
        db.add(log)

    for t in data.get("trips", []):
        trip = TripPlan(
            id=t.get("id"),
            user_id=current_user.id,
            name=t["name"],
            destination=t.get("destination"),
            start_date=parse_dt(t.get("start_date")),
            end_date=parse_dt(t.get("end_date")),
            trip_type=t.get("trip_type", "both"),
            item_ids=json.dumps(t.get("item_ids", [])),
            duration_only=t.get("duration_only", False),
            custom_duration_days=t.get("custom_duration_days"),
            created_at=parse_dt(t.get("created_at")),
        )
        db.add(trip)

    for s in data.get("settings", []):
        setting = AppSetting(
            user_id=current_user.id,
            key=s["key"],
            value=s["value"],
        )
        db.add(setting)

    db.commit()
    return {"message": "Backup importato con successo"}
