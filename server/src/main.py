from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

from database import init_db
from auth import BASE_DIR
from routers.auth import router as auth_router
from routers.apply import router as apply_router
from routers.dashboard import router as dashboard_router
from routers.applications import router as applications_router
from routers.ws import router as ws_router

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="lendmind-mgmt-secret-key-2024")

app.mount("/public", StaticFiles(directory=str(BASE_DIR / "public")), name="public")

init_db()

app.include_router(auth_router)
app.include_router(apply_router)
app.include_router(dashboard_router)
app.include_router(applications_router)
app.include_router(ws_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    print("Server started at http://localhost:8000")
