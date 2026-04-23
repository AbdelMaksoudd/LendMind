from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from controllers.application_controller import render_application_detail, update_application_status
from database import get_db

router = APIRouter()


@router.get("/applications/{app_id}", response_class=HTMLResponse)
async def application_detail(request: Request, app_id: int, db: Session = Depends(get_db)):
    return render_application_detail(request, app_id, db)


@router.post("/applications/{app_id}/status")
async def update_status(
    request: Request,
    app_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
):
    return await update_application_status(request, app_id, status, db)
