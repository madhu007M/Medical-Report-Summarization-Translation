"""
SQLAlchemy database models for the Medical Report Platform.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean,
    DateTime, ForeignKey, JSON, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from backend.config import DATABASE_URL

Base = declarative_base()
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# User / Doctor models
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    language_preference = Column(String(10), default="en")
    location_lat = Column(Float, nullable=True)
    location_lon = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    reports = relationship("MedicalReport", back_populates="user")
    symptom_logs = relationship("SymptomLog", back_populates="user")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    region = Column(String(100), nullable=True)
    specialization = Column(String(100), nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    alerts = relationship("DoctorAlert", back_populates="doctor")


# ---------------------------------------------------------------------------
# Medical Report models
# ---------------------------------------------------------------------------

class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # pdf, image, text
    extracted_text = Column(Text, nullable=True)
    summary_en = Column(Text, nullable=True)
    summary_hi = Column(Text, nullable=True)
    summary_kn = Column(Text, nullable=True)
    summary_ta = Column(Text, nullable=True)
    risk_level = Column(String(20), nullable=True)   # Low, Moderate, High
    risk_score = Column(Float, nullable=True)
    risk_details = Column(JSON, nullable=True)
    audio_path_en = Column(String(255), nullable=True)
    audio_path_hi = Column(String(255), nullable=True)
    audio_path_kn = Column(String(255), nullable=True)
    audio_path_ta = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reports")
    chat_sessions = relationship("ChatSession", back_populates="report")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("medical_reports.id"), nullable=False)
    messages = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    report = relationship("MedicalReport", back_populates="chat_sessions")


# ---------------------------------------------------------------------------
# Symptom & Alert models
# ---------------------------------------------------------------------------

class SymptomLog(Base):
    __tablename__ = "symptom_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    symptoms = Column(JSON, nullable=False)   # list of symptom strings
    location_lat = Column(Float, nullable=True)
    location_lon = Column(Float, nullable=True)
    region = Column(String(100), nullable=True)
    reported_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="symptom_logs")


class OutbreakAlert(Base):
    __tablename__ = "outbreak_alerts"

    id = Column(Integer, primary_key=True, index=True)
    disease = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    case_count = Column(Integer, default=0)
    severity = Column(String(20), default="Watch")   # Watch, Warning, Emergency
    message = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DoctorAlert(Base):
    __tablename__ = "doctor_alerts"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    region = Column(String(100), nullable=True)
    alert_type = Column(String(50), default="awareness")  # awareness, prevention, emergency
    is_broadcast = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    doctor = relationship("Doctor", back_populates="alerts")
