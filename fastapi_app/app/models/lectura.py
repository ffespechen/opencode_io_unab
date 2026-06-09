from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from bson import ObjectId


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(str(v)):
            raise ValueError("ObjectId inválido")
        return str(v)


class LecturaIn(BaseModel):
    valor: float = Field(..., description="Valor numérico con decimales")
    sensor: str = Field(..., min_length=1, description="Identificador del sensor")
    ubicacion: str = Field(..., min_length=1, description="Ubicación física")
    fecha_hora: datetime = Field(..., description="Fecha y hora ISO8601")
    nodered: bool = Field(..., description="Indica si el origen es NodeRED")


class LecturaOut(LecturaIn):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
