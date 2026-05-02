# Vesto Web-App — Specifica Completa per Implementazione

> **Documento destinato a:** Un'altra istanza di Claude che dovrà costruire da zero la versione web di Vesto, self-hostabile con Docker.
> **Data di redazione:** 2026-05-02
> **App originale:** Flutter mobile app per gestione guardaroba intelligente

---

## 1. Cos'è Vesto

Vesto è un'applicazione per gestire il proprio guardaroba personale in modo intelligente. Permette di:

- Catalogare i propri capi di abbigliamento con foto, caratteristiche e metadati
- Ricevere suggerimenti automatici di outfit basati su meteo, occasione e storico utilizzi
- Registrare gli outfit indossati per evitare ripetizioni
- Pianificare la valigia per i viaggi con suggerimento automatico dei capi da portare
- Sincronizzare i dati tramite backup su filesystem

L'app originale è mobile (Flutter/Dart) con database SQLite locale e backup su Google Drive. La versione web dovrà replicare tutte le funzionalità come Single Page Application con backend REST API, database server-side e storage locale per le foto, il tutto impacchettato in Docker Compose per self-hosting.

La versione web supporta **più utenti** (massimo ~5), ognuno con il proprio guardaroba separato. È presente un ruolo **amministratore** per la gestione degli utenti. L'autenticazione è obbligatoria per accedere a qualsiasi funzionalità.

---

## 2. Stack Tecnologico

### Backend
- **Python 3.12 + FastAPI** — API REST, async, documentazione OpenAPI automatica
- **SQLite** — adeguato per ≤5 utenti con un guardaroba di centinaia di capi ciascuno
- **SQLAlchemy 2.x** — ORM per gestione database
- **Alembic** — migrazioni database
- **Pillow** — compressione/resize foto
- **python-multipart** — upload file
- **uvicorn** — ASGI server
- **passlib[bcrypt]** — hashing password
- **python-jose[cryptography]** — generazione e verifica JWT

### Frontend
- **Vue 3 + Vite + TypeScript** — framework reattivo con Composition API
- **Vuetify 3** — libreria UI Material Design 3, mobile-first, bottom navigation nativa
- **Pinia** — state management
- **Vue Router 4** — routing SPA con navigation guards per auth
- **Axios** — HTTP client con interceptors per JWT
- **vite-plugin-pwa** — Service Worker + Web App Manifest per installabilità mobile (PWA)

### Infrastruttura Docker
- **Nginx** — reverse proxy + serve static files frontend
- **Docker Compose** — orchestrazione multi-container

---

## 3. Architettura Docker

```
┌─────────────────────────────────────────────────┐
│                  Docker Compose                  │
│                                                  │
│  ┌──────────┐    ┌──────────┐   ┌────────────┐  │
│  │  nginx   │───▶│ frontend │   │  backend   │  │
│  │  :80     │    │  :3000   │   │  :8000     │  │
│  └──────────┘    └──────────┘   └─────┬──────┘  │
│       │                               │         │
│       └───────────────────────────────┘         │
│                                        │         │
│                              ┌─────────▼──────┐  │
│                              │  volumes/      │  │
│                              │  data/vesto.db │  │
│                              │  photos/       │  │
│                              └────────────────┘  │
└─────────────────────────────────────────────────┘
```

### docker-compose.yml

```yaml
version: '3.9'

services:
  backend:
    build: ./backend
    container_name: vesto-backend
    restart: unless-stopped
    volumes:
      - vesto_data:/app/data
      - vesto_photos:/app/photos
    environment:
      - DATABASE_URL=sqlite:////app/data/vesto.db
      - PHOTOS_DIR=/app/photos
      - SECRET_KEY=${SECRET_KEY:-change-me-in-production}
      - ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
      - ADMIN_PASSWORD=${ADMIN_PASSWORD:-changeme}
    expose:
      - "8000"

  frontend:
    build: ./frontend
    container_name: vesto-frontend
    restart: unless-stopped
    expose:
      - "3000"

  nginx:
    image: nginx:alpine
    container_name: vesto-nginx
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
      - frontend

volumes:
  vesto_data:
  vesto_photos:
```

### nginx/nginx.conf

```nginx
events { worker_connections 1024; }

http {
  server {
    listen 80;

    location /api/ {
      proxy_pass http://backend:8000/;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      client_max_body_size 10M;
    }

    location /photos/ {
      proxy_pass http://backend:8000/photos/;
    }

    location / {
      proxy_pass http://frontend:3000;
      proxy_set_header Host $host;
    }
  }
}
```

### .env (da creare in root del progetto)

```
SECRET_KEY=una-stringa-casuale-molto-lunga
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password-sicura
```

---

## 4. Modelli Dati

### 4.1 Enumerazioni

```python
# backend/app/models/enums.py
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
```

### 4.2 Schema Database SQLAlchemy

```python
# backend/app/models/db.py
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")          # UserRole: "admin" | "user"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ClothingItem(Base):
    __tablename__ = "clothing_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)          # ClothingCategory
    local_photo_path = Column(String, nullable=True)   # path relativo in /photos
    age_years = Column(Float, default=0)
    weight = Column(String, default="medium")          # ClothingWeight
    condition = Column(String, default="good")         # ClothingCondition
    like_score = Column(Integer, default=3)            # 1-5
    usage_type = Column(String, default="both")        # UsageType
    seasons = Column(Text, default="[]")               # JSON array di Season
    status = Column(String, default="inWardrobe")      # ItemStatus
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
    item_ids = Column(Text, nullable=False)            # JSON array di item IDs
    occasion = Column(String, nullable=False)          # UsageType
    weather = Column(String, nullable=True)            # Weather
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
    trip_type = Column(String, default="both")         # UsageType
    item_ids = Column(Text, default="[]")              # JSON array di item IDs
    duration_only = Column(Boolean, default=False)
    custom_duration_days = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AppSetting(Base):
    __tablename__ = "app_settings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    key = Column(String, nullable=False)
    value = Column(Text, nullable=False)
    # Usata per: locations (JSON array), preferenze app
    # Chiave univoca per (user_id, key)
```

### 4.3 Schemi Pydantic (API)

```python
# backend/app/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Auth ---

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

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

class TripPlanResponse(TripPlanCreate):
    id: str
    user_id: str
    item_ids: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True

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
```

---

## 5. Autenticazione e Autorizzazione

### 5.1 Logica JWT

```python
# backend/app/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db import User
import os

SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 giorni

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token non valido o scaduto",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if user is None:
        raise credentials_exception
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Richiesti privilegi amministratore")
    return current_user
```

### 5.2 Inizializzazione Admin al primo avvio

In `main.py`, all'avvio dell'app, creare l'utente admin se non esiste:

```python
def create_initial_admin(db: Session):
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "changeme")
    existing = db.query(User).filter(User.username == admin_username).first()
    if not existing:
        admin = User(
            username=admin_username,
            hashed_password=hash_password(admin_password),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()
```

---

## 6. API Endpoints

Base URL: `/api/v1`

Tutti gli endpoint (tranne `/auth/login`) richiedono header `Authorization: Bearer <token>`.

### 6.1 Autenticazione

| Metodo | Path | Auth | Descrizione |
|--------|------|------|-------------|
| POST | `/auth/login` | No | Login. Body: `{"username": "...", "password": "..."}`. Risposta: `{"access_token": "...", "token_type": "bearer"}` |
| GET | `/auth/me` | Sì | Dati utente corrente |

### 6.2 Gestione Utenti (solo Admin)

| Metodo | Path | Descrizione |
|--------|------|-------------|
| GET | `/auth/users` | Lista tutti gli utenti |
| POST | `/auth/users` | Crea nuovo utente `{"username": "...", "password": "...", "role": "user"}` |
| PUT | `/auth/users/{id}` | Modifica utente (password, ruolo, is_active) |
| DELETE | `/auth/users/{id}` | Elimina utente (non se stesso) |

### 6.3 Capi Abbigliamento

Tutti filtrati per `user_id` dell'utente autenticato.

| Metodo | Path | Descrizione |
|--------|------|-------------|
| GET | `/items` | Lista capi. Query params: `category`, `status`, `season`, `location`, `usage_type` |
| POST | `/items` | Crea nuovo capo (form-data con foto opzionale) |
| GET | `/items/{id}` | Dettaglio capo |
| PUT | `/items/{id}` | Aggiorna capo |
| DELETE | `/items/{id}` | Elimina capo (e foto) |
| POST | `/items/{id}/photo` | Upload/replace foto (multipart/form-data, field `photo`) |
| DELETE | `/items/{id}/photo` | Rimuovi foto |

**GET /items** — risposta:
```json
{
  "items": [...],
  "total": 42
}
```

### 6.4 Outfit Log

| Metodo | Path | Descrizione |
|--------|------|-------------|
| GET | `/outfit-logs` | Lista log. Query params: `days=90` |
| POST | `/outfit-logs` | Registra outfit indossato |
| GET | `/outfit-logs/{id}` | Dettaglio log |
| DELETE | `/outfit-logs/{id}` | Elimina log |

### 6.5 Viaggi

| Metodo | Path | Descrizione |
|--------|------|-------------|
| GET | `/trips` | Lista tutti i viaggi |
| POST | `/trips` | Crea nuovo viaggio |
| GET | `/trips/{id}` | Dettaglio viaggio |
| PUT | `/trips/{id}` | Aggiorna viaggio |
| DELETE | `/trips/{id}` | Elimina viaggio |
| PUT | `/trips/{id}/items` | Aggiorna lista capi `{"item_ids": [...]}` |

### 6.6 Suggerimenti

| Metodo | Path | Descrizione |
|--------|------|-------------|
| POST | `/suggestions/outfit` | Suggerisce outfit (body: `OutfitSuggestionRequest`) |
| POST | `/suggestions/packing` | Suggerisce packing lista (body: `PackingSuggestionRequest`) |

### 6.7 Impostazioni

| Metodo | Path | Descrizione |
|--------|------|-------------|
| GET | `/settings/locations` | Lista locazioni utente corrente |
| POST | `/settings/locations` | Aggiungi locazione `{"name": "Palestra"}` |
| DELETE | `/settings/locations/{name}` | Rimuovi locazione |
| GET | `/settings/stats` | Statistiche utente corrente |

### 6.8 Backup / Export

| Metodo | Path | Descrizione |
|--------|------|-------------|
| GET | `/backup/export` | Esporta dati utente corrente in JSON |
| POST | `/backup/import` | Importa da JSON (sovrascrive dati utente corrente) |

### 6.9 Dati di Test

| Metodo | Path | Descrizione |
|--------|------|-------------|
| POST | `/settings/seed-test-data` | Inserisce 19 capi di esempio per l'utente corrente |

### 6.10 Foto

Le foto sono servite da `/photos/{filename}` tramite FastAPI StaticFiles o Nginx. Il nome file include l'`item_id` per garantire unicità tra utenti: `photo_{item_id}.jpg`.

---

## 7. Algoritmi Core (da reimplementare in Python)

Tutti gli algoritmi devono ricevere il `user_id` e filtrare i dati di conseguenza.

### 7.1 OutfitSuggestionService

```python
# backend/app/services/outfit_suggestion.py
from typing import Optional, List
from datetime import date, datetime, timedelta
import json
from sqlalchemy.orm import Session
from app.models.db import ClothingItem, OutfitLog

def get_current_season() -> str:
    month = date.today().month
    if month in [3, 4, 5]: return "spring"
    if month in [6, 7, 8]: return "summer"
    if month in [9, 10, 11]: return "autumn"
    return "winter"

def weather_weight_bonus(weather: Optional[str], weight: str) -> float:
    if weather in ["cold", "rainy"] and weight == "heavy": return 2.0
    if weather in ["cold", "rainy"] and weight == "light": return -2.0
    if weather in ["hot", "sunny"] and weight == "light": return 2.0
    if weather in ["hot", "sunny"] and weight == "heavy": return -2.0
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
    recent_logs = db.query(OutfitLog).filter(
        OutfitLog.user_id == user_id,
        OutfitLog.date >= cutoff
    ).all()

    worn_top_bottom_pairs = set()
    for log in recent_logs:
        ids = json.loads(log.item_ids)
        log_items = db.query(ClothingItem).filter(
            ClothingItem.id.in_(ids),
            ClothingItem.user_id == user_id
        ).all()
        tops_in_log = [i.id for i in log_items if i.category == "top"]
        bottoms_in_log = [i.id for i in log_items if i.category == "bottom"]
        for t in tops_in_log:
            for b in bottoms_in_log:
                worn_top_bottom_pairs.add((t, b))

    query = db.query(ClothingItem).filter(
        ClothingItem.user_id == user_id,
        ClothingItem.status != "inLaundry"
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
        else:
            w_bonus = weather_weight_bonus(weather, item.weight)
            return days * 2.0 + item.like_score + w_bonus

    compatible = [i for i in all_items if is_compatible(i)]
    by_category = {}
    for item in compatible:
        by_category.setdefault(item.category, []).append(item)

    result = {
        "top": None, "bottom": None,
        "shoes": None, "outerwear": None,
        "accessories": [], "missing_categories": []
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

    if not result["top"]: result["missing_categories"].append("top")
    if not result["bottom"]: result["missing_categories"].append("bottom")
    if not result["shoes"]: result["missing_categories"].append("shoes")
    if needs_outerwear and not result["outerwear"]:
        result["missing_categories"].append("outerwear")

    return result
```

### 7.2 PackingService

```python
# backend/app/services/packing.py
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
    all_items = db.query(ClothingItem).filter(
        ClothingItem.user_id == user_id,
        ClothingItem.status != "inLaundry"
    ).all()

    def is_seasonal(item: ClothingItem) -> bool:
        seasons = json.loads(item.seasons)
        return season in seasons or len(seasons) == 0

    def is_compatible_type(item: ClothingItem) -> bool:
        if trip_type == "work" and item.usage_type == "personal": return False
        if trip_type == "personal" and item.usage_type == "work": return False
        return True

    def filter_and_sort(category: str, count: int) -> list:
        items = [
            i for i in all_items
            if i.category == category and is_seasonal(i) and is_compatible_type(i)
        ]
        items.sort(key=lambda x: x.like_score, reverse=True)
        return items[:count]

    tops_count = duration_days
    bottoms_count = max(1, duration_days // 2)
    underwear_count = duration_days + 1

    selected = []
    missing = []

    tops = filter_and_sort("top", tops_count)
    if tops: selected.extend(tops)
    else: missing.append("top")

    bottoms = filter_and_sort("bottom", bottoms_count)
    if bottoms: selected.extend(bottoms)
    else: missing.append("bottom")

    underwear = filter_and_sort("underwear", underwear_count)
    if underwear: selected.extend(underwear)
    else: missing.append("underwear")

    shoes = filter_and_sort("shoes", 1)
    if shoes: selected.extend(shoes)
    else: missing.append("shoes")

    if trip_type in ["work", "both"]:
        formal_shoes = [
            i for i in all_items
            if i.category == "shoes" and i.usage_type in ["work", "both"]
            and i not in shoes
        ]
        if formal_shoes:
            selected.append(formal_shoes[0])

    if season in ["autumn", "winter"]:
        outerwear = filter_and_sort("outerwear", 1)
        if outerwear: selected.extend(outerwear)
        else: missing.append("outerwear")

    if duration_days >= 3:
        sport = filter_and_sort("sportswear", 1)
        if sport: selected.extend(sport)

    return {
        "items": selected,
        "missing_categories": missing
    }
```

---

## 8. Struttura File Backend

```
backend/
├── Dockerfile
├── requirements.txt
├── app/
│   ├── main.py              # FastAPI app, startup admin, include routers
│   ├── database.py          # SQLAlchemy engine, SessionLocal, get_db
│   ├── auth.py              # JWT, hashing, dipendenze auth
│   ├── models/
│   │   ├── __init__.py
│   │   ├── db.py            # SQLAlchemy models (User incluso)
│   │   └── enums.py         # Enumerazioni
│   ├── schemas.py           # Pydantic schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          # Login, /me, gestione utenti (admin)
│   │   ├── items.py         # CRUD capi
│   │   ├── outfit_logs.py   # CRUD outfit logs
│   │   ├── trips.py         # CRUD viaggi
│   │   ├── suggestions.py   # Algoritmi suggerimento
│   │   ├── settings.py      # Impostazioni, locazioni, seed
│   │   └── backup.py        # Export/Import JSON
│   └── services/
│       ├── __init__.py
│       ├── outfit_suggestion.py
│       ├── packing.py
│       └── photo_service.py
```

### backend/app/main.py

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from app.database import engine, SessionLocal
from app.models.db import Base
from app.routers import auth, items, outfit_logs, trips, suggestions, settings, backup
from app.auth import hash_password
from app.models.db import User

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vesto API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "changeme")
        existing = db.query(User).filter(User.username == admin_username).first()
        if not existing:
            admin = User(
                username=admin_username,
                hashed_password=hash_password(admin_password),
                role="admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()

PHOTOS_DIR = os.getenv("PHOTOS_DIR", "/app/photos")
os.makedirs(PHOTOS_DIR, exist_ok=True)
app.mount("/photos", StaticFiles(directory=PHOTOS_DIR), name="photos")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(items.router, prefix="/items", tags=["items"])
app.include_router(outfit_logs.router, prefix="/outfit-logs", tags=["outfit-logs"])
app.include_router(trips.router, prefix="/trips", tags=["trips"])
app.include_router(suggestions.router, prefix="/suggestions", tags=["suggestions"])
app.include_router(settings.router, prefix="/settings", tags=["settings"])
app.include_router(backup.router, prefix="/backup", tags=["backup"])
```

### backend/Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data /app/photos

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### backend/requirements.txt

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.35
alembic==1.13.3
pillow==10.4.0
python-multipart==0.0.12
pydantic==2.9.2
python-dateutil==2.9.0
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
```

---

## 9. Struttura File Frontend

```
frontend/
├── Dockerfile
├── package.json
├── vite.config.ts
├── tsconfig.json
├── index.html
├── public/
│   ├── manifest.webmanifest   # PWA manifest
│   └── icons/                 # App icons 192x192, 512x512
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── plugins/
│   │   └── vuetify.ts         # Configurazione Vuetify + tema custom
│   ├── router/
│   │   └── index.ts           # Routes con navigation guard (requiresAuth)
│   ├── stores/
│   │   ├── auth.ts            # Pinia: token, user, login/logout
│   │   ├── items.ts
│   │   ├── outfitLogs.ts
│   │   ├── trips.ts
│   │   └── settings.ts
│   ├── api/
│   │   ├── client.ts          # Axios instance con interceptor JWT
│   │   ├── auth.ts
│   │   ├── items.ts
│   │   ├── outfitLogs.ts
│   │   ├── trips.ts
│   │   ├── suggestions.ts
│   │   └── settings.ts
│   ├── types/
│   │   └── index.ts           # TypeScript types (mirror Pydantic schemas)
│   ├── components/
│   │   ├── items/
│   │   │   ├── ItemCard.vue       # VCard capo con foto/placeholder
│   │   │   ├── ItemGrid.vue       # Griglia responsive capi
│   │   │   ├── ItemForm.vue       # Form aggiungi/modifica
│   │   │   ├── ItemDetail.vue     # VDialog dettaglio capo
│   │   │   └── PhotoUpload.vue    # Upload foto con preview
│   │   ├── outfit/
│   │   │   ├── OutfitSuggestion.vue   # Card suggerimento outfit
│   │   │   ├── OutfitCard.vue         # Card outfit nel log
│   │   │   └── LogOutfitDialog.vue    # VDialog registra outfit
│   │   └── trip/
│   │       ├── TripCard.vue
│   │       ├── TripForm.vue
│   │       └── PackingList.vue
│   ├── views/
│   │   ├── LoginView.vue          # Pagina di login
│   │   ├── WardrobeView.vue       # Guardaroba
│   │   ├── TodayView.vue          # Outfit del giorno
│   │   ├── DiscoveryView.vue      # Prova nuovi outfit
│   │   ├── HistoryView.vue        # Storico outfit
│   │   ├── TripView.vue           # Pianificatore viaggi
│   │   ├── SettingsView.vue       # Impostazioni
│   │   └── admin/
│   │       └── UsersView.vue      # Gestione utenti (solo admin)
│   └── utils/
│       ├── seasons.ts
│       ├── constants.ts
│       └── formatters.ts
```

### frontend/package.json (dipendenze principali)

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vuetify": "^3.6.0",
    "pinia": "^2.1.0",
    "vue-router": "^4.3.0",
    "axios": "^1.7.0",
    "@mdi/font": "^7.4.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0",
    "vite-plugin-pwa": "^0.20.0",
    "vite-plugin-vuetify": "^2.0.0",
    "typescript": "^5.4.0"
  }
}
```

### frontend/vite.config.ts

```ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    vuetify({ autoImport: true }),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Vesto',
        short_name: 'Vesto',
        description: 'Il tuo guardaroba intelligente',
        theme_color: '#2E4057',
        background_color: '#F8F9FA',
        display: 'standalone',
        orientation: 'portrait',
        icons: [
          { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
    }),
  ],
})
```

### frontend/Dockerfile

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx-spa.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

> Il file `nginx-spa.conf` deve avere la direttiva `try_files $uri $uri/ /index.html;` per supportare il routing SPA.

---

## 10. UI/UX — Tema e Design

### Tema Vuetify (src/plugins/vuetify.ts)

```ts
import { createVuetify } from 'vuetify'
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

export default createVuetify({
  theme: {
    defaultTheme: 'vestoLight',
    themes: {
      vestoLight: {
        dark: false,
        colors: {
          primary: '#2E4057',       // blu-grigio scuro — header, bottoni primari
          secondary: '#048A81',     // teal — accenti, FAB
          warning: '#F4B942',       // giallo-oro — badge, like score
          error: '#D62839',         // rosso — errori, cancella
          background: '#F8F9FA',    // grigio chiarissimo — sfondo pagine
          surface: '#FFFFFF',
        },
      },
    },
  },
  defaults: {
    VBtn: { rounded: 'lg' },
    VCard: { rounded: 'xl' },
    VTextField: { variant: 'outlined', density: 'comfortable' },
    VSelect: { variant: 'outlined', density: 'comfortable' },
  },
})
```

### Navigazione

**Layout principale (App.vue):** usa `VNavigationDrawer` su desktop (≥960px) e `VBottomNavigation` su mobile (<960px), rilevato tramite `useDisplay()` di Vuetify.

| Icona MDI | Label | Route |
|-----------|-------|-------|
| `mdi-hanger` | Guardaroba | `/` |
| `mdi-weather-sunny` | Oggi | `/today` |
| `mdi-sparkles` | Prova | `/discovery` |
| `mdi-bag-suitcase` | Valigia | `/trips` |
| `mdi-cog` | Impostazioni | `/settings` |

Admin vede anche una voce aggiuntiva: `mdi-account-group` → `/admin/users`.

### Pagina Login

- `VCard` centrata con logo/titolo "Vesto"
- Campi username e password
- Pulsante "Accedi"
- Errore mostrato con `VAlert` variant="tonal" color="error"
- Il token viene salvato in `localStorage` e iniettato in Axios

### Pagina Guardaroba (`/`)

- `VTextField` di ricerca + chip per filtri (categoria, stagione, status, locazione)
- Griglia `VRow` + `VCol` responsive: `cols="12" sm="6" md="4" lg="3"`
- `ItemCard`: `VCard` con immagine (`VImg`, aspect-ratio 1, cover) o placeholder `VIcon` `mdi-tshirt-crew`
- FAB `VBtn` icon `mdi-plus` color="secondary" position="bottom right" per nuovo capo
- Click su card → `VDialog` fullscreen su mobile, large su desktop

### Pagina Oggi (`/today`) e Prova (`/discovery`)

- Selettori `VBtnToggle` per occasione e meteo
- Pulsante "Suggerisci Outfit" → mostra outfit in card con foto capi
- Pulsante "Indossa" → `VDialog` per confermare e registrare nel log
- Pulsante "Rigenera" per nuovo suggerimento
- Tab o sezione inferiore con storico ultimi outfit (togglabile)

### Pagina Valigia (`/trips`)

- Lista viaggi con `VCard`
- `VDialog` per creare/modificare viaggio
- Dettaglio viaggio: info + lista packing con `VCheckbox` per ogni capo

### Pagina Impostazioni (`/settings`)

- `VList` per locazioni (aggiungi/rimuovi)
- `VCard` statistiche con `VStatItem` o layout a 3 colonne
- Pulsanti export/import JSON

### Pagina Utenti Admin (`/admin/users`)

- `VDataTable` con colonne: username, ruolo, stato, azioni
- `VDialog` per creazione nuovo utente
- Toggle attivo/disattivo per ogni utente
- Reset password inline

---

## 11. Autenticazione Frontend

### Axios interceptor (src/api/client.ts)

```ts
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const client = axios.create({ baseURL: '/api/v1' })

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('vesto_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('vesto_token')
      router.push('/login')
    }
    return Promise.reject(err)
  }
)

export default client
```

### Navigation guard (src/router/index.ts)

```ts
router.beforeEach((to) => {
  const token = localStorage.getItem('vesto_token')
  if (to.meta.requiresAuth && !token) return '/login'
  if (to.meta.requiresAdmin) {
    const auth = useAuthStore()
    if (auth.user?.role !== 'admin') return '/'
  }
  if (to.path === '/login' && token) return '/'
})
```

Tutte le route tranne `/login` hanno `meta: { requiresAuth: true }`. La route `/admin/users` ha anche `meta: { requiresAdmin: true }`.

### Pinia auth store (src/stores/auth.ts)

```ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiLogin, apiGetMe } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('vesto_token'))
  const user = ref<UserResponse | null>(null)

  async function login(username: string, password: string) {
    const data = await apiLogin(username, password)
    token.value = data.access_token
    localStorage.setItem('vesto_token', data.access_token)
    await fetchMe()
  }

  async function fetchMe() {
    user.value = await apiGetMe()
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('vesto_token')
  }

  return { token, user, login, logout, fetchMe }
})
```

---

## 12. Gestione Foto

Il backend deve:

1. Accettare upload via `POST /items/{id}/photo` (multipart/form-data, campo `photo`)
2. Salvare ridimensionata (max 400px lato lungo, JPEG 78%) come `photo_{item_id}.jpg`
3. Eliminare la foto quando si elimina il capo o si fa `DELETE /items/{id}/photo`
4. Rispondere con `photo_url = /photos/photo_{item_id}.jpg`

```python
# backend/app/services/photo_service.py
from PIL import Image
import io, os

PHOTOS_DIR = os.getenv("PHOTOS_DIR", "/app/photos")
MAX_SIZE = 400
JPEG_QUALITY = 78

def save_photo(item_id: str, file_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(file_bytes))
    img = img.convert("RGB")
    img.thumbnail((MAX_SIZE, MAX_SIZE), Image.LANCZOS)
    filename = f"photo_{item_id}.jpg"
    path = os.path.join(PHOTOS_DIR, filename)
    img.save(path, "JPEG", quality=JPEG_QUALITY)
    return filename

def delete_photo(item_id: str) -> None:
    path = os.path.join(PHOTOS_DIR, f"photo_{item_id}.jpg")
    if os.path.exists(path):
        os.remove(path)
```

---

## 13. Dati di Test (Seed)

Endpoint `POST /settings/seed-test-data` — richiede autenticazione, inserisce i capi per l'utente corrente:

```python
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
```

---

## 14. Internazionalizzazione

L'app è in **italiano**. Tutte le label, placeholder e messaggi nel frontend sono in italiano. Non implementare i18n completo — usare direttamente le stringhe italiane nel codice.

```ts
// src/utils/constants.ts
export const CATEGORY_LABELS: Record<string, string> = {
  top: "Parte sopra",
  bottom: "Parte sotto",
  shoes: "Scarpe",
  outerwear: "Capospalla",
  accessory: "Accessorio",
  underwear: "Intimo",
  sportswear: "Abbigliamento sportivo",
};

export const SEASON_LABELS: Record<string, string> = {
  spring: "Primavera",
  summer: "Estate",
  autumn: "Autunno",
  winter: "Inverno",
};

export const WEATHER_LABELS: Record<string, string> = {
  sunny: "Soleggiato",
  cloudy: "Nuvoloso",
  rainy: "Pioggia",
  cold: "Freddo",
  hot: "Caldo",
};

export const USAGE_TYPE_LABELS: Record<string, string> = {
  work: "Lavoro",
  personal: "Personale",
  both: "Entrambi",
};

export const STATUS_LABELS: Record<string, string> = {
  inWardrobe: "In guardaroba",
  inLaundry: "In lavanderia",
  inUse: "In uso",
};

export const CONDITION_LABELS: Record<string, string> = {
  new: "Nuovo",
  good: "Buono",
  worn: "Consumato",
  old: "Vecchio",
};
```

---

## 15. Funzionalità NON da implementare

- **Google Drive sync** — sostituito dal backup JSON locale
- **Google Sign-in** — sostituito dall'autenticazione propria con JWT
- **Camera access** — sostituito da upload file normale
- **Push notifications** — non applicabile
- **CI/CD Codemagic** — irrilevante

---

## 16. Procedura di Build e Avvio

### Prerequisiti
- Docker Engine 24+
- Docker Compose v2+

### Struttura cartelle del progetto

```
vesto-web/
├── docker-compose.yml
├── .env                    # SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD
├── nginx/
│   └── nginx.conf
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       └── ...
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts
    ├── public/
    │   ├── manifest.webmanifest
    │   └── icons/
    └── src/
        └── ...
```

### Avvio

```bash
# Prima esecuzione
docker compose up --build -d

# Aggiornamento dopo modifiche
docker compose up --build -d

# Logs
docker compose logs -f

# Stop
docker compose down

# Stop + rimuovi volumi (cancella tutti i dati)
docker compose down -v
```

L'app sarà disponibile su `http://localhost` (porta 80). Al primo avvio viene creato automaticamente l'utente admin con le credenziali definite nel `.env`.

---

## 17. Considerazioni Finali

1. **Multi-utente (max ~5):** Ogni utente vede e gestisce solo il proprio guardaroba. L'admin può gestire gli account ma non naviga nei dati altrui. SQLite è adeguato per questo carico.

2. **PWA installabile:** Grazie a `vite-plugin-pwa` l'app è installabile su Android e iOS come app home screen. Il service worker gestisce la cache degli asset statici per uso offline parziale (la UI carica, ma i dati richiedono connessione).

3. **Mobile-first:** Navigazione bottom bar su mobile, sidebar su desktop. Card a tutta larghezza su schermi stretti. Tutti i dialog sono fullscreen su mobile.

4. **Persistenza dati:** I dati sono in volumi Docker. Usare la funzione export JSON periodicamente o fare backup del volume `vesto_data`.

5. **HTTPS:** Per accesso remoto aggiungere un reverse proxy esterno (Traefik o Caddy) con certificato TLS. Non è in scope per questo documento. Con HTTPS il token JWT in localStorage è accettabile per 5 utenti privati; per maggiore sicurezza si può migrare a httpOnly cookie.

6. **Foto senza foto:** Ogni capo può non avere foto. Mostrare placeholder con icona `mdi-tshirt-crew` (o icona appropriata per categoria).

7. **Auto-detect stagione:** Marzo-Maggio → Primavera, Giugno-Agosto → Estate, Settembre-Novembre → Autunno, Dicembre-Febbraio → Inverno.
