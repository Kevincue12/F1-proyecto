from pydantic import BaseModel
from typing import Optional, List

# ======== PILOTOS ========
class PilotoBase(BaseModel):
    nombre: str
    numero: int
    nacionalidad: str
    campeonatos_pilotos: int
    escuderia_id: int


class PilotoCreate(PilotoBase):
    pass


class PilotoOut(PilotoBase):
    id: int

    class Config:
        from_attributes = True  # ✅ Actualizado para Pydantic v2


# ======== ESCUDERIAS ========
class EscuderiaBase(BaseModel):
    nombre: str
    pais: str
    campeonatos_constructores: int = 0


class EscuderiaCreate(EscuderiaBase):
    pass


class Escuderia(EscuderiaBase):
    id: int
    pilotos: List["PilotoOut"] = []  # ✅ Se pone entre comillas para evitar NameError

    class Config:
        from_attributes = True  # ✅ Actualizado para Pydantic v2
