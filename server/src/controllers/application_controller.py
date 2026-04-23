from fastapi import Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from auth import templates, require_role
from database import get_db, LoanApplication, LoanStatus
from ws_manager import manager


def render_apply_page(request: Request, user):
    return templates.TemplateResponse(
        "apply.html",
        {"request": request, "user": user, "success": None, "errors": None},
    )


async def submit_application(
    request: Request,
    loan_amnt: float,
    int_rate: float,
    annual_inc: float,
    dti: float,
    revol_bal: float,
    revol_util: float,
    total_bal_ex_mort: float,
    bc_util: float,
    bc_open_to_buy: float,
    total_bc_limit: float,
    mo_sin_old_rev_tl_op: int,
    mo_sin_old_il_acct: int,
    tot_cur_bal: float,
    avg_cur_bal: float,
    total_rev_hi_lim: float,
    db: Session,
):
    user = require_role(request, "user")
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    errors = []
    if loan_amnt <= 0:
        errors.append("Loan amount must be greater than zero.")
    if annual_inc <= 0:
        errors.append("Annual income must be greater than zero.")
    if dti < 0 or dti > 100:
        errors.append("Debt-to-Income Ratio must be between 0 and 100.")

    if errors:
        return templates.TemplateResponse(
            "apply.html",
            {"request": request, "user": user, "success": None, "errors": errors},
        )

    application = LoanApplication(
        loan_amnt=loan_amnt,
        int_rate=int_rate,
        annual_inc=annual_inc,
        dti=dti,
        revol_bal=revol_bal,
        revol_util=revol_util,
        total_bal_ex_mort=total_bal_ex_mort,
        bc_util=bc_util,
        bc_open_to_buy=bc_open_to_buy,
        total_bc_limit=total_bc_limit,
        mo_sin_old_rev_tl_op=mo_sin_old_rev_tl_op,
        mo_sin_old_il_acct=mo_sin_old_il_acct,
        tot_cur_bal=tot_cur_bal,
        avg_cur_bal=avg_cur_bal,
        total_rev_hi_lim=total_rev_hi_lim,
        status=LoanStatus.PENDING,
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    await manager.broadcast(
        {
            "event": "NEW_APPLICATION",
            "id": application.id,
            "amount": application.loan_amnt,
            "status": application.status.value,
        }
    )

    return templates.TemplateResponse(
        "apply.html",
        {
            "request": request,
            "user": user,
            "success": "Your loan application has been submitted and is under review.",
            "errors": None,
        },
    )


def render_application_detail(request: Request, app_id: int, db: Session):
    user = require_role(request, "admin")
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    application = db.query(LoanApplication).filter(LoanApplication.id == app_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    return templates.TemplateResponse(
        "application_detail.html",
        {
            "request": request,
            "user": user,
            "application": application,
        },
    )


async def update_application_status(
    request: Request, app_id: int, status: str, db: Session
):
    user = require_role(request, "admin")
    if not user:
        raise HTTPException(status_code=403)

    application = db.query(LoanApplication).filter(LoanApplication.id == app_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    try:
        application.status = LoanStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status value")

    db.commit()

    await manager.broadcast(
        {
            "event": "STATUS_UPDATE",
            "id": application.id,
            "status": application.status.value,
        }
    )

    return RedirectResponse(url="/applications/" + str(app_id), status_code=303)
