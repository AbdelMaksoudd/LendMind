from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from controllers.application_controller import render_apply_page, submit_application
from auth import require_role
from database import get_db

router = APIRouter()


@router.get("/apply", response_class=HTMLResponse)
async def apply_page(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, "user")
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return render_apply_page(request, user)


@router.post("/apply")
async def apply_submit(
    request: Request,
    loan_amnt: float = Form(...),
    int_rate: float = Form(...),
    annual_inc: float = Form(...),
    dti: float = Form(...),
    revol_bal: float = Form(...),
    revol_util: float = Form(...),
    total_bal_ex_mort: float = Form(...),
    bc_util: float = Form(...),
    bc_open_to_buy: float = Form(...),
    total_bc_limit: float = Form(...),
    mo_sin_old_rev_tl_op: int = Form(...),
    mo_sin_old_il_acct: int = Form(...),
    tot_cur_bal: float = Form(...),
    avg_cur_bal: float = Form(...),
    total_rev_hi_lim: float = Form(...),
    db: Session = Depends(get_db),
):
    return await submit_application(
        request,
        loan_amnt,
        int_rate,
        annual_inc,
        dti,
        revol_bal,
        revol_util,
        total_bal_ex_mort,
        bc_util,
        bc_open_to_buy,
        total_bc_limit,
        mo_sin_old_rev_tl_op,
        mo_sin_old_il_acct,
        tot_cur_bal,
        avg_cur_bal,
        total_rev_hi_lim,
        db,
    )
