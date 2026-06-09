from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from datetime import datetime
from app.models.lectura import LecturaIn
from app.controllers import lectura as ctrl
from app.template_utils import templates

router = APIRouter(tags=["Web"])


@router.get("/")
async def index():
    docs = await ctrl.listar()
    return templates.TemplateResponse("index.html", {"lecturas": docs, "error": None})


@router.get("/create")
async def create_form():
    return templates.TemplateResponse("create.html", {"errors": [], "old": {}})


@router.post("/create")
async def create_action(
    valor: float = Form(...),
    sensor: str = Form(...),
    ubicacion: str = Form(...),
    fecha_hora: str = Form(...),
    nodered: bool = Form(...),
):
    try:
        data = LecturaIn(
            valor=valor,
            sensor=sensor,
            ubicacion=ubicacion,
            fecha_hora=datetime.fromisoformat(fecha_hora),
            nodered=nodered,
        )
        await ctrl.crear(data)
        return RedirectResponse(url="/", status_code=302)
    except Exception as e:
        return templates.TemplateResponse(
            "create.html",
            {
                "errors": [{"msg": str(e)}],
                "old": {"valor": valor, "sensor": sensor, "ubicacion": ubicacion, "fecha_hora": fecha_hora, "nodered": str(nodered).lower()},
            },
        )


@router.get("/edit/{id}")
async def edit_form(id: str):
    doc = await ctrl.obtener(id)
    if not doc:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("edit.html", {"lectura": doc, "errors": []})


@router.post("/edit/{id}")
async def edit_action(
    id: str,
    valor: float = Form(...),
    sensor: str = Form(...),
    ubicacion: str = Form(...),
    fecha_hora: str = Form(...),
    nodered: bool = Form(...),
):
    try:
        data = LecturaIn(
            valor=valor,
            sensor=sensor,
            ubicacion=ubicacion,
            fecha_hora=datetime.fromisoformat(fecha_hora),
            nodered=nodered,
        )
        await ctrl.actualizar(id, data)
        return RedirectResponse(url="/", status_code=302)
    except Exception as e:
        return templates.TemplateResponse(
            "edit.html",
            {
                "lectura": {"_id": id, "valor": valor, "sensor": sensor, "ubicacion": ubicacion, "fecha_hora": fecha_hora, "nodered": str(nodered).lower()},
                "errors": [{"msg": str(e)}],
            },
        )


@router.post("/delete/{id}")
async def delete_action(id: str):
    await ctrl.eliminar(id)
    return RedirectResponse(url="/", status_code=302)
