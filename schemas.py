from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from fastapi import Form


# ------------- Auth -------------
class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# Para el dependency del /token (emula OAuth2PasswordRequestForm sin importar python-multipart)
class LoginForm:
    def __init__(self, username: str = Form(...), password: str = Form(...)):
        self.username = username
        self.password = password


# ------------- Dominios F1 -------------
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
        from_attributes = True


class EscuderiaBase(BaseModel):
    nombre: str
    pais: str
    campeonatos_constructores: int = 0


class EscuderiaCreate(EscuderiaBase):
    pass


class EscuderiaOut(EscuderiaBase):
    id: int
    pilotos: List["PilotoOut"] = Field(default_factory=list)

    class Config:
        from_attributes = True


class GranPremioBase(BaseModel):
    nombre: str
    pais: str
    fecha: date


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


class ResultadoTabla(BaseModel):
    posicion: int
    piloto: str
    numero: int
    escuderia: Optional[str]


class CampeonatoFila(BaseModel):
    puesto: int
    piloto: str
    numero: int
    escuderia: Optional[str]
    puntos: int
