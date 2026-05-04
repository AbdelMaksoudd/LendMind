from fastapi import Request, Form, Response
from fastapi.responses import RedirectResponse

from auth import templates, USERS, get_current_user


def render_login_page(request: Request):
    demo_users = [
        {"username": u, "password": info["password"], "role": info["role"]}
        for u, info in USERS.items()
    ]
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request, "error": None, "demo_users": demo_users},
    )


def handle_login(request: Request, username: str, password: str):
    if username in USERS and USERS[username]["password"] == password:
        request.session["username"] = username
        if USERS[username]["role"] == "admin":
            return RedirectResponse(url="/dashboard", status_code=303)
        return RedirectResponse(url="/apply", status_code=303)
    demo_users = [
        {"username": u, "password": info["password"], "role": info["role"]}
        for u, info in USERS.items()
    ]
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "error": "Invalid credentials. Please try again.",
            "demo_users": demo_users,
        },
    )


def handle_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


def resolve_root(request: Request):
    user = get_current_user(request)
    if user:
        if user["role"] == "admin":
            return RedirectResponse(url="/dashboard", status_code=303)
        return RedirectResponse(url="/apply", status_code=303)
    return RedirectResponse(url="/login", status_code=303)
