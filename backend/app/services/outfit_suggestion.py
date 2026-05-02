from typing import Optional, List
from datetime import date, datetime, timedelta
import json
from sqlalchemy.orm import Session
from app.models.db import ClothingItem, OutfitLog


def get_current_season() -> str:
    month = date.today().month
    if month in [3, 4, 5]:
        return "spring"
    if month in [6, 7, 8]:
        return "summer"
    if month in [9, 10, 11]:
        return "autumn"
    return "winter"


def weather_weight_bonus(weather: Optional[str], weight: str) -> float:
    if weather in ["cold", "rainy"] and weight == "heavy":
        return 2.0
    if weather in ["cold", "rainy"] and weight == "light":
        return -2.0
    if weather in ["hot", "sunny"] and weight == "light":
        return 2.0
    if weather in ["hot", "sunny"] and weight == "heavy":
        return -2.0
    return 0.0


def days_since_last_worn(item_id: str, logs: List[OutfitLog]) -> int:
    worn_dates = []
    for log in logs:
        ids = json.loads(log.item_ids)
        if item_id in ids:
            worn_dates.append(log.date.date())
    if not worn_dates:
        return 9999
    return (date.today() - max(worn_dates)).days


def suggest_outfit(
    db: Session,
    user_id: str,
    occasion: str,
    weather: Optional[str] = None,
    season: Optional[str] = None,
    location: Optional[str] = None,
    novelty: bool = False,
) -> dict:
    if season is None:
        season = get_current_season()

    cutoff = datetime.utcnow() - timedelta(days=90)
    recent_logs = (
        db.query(OutfitLog)
        .filter(OutfitLog.user_id == user_id, OutfitLog.date >= cutoff)
        .all()
    )

    worn_top_bottom_pairs = set()
    for log in recent_logs:
        ids = json.loads(log.item_ids)
        log_items = (
            db.query(ClothingItem)
            .filter(ClothingItem.id.in_(ids), ClothingItem.user_id == user_id)
            .all()
        )
        tops_in_log = [i.id for i in log_items if i.category == "top"]
        bottoms_in_log = [i.id for i in log_items if i.category == "bottom"]
        for t in tops_in_log:
            for b in bottoms_in_log:
                worn_top_bottom_pairs.add((t, b))

    query = db.query(ClothingItem).filter(
        ClothingItem.user_id == user_id,
        ClothingItem.status != "inLaundry",
    )
    if location:
        query = query.filter(ClothingItem.location == location)
    all_items = query.all()

    def is_compatible(item: ClothingItem) -> bool:
        seasons = json.loads(item.seasons)
        if season not in seasons and len(seasons) > 0:
            return False
        if occasion == "work" and item.usage_type == "personal":
            return False
        if occasion == "personal" and item.usage_type == "work":
            return False
        return True

    def item_score(item: ClothingItem) -> float:
        days = days_since_last_worn(item.id, recent_logs)
        if novelty:
            return float(days)
        w_bonus = weather_weight_bonus(weather, item.weight)
        return days * 2.0 + item.like_score + w_bonus

    compatible = [i for i in all_items if is_compatible(i)]
    by_category: dict[str, list] = {}
    for item in compatible:
        by_category.setdefault(item.category, []).append(item)

    result: dict = {
        "top": None, "bottom": None,
        "shoes": None, "outerwear": None,
        "accessories": [], "missing_categories": [],
    }

    tops = sorted(by_category.get("top", []), key=item_score, reverse=True)
    bottoms = sorted(by_category.get("bottom", []), key=item_score, reverse=True)

    chosen_top = None
    chosen_bottom = None
    for top in tops:
        for bottom in bottoms:
            if (top.id, bottom.id) not in worn_top_bottom_pairs:
                chosen_top = top
                chosen_bottom = bottom
                break
        if chosen_top:
            break

    if not chosen_top and tops:
        chosen_top = tops[0]
    if not chosen_bottom and bottoms:
        chosen_bottom = bottoms[0]

    result["top"] = chosen_top
    result["bottom"] = chosen_bottom

    shoes_list = sorted(by_category.get("shoes", []), key=item_score, reverse=True)
    result["shoes"] = shoes_list[0] if shoes_list else None

    needs_outerwear = weather in ["cold", "rainy"] or season in ["autumn", "winter"]
    if needs_outerwear:
        outerwear_list = sorted(by_category.get("outerwear", []), key=item_score, reverse=True)
        result["outerwear"] = outerwear_list[0] if outerwear_list else None

    if not result["top"]:
        result["missing_categories"].append("top")
    if not result["bottom"]:
        result["missing_categories"].append("bottom")
    if not result["shoes"]:
        result["missing_categories"].append("shoes")
    if needs_outerwear and not result["outerwear"]:
        result["missing_categories"].append("outerwear")

    return result
