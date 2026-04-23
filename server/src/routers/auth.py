from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import HTMLResponse

from controllers.auth_controller import render_login_page, handle_login, handle_logout, resolve_root

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return resolve_root(request)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return render_login_page(request)


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
):
    return handle_login(request, username, password)


@router.get("/logout")
async def logout(request: Request):
    return handle_logout(request)
