from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# --- Auth ---

class LoginRequest(BaseModel):
    username: str
    password: str
    trusted_device_token: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: Optional[str] = None
    token_type: str = "bearer"
    requires_2fa: bool = False
    partial_token: Optional[str] = None


class TwoFAVerifyRequest(BaseModel):
    partial_token: str
    otp_code: str
    remember_device: bool = True


class TwoFAVerifyResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    trusted_device_token: Optional[str] = None


class TwoFASetupResponse(BaseModel):
    qr_code: str
    secret: str


class TwoFAEnableRequest(BaseModel):
    otp_code: str


class TwoFADisableRequest(BaseModel):
    otp_code: str


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"


class UserUpdate(BaseModel):
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: str
    username: str
    role: str
    is_active: bool
    totp_enabled: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


# --- Clothing Items ---

class ClothingItemCreate(BaseModel):
    name: str
    category: str
    age_years: float = 0
    weight: str = "medium"
    condition: str = "good"
    like_score: int = 3
    usage_type: str = "both"
    seasons: List[str] = []
    status: str = "inWardrobe"
    location: str = "Casa"
    color: Optional[str] = None
    notes: Optional[str] = None


class ClothingItemUpdate(ClothingItemCreate):
    pass


class ClothingItemResponse(ClothingItemCreate):
    id: str
    user_id: str
    local_photo_path: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClothingItemListResponse(BaseModel):
    items: List[ClothingItemResponse]
    total: int


# --- Outfit Log ---

class OutfitLogCreate(BaseModel):
    date: datetime
    item_ids: List[str]
    occasion: str
    weather: Optional[str] = None
    notes: Optional[str] = None


class OutfitLogResponse(OutfitLogCreate):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Trip Plans ---

class TripPlanCreate(BaseModel):
    name: str
    destination: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    trip_type: str = "both"
    duration_only: bool = False
    custom_duration_days: Optional[int] = None


class TripSlot(BaseModel):
    day: int
    category: str
    item_id: str
    locked: bool = True


class TripPlanResponse(TripPlanCreate):
    id: str
    user_id: str
    item_ids: List[str] = []
    packing_slots: List[TripSlot] = []
    created_at: datetime

    class Config:
        from_attributes = True


class TripItemsUpdate(BaseModel):
    item_ids: List[str]
    locked_item_ids: List[str] = []


class TripSlotsUpdate(BaseModel):
    packing_slots: List[TripSlot]


# --- Suggestions ---

class OutfitSuggestionRequest(BaseModel):
    occasion: str
    weather: Optional[str] = None
    season: Optional[str] = None
    location: Optional[str] = None
    novelty: bool = False


class OutfitSuggestionResponse(BaseModel):
    top: Optional[ClothingItemResponse] = None
    bottom: Optional[ClothingItemResponse] = None
    shoes: Optional[ClothingItemResponse] = None
    outerwear: Optional[ClothingItemResponse] = None
    accessories: List[ClothingItemResponse] = []
    missing_categories: List[str] = []


class PackingSuggestionRequest(BaseModel):
    trip_type: str
    season: str
    duration_days: int


class PackingSuggestionResponse(BaseModel):
    items: List[ClothingItemResponse]
    missing_categories: List[str] = []


# --- Settings ---

class LocationAdd(BaseModel):
    name: str


class StatsResponse(BaseModel):
    total_items: int
    total_logs: int
    total_trips: int
