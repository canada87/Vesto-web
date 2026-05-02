from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from app.database import get_db
from app.models.db import AppSetting, ClothingItem, OutfitLog, TripPlan, User
from app.auth import get_current_user
from app.schemas import LocationAdd, StatsResponse

router = APIRouter()

DEFAULT_LOCATIONS = ["Casa", "Ufficio", "Palestra"]
LOCATIONS_KEY = "locations"

TEST_ITEMS = [
    {"name": "Camicia Oxford Bianca", "category": "top", "weight": "light", "condition": "good", "like_score": 4, "usage_type": "work", "seasons": ["spring", "summer", "autumn"], "color": "bianco"},
    {"name": "Camicia a Quadri Flanella", "category": "top", "weight": "medium", "condition": "good", "like_score": 3, "usage_type": "personal", "seasons": ["autumn", "winter"], "color": "rosso/blu"},
    {"name": "T-Shirt Bianca Basic", "category": "top", "weight": "light", "condition": "worn", "like_score": 2, "usage_type": "both", "seasons": ["spring", "summer"], "color": "bianco"},
    {"name": "T-Shirt Nera", "category": "top", "weight": "light", "condition": "good", "like_score": 4, "usage_type": "both", "seasons": ["spring", "summer"], "color": "nero"},
    {"name": "Polo Navy", "category": "top", "weight": "light", "condition": "good", "like_score": 3, "usage_type": "both", "seasons": ["spring", "summer"], "color": "blu navy"},
    {"name": "Maglione Grigio Merino", "category": "top", "weight": "heavy", "condition": "good", "like_score": 5, "usage_type": "both", "seasons": ["autumn", "winter"], "color": "grigio"},
    {"name": "Felpa con Cappuccio", "category": "top", "weight": "medium", "condition": "good", "like_score": 4, "usage_type": "personal", "seasons": ["autumn", "winter"], "color": "antracite"},
    {"name": "Jeans Slim Blu", "category": "bottom", "weight": "medium", "condition": "good", "like_score": 5, "usage_type": "both", "seasons": ["spring", "summer", "autumn", "winter"], "color": "blu"},
    {"name": "Chino Beige", "category": "bottom", "weight": "light", "condition": "good", "like_score": 4, "usage_type": "work", "seasons": ["spring", "summer", "autumn"], "color": "beige"},
    {"name": "Pantaloni Grigi Formali", "category": "bottom", "weight": "medium", "condition": "good", "like_score": 3, "usage_type": "work", "seasons": ["autumn", "winter"], "color": "grigio"},
    {"name": "Shorts Cargo", "category": "bottom", "weight": "light", "condition": "good", "like_score": 3, "usage_type": "personal", "seasons": ["summer"], "color": "verde militare"},
    {"name": "Sneakers Bianche", "category": "shoes", "weight": "medium", "condition": "good", "like_score": 5, "usage_type": "personal", "seasons": ["spring", "summer", "autumn"], "color": "bianco"},
    {"name": "Scarpe Derby Marroni", "category": "shoes", "weight": "medium", "condition": "good", "like_score": 4, "usage_type": "work", "seasons": ["autumn", "winter"], "color": "marrone"},
    {"name": "Mocassini Cognac", "category": "shoes", "weight": "light", "condition": "good", "like_score": 4, "usage_type": "both", "seasons": ["spring", "summer"], "color": "cognac"},
    {"name": "Giubbotto Denim", "category": "outerwear", "weight": "medium", "condition": "good", "like_score": 4, "usage_type": "personal", "seasons": ["spring", "autumn"], "color": "blu"},
    {"name": "Cappotto Cammello", "category": "outerwear", "weight": "heavy", "condition": "good", "like_score": 5, "usage_type": "both", "seasons": ["autumn", "winter"], "color": "cammello"},
    {"name": "Piumino Nero", "category": "outerwear", "weight": "heavy", "condition": "good", "like_score": 3, "usage_type": "personal", "seasons": ["winter"], "color": "nero"},
    {"name": "Kit Sportivo Running", "category": "sportswear", "weight": "light", "condition": "good", "like_score": 4, "usage_type": "personal", "seasons": ["spring", "summer", "autumn"], "color": "grigio/neon"},
    {"name": "Cintura Pelle Marrone", "category": "accessory", "weight": "light", "condition": "good", "like_score": 3, "usage_type": "work", "seasons": ["spring", "summer", "autumn", "winter"], "color": "marrone"},
]


def _get_locations(db: Session, user_id: str) -> list[str]:
    setting = db.query(AppSetting).filter(
        AppSetting.user_id == user_id,
        AppSetting.key == LOCATIONS_KEY,
    ).first()
    if not setting:
        return list(DEFAULT_LOCATIONS)
    return json.loads(setting.value)


def _set_locations(db: Session, user_id: str, locations: list[str]):
    setting = db.query(AppSetting).filter(
        AppSetting.user_id == user_id,
        AppSetting.key == LOCATIONS_KEY,
    ).first()
    if setting:
        setting.value = json.dumps(locations)
    else:
        setting = AppSetting(user_id=user_id, key=LOCATIONS_KEY, value=json.dumps(locations))
        db.add(setting)
    db.commit()


@router.get("/locations", response_model=list[str])
def get_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_locations(db, current_user.id)


@router.post("/locations", response_model=list[str], status_code=201)
def add_location(
    body: LocationAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    locations = _get_locations(db, current_user.id)
    if body.name not in locations:
        locations.append(body.name)
        _set_locations(db, current_user.id, locations)
    return locations


@router.delete("/locations/{name}", response_model=list[str])
def delete_location(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    locations = _get_locations(db, current_user.id)
    if name in locations:
        locations.remove(name)
        _set_locations(db, current_user.id, locations)
    return locations


@router.get("/stats", response_model=StatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_items = db.query(ClothingItem).filter(ClothingItem.user_id == current_user.id).count()
    total_logs = db.query(OutfitLog).filter(OutfitLog.user_id == current_user.id).count()
    total_trips = db.query(TripPlan).filter(TripPlan.user_id == current_user.id).count()
    return StatsResponse(total_items=total_items, total_logs=total_logs, total_trips=total_trips)


@router.post("/seed-test-data", status_code=201)
def seed_test_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    for data in TEST_ITEMS:
        item = ClothingItem(
            user_id=current_user.id,
            name=data["name"],
            category=data["category"],
            weight=data.get("weight", "medium"),
            condition=data.get("condition", "good"),
            like_score=data.get("like_score", 3),
            usage_type=data.get("usage_type", "both"),
            seasons=json.dumps(data.get("seasons", [])),
            color=data.get("color"),
        )
        db.add(item)
    db.commit()
    return {"message": f"{len(TEST_ITEMS)} capi di esempio inseriti"}
