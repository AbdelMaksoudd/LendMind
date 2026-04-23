from fastapi import Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(directory=str(BASE_DIR / "views"))

# --- Demo Credentials ---
USERS = {
    "admin_user": {"password": "admin123", "role": "admin"},
    "standard_user": {"password": "user456", "role": "user"},
}


# --- Auth helpers ---
def get_current_user(request: Request):
    username = request.session.get("username")
    if not username or username not in USERS:
        return None
    return {"username": username, "role": USERS[username]["role"]}


def require_role(request: Request, role: str):
    user = get_current_user(request)
    if not user or user["role"] != role:
        return None
    return user
