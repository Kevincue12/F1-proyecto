from pydantic import BaseModel
from typing import Optional, List


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
        from_attributes = True  # antes orm_mode = True


class EscuderiaBase(BaseModel):
    nombre: str
    pais: str
    campeonatos_constructores: int = 0


class EscuderiaCreate(EscuderiaBase):
    pass


class Escuderia(EscuderiaBase):
    id: int
    pilotos: List["PilotoOut"] = []

    class Config:
        from_attributes = True


class GranPremioBase(BaseModel):
    nombre: str
    pais: str


class GranPremioCreate(GranPremioBase):
    pass


class GranPremioOut(GranPremioBase):
    id: int

    class Config:
        from_attributes = True


class ResultadoBase(BaseModel):
    posicion: int


class ResultadoCreate(ResultadoBase):
    piloto_numero: int
    gran_premio_id: int


class ResultadoOut(ResultadoBase):
    id: int
    piloto_id: int
    gran_premio_id: int

    class Config:
        from_attributes = True
