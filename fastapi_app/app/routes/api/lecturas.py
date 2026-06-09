from fastapi import APIRouter, HTTPException
from app.models.lectura import LecturaIn
from app.controllers import lectura as ctrl

router = APIRouter(prefix="/api/lecturas", tags=["API"])


@router.get("")
async def listar(sensor: str | None = None, ubicacion: str | None = None):
    docs = await ctrl.listar(sensor, ubicacion)
    return docs


@router.get("/{id}")
async def obtener(id: str):
    doc = await ctrl.obtener(id)
    if not doc:
        raise HTTPException(404, "No encontrado")
    return doc


@router.post("", status_code=201)
async def crear(data: LecturaIn):
    doc = await ctrl.crear(data)
    return doc


@router.put("/{id}")
async def actualizar(id: str, data: LecturaIn):
    doc = await ctrl.actualizar(id, data)
    if not doc:
        raise HTTPException(404, "No encontrado")
    return doc


@router.delete("/{id}")
async def eliminar(id: str):
    ok = await ctrl.eliminar(id)
    if not ok:
        raise HTTPException(404, "No encontrado")
    return {"mensaje": "Eliminado correctamente"}
