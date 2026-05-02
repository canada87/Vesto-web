from sqlalchemy.orm import Session
from app.models.db import ClothingItem
import json


def suggest_packing(
    db: Session,
    user_id: str,
    trip_type: str,
    season: str,
    duration_days: int,
) -> dict:
    all_items = (
        db.query(ClothingItem)
        .filter(ClothingItem.user_id == user_id, ClothingItem.status != "inLaundry")
        .all()
    )

    def is_seasonal(item: ClothingItem) -> bool:
        seasons = json.loads(item.seasons)
        return season in seasons or len(seasons) == 0

    def is_compatible_type(item: ClothingItem) -> bool:
        if trip_type == "work" and item.usage_type == "personal":
            return False
        if trip_type == "personal" and item.usage_type == "work":
            return False
        return True

    def filter_and_sort(category: str, count: int) -> list:
        items = [
            i for i in all_items
            if i.category == category and is_seasonal(i) and is_compatible_type(i)
        ]
        items.sort(key=lambda x: x.like_score, reverse=True)
        return items[:count]

    tops_count = duration_days
    bottoms_count = duration_days
    underwear_count = duration_days + 1

    selected = []
    missing = []

    tops = filter_and_sort("top", tops_count)
    if tops:
        selected.extend(tops)
    else:
        missing.append("top")

    bottoms = filter_and_sort("bottom", bottoms_count)
    if bottoms:
        selected.extend(bottoms)
    else:
        missing.append("bottom")

    underwear = filter_and_sort("underwear", underwear_count)
    if underwear:
        selected.extend(underwear)
    else:
        missing.append("underwear")

    shoes = filter_and_sort("shoes", 1)
    if shoes:
        selected.extend(shoes)
    else:
        missing.append("shoes")

    if trip_type in ["work", "both"]:
        formal_shoes = [
            i for i in all_items
            if i.category == "shoes"
            and i.usage_type in ["work", "both"]
            and i not in shoes
        ]
        if formal_shoes:
            selected.append(formal_shoes[0])

    if season in ["autumn", "winter"]:
        outerwear = filter_and_sort("outerwear", 1)
        if outerwear:
            selected.extend(outerwear)
        else:
            missing.append("outerwear")

    if duration_days >= 3:
        sport = filter_and_sort("sportswear", 1)
        if sport:
            selected.extend(sport)

    accessories_count = max(1, duration_days // 2)
    accessories = filter_and_sort("accessory", accessories_count)
    if accessories:
        selected.extend(accessories)

    return {"items": selected, "missing_categories": missing}
