from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from fastapi import Form, UploadFile, File

# ======================
# AUTH
# ======================

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


# ======================
# PILOTOS
# ======================

class PilotoBase(BaseModel):
    nombre: str
    numero: int
    nacionalidad: str
    campeonatos_pilotos: int
    escuderia_id: int
    foto: Optional[bytes] = None   # bytes para BD

class PilotoCreate(PilotoBase):
    pass

class PilotoOut(BaseModel):
    id: int
    nombre: str
    numero: int
    nacionalidad: str
    campeonatos_pilotos: int
    escuderia_id: int
    tiene_foto: bool = False       # no enviamos bytes pesados

    class Config:
        from_attributes = True


# ======================
# ESCUDERIAS
# ======================

class EscuderiaBase(BaseModel):
    nombre: str
    pais: str
    campeonatos_constructores: int = 0
    foto: Optional[bytes] = None

class EscuderiaCreate(EscuderiaBase):
    pass

class EscuderiaOut(BaseModel):
    id: int
    nombre: str
    pais: str
    campeonatos_constructores: int
    tiene_foto: bool = False
    pilotos: List[PilotoOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ======================
# GRANDES PREMIOS
# ======================

class GranPremioBase(BaseModel):
    nombre: str
    fecha: date
    pais: Optional[str] = None   # ← agregado porque models.py lo tiene

class GranPremioCreate(GranPremioBase):
    pass

class GranPremioOut(GranPremioBase):
    id: int

    class Config:
        from_attributes = True


# ======================
# RESULTADOS
# ======================

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


# ======================
# FORMULARIOS PARA CREAR (con fotos)
# ======================

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
