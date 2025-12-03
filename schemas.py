from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from fastapi import Form, UploadFile, File

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


class LoginForm:
    def __init__(self, username: str = Form(...), password: str = Form(...)):
        self.username = username
        self.password = password


# ------------- Dominios F1 -------------

# ----- Pilotos -----
class PilotoBase(BaseModel):
    nombre: str
    numero: int
    nacionalidad: str
    campeonatos_pilotos: int
    escuderia_id: int
    foto: Optional[str] = None  # Ruta de la imagen


class PilotoCreate(PilotoBase):
    pass


class PilotoOut(PilotoBase):
    id: int

    class Config:
        from_attributes = True


# ----- Escuderías -----
class EscuderiaBase(BaseModel):
    nombre: str
    pais: str
    campeonatos_constructores: int = 0
    foto: Optional[str] = None  # Ruta de la imagen


class EscuderiaCreate(EscuderiaBase):
    pass


class EscuderiaOut(EscuderiaBase):
    id: int
    pilotos: List["PilotoOut"] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ----- Grandes Premios -----
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


# ----- Resultados -----
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


# Resultado para tablas unidas
class ResultadoTabla(BaseModel):
    posicion: int
    piloto: str
    numero: int
    escuderia: Optional[str]


# Tabla de campeonato
class CampeonatoFila(BaseModel):
    puesto: int
    piloto: str
    numero: int
    escuderia: Optional[str]
    puntos: int


# -----------------------------------------------------------
# FORMULARIOS ESPECIALES PARA SUBIR FOTOS
# -----------------------------------------------------------

class EscuderiaForm:
    def __init__(
        self,
        nombre: str = Form(...),
        pais: str = Form(...),
        campeonatos_constructores: int = Form(0),
        foto: UploadFile = File(None)
    ):
        self.nombre = nombre
        self.pais = pais
        self.campeonatos_constructores = campeonatos_constructores
        self.foto = foto


class PilotoForm:
    def __init__(
        self,
        nombre: str = Form(...),
        numero: int = Form(...),
        nacionalidad: str = Form(...),
        campeonatos_pilotos: int = Form(0),
        escuderia_id: int = Form(...),
        foto: UploadFile = File(None)
    ):
        self.nombre = nombre
        self.numero = numero
        self.nacionalidad = nacionalidad
        self.campeonatos_pilotos = campeonatos_pilotos
        self.escuderia_id = escuderia_id
        self.foto = foto
