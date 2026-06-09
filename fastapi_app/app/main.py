from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.config.db import connect_db, close_db
from app.routes.api.lecturas import router as api_router
from app.routes.web.lecturas import router as web_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(title="IoT FastAPI", lifespan=lifespan)

app.include_router(api_router)
app.include_router(web_router)


@app.exception_handler(404)
async def not_found(request: Request, exc):
    return HTMLResponse("Ruta no encontrada", status_code=404)
