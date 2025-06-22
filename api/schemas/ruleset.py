from pydantic import BaseModel
from typing import Any

class RulesetBase(BaseModel):
    nombre: str
    descripcion: str
    reglas_json: Any
    contexto_json: Any
    activo: bool = True

class RulesetCreate(RulesetBase):
    pass

class RulesetUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    reglas_json: Any | None = None
    contexto_json: Any | None = None
    activo: bool | None = None

class RulesetOut(RulesetBase):
    id: int

    class Config:
        from_attributes = True
