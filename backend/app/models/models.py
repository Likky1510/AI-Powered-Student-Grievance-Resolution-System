"""
ORM models for the Grievance Resolution System.

Lifecycle of a Grievance:
  SUBMITTED -> CATEGORIZED -> ASSIGNED -> IN_PROGRESS -> (ESCALATED) -> RESOLVED -> CLOSED
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Enum, Integer, Boolean
)
from sqlalchemy.orm import relationship

from app.db.session import Base


def gen_uuid():
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    student = "student"
    staff = "staff"
    admin = "admin"


class GrievanceCategory(str, enum.Enum):
    academic = "academic"
    fees = "fees"
    hostel = "hostel"
    attendance = "attendance"
    certificates = "certificates"
    infrastructure = "infrastructure"
    other = "other"


class GrievancePriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class GrievanceStatus(str, enum.Enum):
    submitted = "submitted"
    categorized = "categorized"
    assigned = "assigned"
    in_progress = "in_progress"
    escalated = "escalated"
    resolved = "resolved"
    closed = "closed"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.student)
    department_id = Column(String, ForeignKey("departments.id"), nullable=True)  # set for staff
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    department = relationship("Department", back_populates="staff_members")
    grievances = relationship("Grievance", back_populates="student", foreign_keys="Grievance.student_id")


class Department(Base):
    __tablename__ = "departments"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, unique=True, nullable=False)
    category = Column(Enum(GrievanceCategory), nullable=False, unique=True)
    sla_hours = Column(Integer, nullable=False, default=72)  # resolution target
    contact_email = Column(String, nullable=True)
    contact_whatsapp = Column(String, nullable=True)

    staff_members = relationship("User", back_populates="department")
    grievances = relationship("Grievance", back_populates="department")


class Grievance(Base):
    __tablename__ = "grievances"

    id = Column(String, primary_key=True, default=gen_uuid)
    student_id = Column(String, ForeignKey("users.id"), nullable=False)
    department_id = Column(String, ForeignKey("departments.id"), nullable=True)

    raw_text = Column(Text, nullable=False)               # original complaint text
    category = Column(Enum(GrievanceCategory), nullable=True)   # set by Classification Agent
    priority = Column(Enum(GrievancePriority), nullable=True)   # set by Priority Agent
    status = Column(Enum(GrievanceStatus), nullable=False, default=GrievanceStatus.submitted)

    classification_reason = Column(Text, nullable=True)   # explainability from the agent
    priority_reason = Column(Text, nullable=True)

    assigned_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    is_escalated = Column(Boolean, default=False)
    escalation_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("User", back_populates="grievances", foreign_keys=[student_id])
    department = relationship("Department", back_populates="grievances")
    status_history = relationship("StatusHistory", back_populates="grievance", order_by="StatusHistory.created_at")
    escalations = relationship("Escalation", back_populates="grievance")
    feedback = relationship("Feedback", back_populates="grievance", uselist=False)


class StatusHistory(Base):
    """Audit trail: every status change a grievance goes through."""
    __tablename__ = "status_history"

    id = Column(String, primary_key=True, default=gen_uuid)
    grievance_id = Column(String, ForeignKey("grievances.id"), nullable=False)
    status = Column(Enum(GrievanceStatus), nullable=False)
    note = Column(Text, nullable=True)
    changed_by = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    grievance = relationship("Grievance", back_populates="status_history")


class Escalation(Base):
    __tablename__ = "escalations"

    id = Column(String, primary_key=True, default=gen_uuid)
    grievance_id = Column(String, ForeignKey("grievances.id"), nullable=False)
    reason = Column(Text, nullable=False)
    escalated_to = Column(String, nullable=True)  # e.g. "Department Head", "Admin"
    created_at = Column(DateTime, default=datetime.utcnow)

    grievance = relationship("Grievance", back_populates="escalations")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, default=gen_uuid)
    grievance_id = Column(String, ForeignKey("grievances.id"), unique=True, nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    grievance = relationship("Grievance", back_populates="feedback")
