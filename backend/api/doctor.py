"""
Doctor Dashboard API — authentication, alerts, and broadcast messaging.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError

from backend.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from backend.models.database import get_db, Doctor, DoctorAlert, User
from backend.services import messaging_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/doctor", tags=["Doctor Dashboard"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/doctor/login")


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def _hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _get_current_doctor(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Doctor:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        doctor_id: int = payload.get("sub")
        if doctor_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise credentials_exception
    if not doctor.is_verified:
        raise HTTPException(status_code=403, detail="Doctor account not verified.")
    return doctor


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class DoctorRegister(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=8)
    region: Optional[str] = None
    specialization: Optional[str] = None


class AlertCreate(BaseModel):
    title: str = Field(..., min_length=3)
    message: str = Field(..., min_length=10)
    region: Optional[str] = None
    alert_type: str = Field("awareness", description="awareness | prevention | emergency")
    broadcast_sms: bool = False


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/register", summary="Register a new doctor account")
def register(req: DoctorRegister, db: Session = Depends(get_db)):
    existing = db.query(Doctor).filter(Doctor.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")
    doctor = Doctor(
        name=req.name,
        email=req.email,
        password_hash=_hash_password(req.password),
        region=req.region,
        specialization=req.specialization,
        is_verified=False,   # admin must verify
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return {
        "message": "Registration successful. Your account is pending verification.",
        "doctor_id": doctor.id,
    }


@router.post("/login", summary="Doctor login — returns JWT access token")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.email == form.username).first()
    if not doctor or not _verify_password(form.password, doctor.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    if not doctor.is_verified:
        raise HTTPException(status_code=403, detail="Account not yet verified.")
    token = _create_access_token({"sub": doctor.id})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", summary="Get current doctor profile")
def me(current: Doctor = Depends(_get_current_doctor)):
    return {
        "id": current.id,
        "name": current.name,
        "email": current.email,
        "region": current.region,
        "specialization": current.specialization,
    }


@router.post("/alerts", summary="Create and optionally broadcast a health alert")
def create_alert(
    req: AlertCreate,
    db: Session = Depends(get_db),
    current: Doctor = Depends(_get_current_doctor),
):
    alert = DoctorAlert(
        doctor_id=current.id,
        title=req.title,
        message=req.message,
        region=req.region or current.region,
        alert_type=req.alert_type,
        is_broadcast=req.broadcast_sms,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    sms_result = None
    if req.broadcast_sms:
        # Collect phone numbers of users in the doctor's region
        region = req.region or current.region
        query = db.query(User.phone).filter(User.phone.is_not(None))
        if region:
            query = query.filter(User.location_lat.is_not(None))  # only users with location
        phones = [row[0] for row in query.all() if row[0]]

        if phones:
            results = messaging_service.broadcast_alert(phones, req.title, req.message)
            success = sum(1 for r in results if r.get("success"))
            sms_result = {"sent": success, "total": len(phones)}

    return {
        "alert_id": alert.id,
        "title": alert.title,
        "region": alert.region,
        "sms_broadcast": sms_result,
    }


@router.get("/alerts", summary="List alerts created by the current doctor")
def list_alerts(db: Session = Depends(get_db), current: Doctor = Depends(_get_current_doctor)):
    alerts = (
        db.query(DoctorAlert)
        .filter(DoctorAlert.doctor_id == current.id)
        .order_by(DoctorAlert.created_at.desc())
        .all()
    )
    return [
        {
            "id": a.id,
            "title": a.title,
            "message": a.message,
            "region": a.region,
            "alert_type": a.alert_type,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in alerts
    ]


@router.get("/alerts/public", summary="Get public doctor alerts (no auth required)")
def public_alerts(region: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(DoctorAlert).order_by(DoctorAlert.created_at.desc())
    if region:
        query = query.filter(DoctorAlert.region.ilike(f"%{region}%"))
    alerts = query.limit(50).all()
    return [
        {
            "id": a.id,
            "title": a.title,
            "message": a.message,
            "region": a.region,
            "alert_type": a.alert_type,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in alerts
    ]


# ---------------------------------------------------------------------------
# Admin-only: verify a doctor account (simple toggle, no extra auth for demo)
# ---------------------------------------------------------------------------

@router.put("/verify/{doctor_id}", summary="[Admin] Verify a doctor account")
def verify_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found.")
    doctor.is_verified = True
    db.commit()
    return {"message": f"Doctor '{doctor.name}' verified successfully."}
