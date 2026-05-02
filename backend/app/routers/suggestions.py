from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db import User
from app.auth import get_current_user
from app.schemas import (
    OutfitSuggestionRequest, OutfitSuggestionResponse,
    PackingSuggestionRequest, PackingSuggestionResponse,
    ClothingItemResponse,
)
from app.services.outfit_suggestion import suggest_outfit
from app.services.packing import suggest_packing
import json

router = APIRouter()


def _item_to_response(item, photo_url=None) -> ClothingItemResponse:
    return ClothingItemResponse(
        id=item.id,
        user_id=item.user_id,
        name=item.name,
        category=item.category,
        age_years=item.age_years,
        weight=item.weight,
        condition=item.condition,
        like_score=item.like_score,
        usage_type=item.usage_type,
        seasons=json.loads(item.seasons),
        status=item.status,
        location=item.location,
        color=item.color,
        notes=item.notes,
        local_photo_path=item.local_photo_path,
        photo_url=f"/photos/{item.local_photo_path}" if item.local_photo_path else None,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.post("/outfit", response_model=OutfitSuggestionResponse)
def outfit_suggestion(
    body: OutfitSuggestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = suggest_outfit(
        db=db,
        user_id=current_user.id,
        occasion=body.occasion,
        weather=body.weather,
        season=body.season,
        location=body.location,
        novelty=body.novelty,
    )
    return OutfitSuggestionResponse(
        top=_item_to_response(result["top"]) if result["top"] else None,
        bottom=_item_to_response(result["bottom"]) if result["bottom"] else None,
        shoes=_item_to_response(result["shoes"]) if result["shoes"] else None,
        outerwear=_item_to_response(result["outerwear"]) if result["outerwear"] else None,
        accessories=[_item_to_response(a) for a in result.get("accessories", [])],
        missing_categories=result["missing_categories"],
    )


@router.post("/packing", response_model=PackingSuggestionResponse)
def packing_suggestion(
    body: PackingSuggestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = suggest_packing(
        db=db,
        user_id=current_user.id,
        trip_type=body.trip_type,
        season=body.season,
        duration_days=body.duration_days,
    )
    return PackingSuggestionResponse(
        items=[_item_to_response(i) for i in result["items"]],
        missing_categories=result["missing_categories"],
    )
