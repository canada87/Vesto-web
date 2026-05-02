from enum import Enum


class ClothingCategory(str, Enum):
    top = "top"
    bottom = "bottom"
    shoes = "shoes"
    outerwear = "outerwear"
    accessory = "accessory"
    underwear = "underwear"
    sportswear = "sportswear"


class ClothingWeight(str, Enum):
    light = "light"
    medium = "medium"
    heavy = "heavy"


class ClothingCondition(str, Enum):
    new_item = "new"
    good = "good"
    worn = "worn"
    old = "old"


class UsageType(str, Enum):
    work = "work"
    personal = "personal"
    both = "both"


class Season(str, Enum):
    spring = "spring"
    summer = "summer"
    autumn = "autumn"
    winter = "winter"


class ItemStatus(str, Enum):
    in_wardrobe = "inWardrobe"
    in_laundry = "inLaundry"
    in_use = "inUse"


class Weather(str, Enum):
    sunny = "sunny"
    cloudy = "cloudy"
    rainy = "rainy"
    cold = "cold"
    hot = "hot"


class UserRole(str, Enum):
    admin = "admin"
    user = "user"
