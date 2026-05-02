from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from app.database import engine, SessionLocal
from app.models.db import Base, User
from app.auth import hash_password
from app.routers import auth, items, outfit_logs, trips, suggestions, settings, backup

Base.metadata.create_all(bind=engine)

# Migrazioni: aggiunge colonne mancanti se il DB esiste già senza di esse
with engine.connect() as conn:
    from sqlalchemy import text
    migrations = [
        ("users", "totp_secret", "TEXT"),
        ("users", "totp_enabled", "INTEGER DEFAULT 0"),
        ("trip_plans", "locked_item_ids", "TEXT DEFAULT '[]'"),
    ]
    for table, col, definition in migrations:
        try:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {definition}"))
            conn.commit()
        except Exception:
            pass  # colonna già presente

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
