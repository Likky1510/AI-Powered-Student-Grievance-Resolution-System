from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user, require_role
from app.models.models import Grievance, StatusHistory, GrievanceStatus, User, UserRole, Feedback
from app.models.schemas import (
    GrievanceCreate, GrievanceOut, GrievanceStatusUpdate,
    StatusHistoryOut, FeedbackCreate,
)
from app.agents.pipeline import run_intake_pipeline
from app.agents.email_service import (
    notify_grievance_submitted, notify_status_change,
    notify_staff_new_grievance,
)

router = APIRouter(prefix="/grievances", tags=["grievances"])


@router.post("", response_model=GrievanceOut, status_code=status.HTTP_201_CREATED)
def submit_grievance(
    payload: GrievanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submission workflow:
    Submission -> Classification Agent -> Priority Agent -> Routing Agent
    -> persisted as ASSIGNED -> email notification sent.
    """
    grievance = Grievance(student_id=current_user.id, raw_text=payload.raw_text)
    db.add(grievance)
    db.commit()
    db.refresh(grievance)

    # Run the multi-agent intake pipeline (LangGraph)
    result = run_intake_pipeline(db, grievance.id, payload.raw_text)

    grievance.category = result["category"]
    grievance.classification_reason = result["category_reason"]
    grievance.priority = result["priority"]
    grievance.priority_reason = result["priority_reason"]
    grievance.department_id = result["department_id"]
    grievance.status = GrievanceStatus.assigned
    grievance.assigned_at = datetime.utcnow()
    db.add(grievance)

    db.add(StatusHistory(grievance_id=grievance.id, status=GrievanceStatus.categorized,
                          note=f"Auto-classified as {result['category']}"))
    db.add(StatusHistory(grievance_id=grievance.id, status=GrievanceStatus.assigned,
                          note=f"Routed to {result['department_name']}"))
    db.commit()
    db.refresh(grievance)

    notify_grievance_submitted(current_user.email, grievance.id, grievance.category.value)

    staff_emails = [u.email for u in db.query(User).filter(User.department_id == grievance.department_id).all()]
    admin_emails = [u.email for u in db.query(User).filter(User.role == UserRole.admin).all()]
    notify_staff_new_grievance(
        staff_emails + admin_emails,
        grievance.id,
        grievance.category.value,
        current_user.email,
        grievance.department.name if grievance.department else "Department",
    )

    return grievance


@router.get("/me", response_model=List[GrievanceOut])
def my_grievances(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Grievance).filter(Grievance.student_id == current_user.id).order_by(Grievance.created_at.desc()).all()


@router.get("/department", response_model=List[GrievanceOut])
def department_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.staff, UserRole.admin)),
):
    """Staff see only their department's queue; admins can see all via /grievances/all."""
    if current_user.role == UserRole.admin:
        return db.query(Grievance).order_by(Grievance.created_at.desc()).all()
    return (
        db.query(Grievance)
        .filter(Grievance.department_id == current_user.department_id)
        .order_by(Grievance.created_at.desc())
        .all()
    )


@router.get("/{grievance_id}", response_model=GrievanceOut)
def get_grievance(grievance_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    grievance = db.query(Grievance).filter(Grievance.id == grievance_id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    if current_user.role == UserRole.student and grievance.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this grievance")
    return grievance


@router.get("/{grievance_id}/history", response_model=List[StatusHistoryOut])
def get_history(grievance_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    grievance = db.query(Grievance).filter(Grievance.id == grievance_id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    return grievance.status_history


@router.patch("/{grievance_id}/status", response_model=GrievanceOut)
def update_status(
    grievance_id: str,
    payload: GrievanceStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.staff, UserRole.admin)),
):
    grievance = db.query(Grievance).filter(Grievance.id == grievance_id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")

    if current_user.role == UserRole.staff and grievance.department_id != current_user.department_id:
        raise HTTPException(status_code=403, detail="Not authorized for this department's grievances")

    grievance.status = payload.status
    if payload.status == GrievanceStatus.resolved:
        grievance.resolved_at = datetime.utcnow()
    if payload.status == GrievanceStatus.closed:
        grievance.closed_at = datetime.utcnow()

    db.add(StatusHistory(
        grievance_id=grievance.id, status=payload.status,
        note=payload.note, changed_by=current_user.id,
    ))
    db.commit()
    db.refresh(grievance)

    student = db.query(User).filter(User.id == grievance.student_id).first()
    if student:
        notify_status_change(student.email, grievance.id, payload.status.value)

    return grievance


@router.post("/{grievance_id}/feedback", status_code=status.HTTP_201_CREATED)
def submit_feedback(
    grievance_id: str,
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    grievance = db.query(Grievance).filter(Grievance.id == grievance_id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    if grievance.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your grievance")
    if grievance.status not in (GrievanceStatus.resolved, GrievanceStatus.closed):
        raise HTTPException(status_code=400, detail="Can only give feedback on resolved/closed grievances")

    existing = db.query(Feedback).filter(Feedback.grievance_id == grievance_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Feedback already submitted")

    feedback = Feedback(grievance_id=grievance_id, rating=payload.rating, comment=payload.comment)
    db.add(feedback)
    grievance.status = GrievanceStatus.closed
    grievance.closed_at = datetime.utcnow()
    db.commit()
    return {"message": "Feedback submitted"}
