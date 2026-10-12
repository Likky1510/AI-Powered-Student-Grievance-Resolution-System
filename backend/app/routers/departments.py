from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import require_role
from app.models.models import Department, UserRole
from app.models.schemas import DepartmentOut

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=List[DepartmentOut])
def list_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()


@router.post("", response_model=DepartmentOut, dependencies=[Depends(require_role(UserRole.admin))])
def create_department(name: str, category: str, sla_hours: int = 72, db: Session = Depends(get_db)):
    existing = db.query(Department).filter(Department.category == category).first()
    if existing:
        raise HTTPException(status_code=400, detail="A department already exists for this category")
    dept = Department(name=name, category=category, sla_hours=sla_hours)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept
