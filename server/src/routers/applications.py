from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from controllers.application_controller import render_application_detail
from database import get_db

router = APIRouter()


@router.get("/applications/{app_id}", response_class=HTMLResponse)
async def application_detail(
    request: Request, app_id: int, db: Session = Depends(get_db)
):
    return render_application_detail(request, app_id, db)
