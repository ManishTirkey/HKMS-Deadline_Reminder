from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Path, Query
from sqlalchemy.orm import Session
from app.services.database_service import get_db
from app.services.database_service import get_service_categories
from pydantic import BaseModel
from typing import Optional, List
from fastapi import BackgroundTasks
from app.services import run_job


class ReminderResponse(BaseModel):
    """Reminder Response model"""
    message: str
    saved_file: str
    new_categories: List


# Error response models
class ErrorResponse(BaseModel):
    """Generic error response model"""
    detail: str
    error_code: Optional[str] = None
    timestamp: Optional[datetime] = None


class DriveUrlRequest(BaseModel):
    """URL Request model for Spreadsheet"""
    url: str


router = APIRouter(
    prefix="/apihkms",
    tags=["API"],
    responses={404: {"description": "Not found"}},
)


@router.get("/services")
async def get_services(db: Session = Depends(get_db)):
    try:
        services = get_service_categories(db)
        return [{"id": s.id, "category_name": s.category_name} for s in services]
    except Exception as e:
        print(f"error found: {e}")
