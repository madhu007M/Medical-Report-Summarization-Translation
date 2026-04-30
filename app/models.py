from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .db import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(256), nullable=True)
    text_content = Column(Text, nullable=False)
    simplified_summary = Column(Text, nullable=True)
    risk_level = Column(String(32), nullable=True)
    language = Column(String(8), default="en")
    location = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    symptoms = relationship("SymptomLog", back_populates="report")


class SymptomLog(Base):
    __tablename__ = "symptom_logs"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=True)
    symptom = Column(String(128), nullable=False)
    severity = Column(String(32), nullable=True)
    location = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    report = relationship("Report", back_populates="symptoms")


class DoctorAlert(Base):
    __tablename__ = "doctor_alerts"

    id = Column(Integer, primary_key=True, index=True)
    doctor_name = Column(String(128), nullable=False)
    region = Column(String(128), nullable=False)
    title = Column(String(256), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(128), unique=True, index=True)
    last_message = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OutbreakCluster(Base):
    __tablename__ = "outbreak_clusters"

    id = Column(Integer, primary_key=True, index=True)
    disease = Column(String(128), nullable=False)
    location = Column(String(128), nullable=False)
    case_count = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)
    last_detected_at = Column(DateTime, default=datetime.utcnow)
