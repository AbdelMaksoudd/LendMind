from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from controllers.dashboard_controller import render_dashboard
from database import get_db

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, db: Session = Depends(get_db)):
    return render_dashboard(request, db)
