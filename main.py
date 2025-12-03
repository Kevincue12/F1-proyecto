from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Request, Cookie
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
import shutil
import uuid
import os
from jose import JWTError, jwt

import models, schemas, crud, crud_usuarios
from database import SessionLocal, engine

# === IMPORTS CORREGIDOS ===
from auth import authenticate_and_create_token, create_access_token, get_current_user

# ==========================================
# CONFIG JWT
# ==========================================
SECRET_KEY = "supersecreto"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ==========================================
# FASTAPI
# ==========================================
app = FastAPI(title="API F1 - Pilotos, Escuderías y Grandes Premios (con usuarios)")

# ==========================================
# STATIC Y TEMPLATES
# ==========================================
os.makedirs("static/uploads/escuderias", exist_ok=True)
os.makedirs("static/uploads/pilotos", exist_ok=True)
os.makedirs("static/img", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ==========================================
# DB
# ==========================================
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# FRONTEND PAGES
# ==========================================
@app.get("/")
def index():
    return FileResponse("templates/index.html")


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# ==========================================
# REGISTRO FORM
# ==========================================
@app.post("/form_register")
def form_register(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = crud_usuarios.get_user_by_username(db, username)
    if user:
        return RedirectResponse("/register?error=usuario_existente", status_code=303)

    new_user = schemas.UserCreate(username=username, password=password)
    crud_usuarios.create_user(db, new_user)

    return RedirectResponse("/login?created=1", status_code=303)


# ==========================================
# LOGIN – CREA COOKIE
# ==========================================
@app.post("/token")
async def login_for_access_token(
    request: Request,
    form_data: schemas.LoginForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_and_create_token(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

    access_token = user["access_token"]

    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="strict",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return response


# ==========================================
# LOGOUT
# ==========================================
@app.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("access_token")
    return response


# ==========================================
# ESCUDERÍAS
# ==========================================
@app.post("/escuderias/", response_model=schemas.EscuderiaOut)
async def crear_escuderia(
    nombre: str = Form(...),
    pais: str = Form(...),
    campeonatos_constructores: int = Form(...),
    foto: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    ruta = None
    if foto:
        nombre_unico = f"{uuid.uuid4()}_{foto.filename}"
        ruta = f"static/uploads/escuderias/{nombre_unico}"
        with open(ruta, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)

    esc_in = schemas.EscuderiaCreate(
        nombre=nombre,
        pais=pais,
        campeonatos_constructores=campeonatos_constructores,
        foto=ruta
    )

    return crud.create_escuderia(db, esc_in, owner_id=current_user.id)


@app.get("/escuderias/", response_model=List[schemas.EscuderiaOut])
def listar_escuderias(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_escuderias(db, owner_id=current_user.id)


# ==========================================
# PILOTOS (endpoint API)
# ==========================================
@app.post("/pilotos/", response_model=schemas.PilotoOut)
async def crear_piloto(
    nombre: str = Form(...),
    numero: int = Form(...),
    nacionalidad: str = Form(...),
    campeonatos_pilotos: int = Form(...),
    escuderia_id: int = Form(...),
    foto: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    ruta = None
    if foto:
        nombre_unico = f"{uuid.uuid4()}_{foto.filename}"
        ruta = f"static/uploads/pilotos/{nombre_unico}"
        with open(ruta, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)

    piloto_in = schemas.PilotoCreate(
        nombre=nombre,
        numero=numero,
        nacionalidad=nacionalidad,
        campeonatos_pilotos=campeonatos_pilotos,
        escuderia_id=escuderia_id,
        foto=ruta
    )

    return crud.create_piloto(db, piloto_in, owner_id=current_user.id)


@app.get("/pilotos/", response_model=List[schemas.PilotoOut])
def listar_pilotos(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_pilotos(db, owner_id=current_user.id)


# ==========================================
# GRANDES PREMIOS
# ==========================================
@app.post("/grandes_premios/", response_model=schemas.GranPremioOut)
def crear_gran_premio(
    gp: schemas.GranPremioCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_gran_premio(db, gp, owner_id=current_user.id)


@app.get("/grandes_premios/", response_model=List[schemas.GranPremioOut])
def listar_grandes_premios(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_grandes_premios(db, owner_id=current_user.id)


# ==========================================
# RESULTADOS
# ==========================================
@app.post("/resultados/", response_model=schemas.ResultadoOut)
def agregar_resultado(
    resultado: schemas.ResultadoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_resultado(db, resultado, owner_id=current_user.id)


# ==========================================
# CAMPEONATO PILOTOS
# ==========================================
@app.get("/campeonato/pilotos", response_model=List[schemas.CampeonatoFila])
def campeonato_pilotos(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_campeonato_pilotos(db, owner_id=current_user.id)


# ==========================================
# DASHBOARD (Sin formulario de pilotos)
# ==========================================
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    escuderias = crud.get_escuderias(db, owner_id=current_user.id)
    pilotos = crud.get_pilotos(db, owner_id=current_user.id)
    tabla = crud.get_campeonato_pilotos(db, owner_id=current_user.id)

    def norm(path):
        return ("/" + path) if path and not path.startswith("/") else path

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": current_user,
            "escuderias": escuderias,
            "pilotos": pilotos,
            "tabla": tabla
        }
    )


# ==========================================
# PÁGINA /pilotos_page (Crear y listar pilotos)
# ==========================================
@app.get("/pilotos_page", response_class=HTMLResponse)
def pilotos_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    pilotos = crud.get_pilotos(db, owner_id=current_user.id)
    escuderias = crud.get_escuderias(db, owner_id=current_user.id)

    return templates.TemplateResponse(
        "pilotos.html",
        {
            "request": request,
            "user": current_user,
            "pilotos": pilotos,
            "escuderias": escuderias
        }
    )


# ==========================================
# REPORTES EXCEL
# ==========================================
@app.get("/reportes/")
def generar_reportes_excel(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    crud.generar_reportes(db, owner_id=current_user.id)
    return FileResponse(
        "reportes_f1.xlsx",
        filename="reportes_f1.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
