from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    totp_secret = Column(String, nullable=True)
    totp_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ClothingItem(Base):
    __tablename__ = "clothing_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    local_photo_path = Column(String, nullable=True)
    age_years = Column(Float, default=0)
    weight = Column(String, default="medium")
    condition = Column(String, default="good")
    like_score = Column(Integer, default=3)
    usage_type = Column(String, default="both")
    seasons = Column(Text, default="[]")
    status = Column(String, default="inWardrobe")
    location = Column(String, default="Casa")
    color = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OutfitLog(Base):
    __tablename__ = "outfit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    item_ids = Column(Text, nullable=False)
    occasion = Column(String, nullable=False)
    weather = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TripPlan(Base):
    __tablename__ = "trip_plans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    destination = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    trip_type = Column(String, default="both")
    item_ids = Column(Text, default="[]")
    locked_item_ids = Column(Text, default="[]")
    packing_slots = Column(Text, default="[]")
    duration_only = Column(Boolean, default=False)
    custom_duration_days = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AppSetting(Base):
    __tablename__ = "app_settings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    key = Column(String, nullable=False)
    value = Column(Text, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_user_setting"),)
