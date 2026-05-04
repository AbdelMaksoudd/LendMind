from fastapi import Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from auth import templates, require_role
from database import get_db, LoanApplication, LoanStatus


def render_dashboard(request: Request, db: Session):
    user = require_role(request, "admin")
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    applications = (
        db.query(LoanApplication).order_by(LoanApplication.created_at.desc()).all()
    )

    total = len(applications)
    approved = sum(1 for a in applications if a.status == LoanStatus.APPROVED)
    rejected = sum(1 for a in applications if a.status == LoanStatus.REJECTED)

    analytics = {
        "total": total,
        "approved": approved,
        "rejected": rejected,
    }

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "user": user,
            "applications": applications,
            "analytics": analytics,
        },
    )
