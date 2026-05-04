from fastapi import Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from auth import templates, require_role
from database import get_db, LoanApplication, LoanStatus
from services.ml_services import loan_approve
from ws_manager import manager


def render_apply_page(request: Request, user):
    return templates.TemplateResponse(
        request=request,
        name="apply.html",
        context={"request": request, "user": user, "success": None, "errors": None},
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
    if int_rate < 0 or int_rate > 100:
        errors.append("Interest rate must be between 0 and 100.")
    if annual_inc <= 0:
        errors.append("Annual income must be greater than zero.")
    if dti < 0 or dti > 100:
        errors.append("Debt-to-Income Ratio must be between 0 and 100.")
    if revol_bal < 0:
        errors.append("Revolving balance cannot be negative.")
    if revol_util < 0 or revol_util > 100:
        errors.append("Revolving utilization must be between 0 and 100.")
    if total_bal_ex_mort < 0:
        errors.append("Total balance excluding mortgage cannot be negative.")
    if bc_util < 0 or bc_util > 100:
        errors.append("Bankcard utilization must be between 0 and 100.")
    if bc_open_to_buy < 0:
        errors.append("Bankcard open to buy cannot be negative.")
    if total_bc_limit < 0:
        errors.append("Total bankcard limit cannot be negative.")
    if mo_sin_old_rev_tl_op < 0:
        errors.append("Age of oldest revolving account cannot be negative.")
    if mo_sin_old_il_acct < 0:
        errors.append("Age of oldest installment account cannot be negative.")
    if tot_cur_bal < 0:
        errors.append("Total current balance cannot be negative.")
    if avg_cur_bal < 0:
        errors.append("Average current balance cannot be negative.")
    if total_rev_hi_lim < 0:
        errors.append("Revolving high limit cannot be negative.")

    if errors:
        return templates.TemplateResponse(
            request=request,
            name="apply.html",
            context={
                "request": request,
                "user": user,
                "success": None,
                "errors": errors,
            },
        )

    user_input = {
        "loan_amnt": loan_amnt,
        "int_rate": int_rate,
        "annual_inc": annual_inc,
        "dti": dti,
        "revol_bal": revol_bal,
        "revol_util": revol_util,
        "total_bal_ex_mort": total_bal_ex_mort,
        "bc_util": bc_util,
        "bc_open_to_buy": bc_open_to_buy,
        "total_bc_limit": total_bc_limit,
        "mo_sin_old_rev_tl_op": mo_sin_old_rev_tl_op,
        "mo_sin_old_il_acct": mo_sin_old_il_acct,
        "tot_cur_bal": tot_cur_bal,
        "avg_cur_bal": avg_cur_bal,
        "total_rev_hi_lim": total_rev_hi_lim,
    }

    status, predicted_loan = loan_approve(user_input)

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
        status=status,
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

    if status == LoanStatus.APPROVED:
        msg = f"Your loan application has been approved! Predicted eligible amount: ${predicted_loan:,.2f}"
    else:
        msg = f"Your loan application has been rejected. Predicted eligible amount: ${predicted_loan:,.2f}. Please consider applying for a lower amount."

    return templates.TemplateResponse(
        request=request,
        name="apply.html",
        context={
            "request": request,
            "user": user,
            "success": msg,
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
        request=request,
        name="application_detail.html",
        context={
            "request": request,
            "user": user,
            "application": application,
        },
    )
