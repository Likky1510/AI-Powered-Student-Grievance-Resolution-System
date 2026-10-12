"""
Pydantic schemas — these define what the API accepts and returns.
Kept separate from the SQLAlchemy models (app/models/models.py) on purpose:
DB models describe storage, schemas describe the API contract.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

from app.models.models import UserRole, GrievanceCategory, GrievancePriority, GrievanceStatus


# ---------- Auth ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    role: UserRole = UserRole.student
    phone: Optional[str] = None
    department_id: Optional[str] = None  # required if role == staff


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole
    department_id: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Department ----------
class DepartmentOut(BaseModel):
    id: str
    name: str
    category: GrievanceCategory
    sla_hours: int

    class Config:
        from_attributes = True


# ---------- Grievance ----------
class GrievanceCreate(BaseModel):
    raw_text: str = Field(min_length=10, description="The student's complaint, in their own words")


class GrievanceOut(BaseModel):
    id: str
    student_id: str
    department_id: Optional[str]
    raw_text: str
    category: Optional[GrievanceCategory]
    priority: Optional[GrievancePriority]
    status: GrievanceStatus
    classification_reason: Optional[str]
    priority_reason: Optional[str]
    is_escalated: bool
    escalation_count: int
    created_at: datetime
    assigned_at: Optional[datetime]
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


class GrievanceStatusUpdate(BaseModel):
    status: GrievanceStatus
    note: Optional[str] = None


class StatusHistoryOut(BaseModel):
    status: GrievanceStatus
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


# ---------- Analytics ----------
class DepartmentStats(BaseModel):
    department_name: str
    total_grievances: int
    resolved_count: int
    avg_resolution_hours: Optional[float]
    escalation_rate: float
    sla_breach_rate: float


class CategoryStats(BaseModel):
    category: str
    total: int
    avg_resolution_hours: Optional[float]


class AnalyticsSummary(BaseModel):
    total_grievances: int
    resolved: int
    pending: int
    escalated: int
    by_department: List[DepartmentStats]
    by_category: List[CategoryStats]
    ai_summary: Optional[str] = None  # Claude-generated plain-English insight
