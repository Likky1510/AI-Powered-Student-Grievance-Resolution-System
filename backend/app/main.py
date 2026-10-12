"""
Main FastAPI app. Run with:
  uvicorn app.main:app --reload
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import engine, Base
from app.routers import auth, grievances, departments, analytics
from app.core.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if they don't exist (use Alembic migrations in real production use)
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="AI-Powered Student Grievance Resolution System",
    description="Multi-agent grievance triage, routing, escalation, and analytics platform.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # frontend dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(grievances.router)
app.include_router(departments.router)
app.include_router(analytics.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
