from datetime import datetime
from bson import ObjectId
from app.config.db import get_collection
from app.models.lectura import LecturaIn, LecturaOut


def _serialize(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def listar(sensor: str | None = None, ubicacion: str | None = None) -> list[dict]:
    filtro = {}
    if sensor:
        filtro["sensor"] = sensor
    if ubicacion:
        filtro["ubicacion"] = ubicacion
    cursor = get_collection().find(filtro).sort("fecha_hora", -1)
    docs = await cursor.to_list(length=None)
    return [_serialize(d) for d in docs]


async def obtener(id: str) -> dict | None:
    doc = await get_collection().find_one({"_id": ObjectId(id)})
    return _serialize(doc)


async def crear(data: LecturaIn) -> dict:
    doc = data.model_dump()
    doc["fecha_hora"] = doc["fecha_hora"].isoformat()
    result = await get_collection().insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc


async def actualizar(id: str, data: LecturaIn) -> dict | None:
    doc = data.model_dump()
    doc["fecha_hora"] = doc["fecha_hora"].isoformat()
    result = await get_collection().find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": doc},
        return_document=True,
    )
    return _serialize(result)


async def eliminar(id: str) -> bool:
    result = await get_collection().delete_one({"_id": ObjectId(id)})
    return result.deleted_count > 0
