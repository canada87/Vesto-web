import io
import base64
import pyotp
import qrcode
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db import User
from app.auth import (
    verify_password, hash_password, create_access_token,
    create_partial_token, create_trusted_device_token,
    verify_partial_token, verify_trusted_device_token,
    get_current_user, require_admin,
)
from app.schemas import (
    LoginRequest, LoginResponse,
    TwoFAVerifyRequest, TwoFAVerifyResponse,
    TwoFASetupResponse, TwoFAEnableRequest, TwoFADisableRequest,
    UserCreate, UserUpdate, UserResponse,
)

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabilitato")

    if user.totp_enabled:
        if body.trusted_device_token and verify_trusted_device_token(body.trusted_device_token, user.id):
            return LoginResponse(access_token=create_access_token({"sub": user.id}))
        return LoginResponse(requires_2fa=True, partial_token=create_partial_token(user.id))

    return LoginResponse(access_token=create_access_token({"sub": user.id}))


@router.post("/2fa/verify", response_model=TwoFAVerifyResponse)
def verify_2fa(body: TwoFAVerifyRequest, db: Session = Depends(get_db)):
    user_id = verify_partial_token(body.partial_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token non valido o scaduto")

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user or not user.totp_enabled:
        raise HTTPException(status_code=401, detail="Utente non trovato")

    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(body.otp_code, valid_window=1):
        raise HTTPException(status_code=400, detail="Codice OTP non valido")

    trusted_token = create_trusted_device_token(user.id) if body.remember_device else None
    return TwoFAVerifyResponse(
        access_token=create_access_token({"sub": user.id}),
        trusted_device_token=trusted_token,
    )


@router.post("/2fa/setup", response_model=TwoFASetupResponse)
def setup_2fa(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=current_user.username, issuer_name="Vesto")

    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    current_user.totp_secret = secret
    db.commit()

    return TwoFASetupResponse(qr_code=qr_b64, secret=secret)


@router.post("/2fa/enable")
def enable_2fa(body: TwoFAEnableRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.totp_secret:
        raise HTTPException(status_code=400, detail="Prima esegui il setup 2FA")

    totp = pyotp.TOTP(current_user.totp_secret)
    if not totp.verify(body.otp_code, valid_window=1):
        raise HTTPException(status_code=400, detail="Codice OTP non valido")

    current_user.totp_enabled = True
    db.commit()

    return {"trusted_device_token": create_trusted_device_token(current_user.id)}


@router.post("/2fa/disable")
def disable_2fa(body: TwoFADisableRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.totp_enabled:
        raise HTTPException(status_code=400, detail="2FA non è attivo")

    totp = pyotp.TOTP(current_user.totp_secret)
    if not totp.verify(body.otp_code, valid_window=1):
        raise HTTPException(status_code=400, detail="Codice OTP non valido")

    current_user.totp_enabled = False
    current_user.totp_secret = None
    db.commit()
    return {"message": "2FA disabilitato"}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(User).order_by(User.created_at).all()


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=409, detail="Username già in uso")
    user = User(
        username=body.username,
        hashed_password=hash_password(body.password),
        role=body.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: str, body: UserUpdate, db: Session = Depends(get_db), current_admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    if body.password is not None:
        user.hashed_password = hash_password(body.password)
    if body.role is not None:
        user.role = body.role
    if body.is_active is not None:
        user.is_active = body.is_active
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: str, db: Session = Depends(get_db), current_admin: User = Depends(require_admin)):
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Non puoi eliminare te stesso")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    db.delete(user)
    db.commit()
