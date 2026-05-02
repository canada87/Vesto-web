from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
import json
from app.database import get_db
from app.models.db import ClothingItem, User
from app.auth import get_current_user
from app.schemas import (
    ClothingItemCreate, ClothingItemUpdate,
    ClothingItemResponse, ClothingItemListResponse,
)
from app.services.photo_service import save_photo, delete_photo

router = APIRouter()


def _build_photo_url(item: ClothingItem) -> Optional[str]:
    if item.local_photo_path:
        return f"/photos/{item.local_photo_path}"
    return None


def _item_to_response(item: ClothingItem) -> ClothingItemResponse:
    data = {
        "id": item.id,
        "user_id": item.user_id,
        "name": item.name,
        "category": item.category,
        "age_years": item.age_years,
        "weight": item.weight,
        "condition": item.condition,
        "like_score": item.like_score,
        "usage_type": item.usage_type,
        "seasons": json.loads(item.seasons),
        "status": item.status,
        "location": item.location,
        "color": item.color,
        "notes": item.notes,
        "local_photo_path": item.local_photo_path,
        "photo_url": _build_photo_url(item),
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }
    return ClothingItemResponse(**data)


@router.get("", response_model=ClothingItemListResponse)
def list_items(
    category: Optional[str] = None,
    status: Optional[str] = None,
    season: Optional[str] = None,
    location: Optional[str] = None,
    usage_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ClothingItem).filter(ClothingItem.user_id == current_user.id)
    if category:
        query = query.filter(ClothingItem.category == category)
    if status:
        query = query.filter(ClothingItem.status == status)
    if location:
        query = query.filter(ClothingItem.location == location)
    if usage_type:
        query = query.filter(ClothingItem.usage_type == usage_type)

    all_items = query.order_by(ClothingItem.created_at.desc()).all()

    if season:
        all_items = [i for i in all_items if season in json.loads(i.seasons)]

    responses = [_item_to_response(i) for i in all_items]
    return ClothingItemListResponse(items=responses, total=len(responses))


@router.post("", response_model=ClothingItemResponse, status_code=201)
async def create_item(
    name: str = Form(...),
    category: str = Form(...),
    age_years: float = Form(0),
    weight: str = Form("medium"),
    condition: str = Form("good"),
    like_score: int = Form(3),
    usage_type: str = Form("both"),
    seasons: str = Form("[]"),
    status: str = Form("inWardrobe"),
    location: str = Form("Casa"),
    color: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = ClothingItem(
        user_id=current_user.id,
        name=name,
        category=category,
        age_years=age_years,
        weight=weight,
        condition=condition,
        like_score=like_score,
        usage_type=usage_type,
        seasons=seasons,
        status=status,
        location=location,
        color=color,
        notes=notes,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    if photo and photo.filename:
        file_bytes = await photo.read()
        filename = save_photo(item.id, file_bytes)
        item.local_photo_path = filename
        db.commit()
        db.refresh(item)

    return _item_to_response(item)


@router.get("/{item_id}", response_model=ClothingItemResponse)
def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id,
        ClothingItem.user_id == current_user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Capo non trovato")
    return _item_to_response(item)


@router.put("/{item_id}", response_model=ClothingItemResponse)
def update_item(
    item_id: str,
    body: ClothingItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id,
        ClothingItem.user_id == current_user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Capo non trovato")

    item.name = body.name
    item.category = body.category
    item.age_years = body.age_years
    item.weight = body.weight
    item.condition = body.condition
    item.like_score = body.like_score
    item.usage_type = body.usage_type
    item.seasons = json.dumps(body.seasons)
    item.status = body.status
    item.location = body.location
    item.color = body.color
    item.notes = body.notes
    db.commit()
    db.refresh(item)
    return _item_to_response(item)


@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id,
        ClothingItem.user_id == current_user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Capo non trovato")
    delete_photo(item.id)
    db.delete(item)
    db.commit()


@router.post("/{item_id}/photo", response_model=ClothingItemResponse)
async def upload_photo(
    item_id: str,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id,
        ClothingItem.user_id == current_user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Capo non trovato")
    file_bytes = await photo.read()
    filename = save_photo(item.id, file_bytes)
    item.local_photo_path = filename
    db.commit()
    db.refresh(item)
    return _item_to_response(item)


@router.delete("/{item_id}/photo", response_model=ClothingItemResponse)
def remove_photo(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id,
        ClothingItem.user_id == current_user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Capo non trovato")
    delete_photo(item.id)
    item.local_photo_path = None
    db.commit()
    db.refresh(item)
    return _item_to_response(item)
