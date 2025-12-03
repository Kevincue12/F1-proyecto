from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
import shutil
import uuid
import os

import models, schemas, crud, crud_usuarios
from database import SessionLocal, engine
from auth import authenticate_and_create_token, get_current_user

# ======================================================
# CONFIG FASTAPI
# ======================================================
app = FastAPI(title="F1 Manager")

# ======================================================
# STATIC FILES
# ======================================================
os.makedirs("static/uploads/escuderias", exist_ok=True)
os.makedirs("static/uploads/pilotos", exist_ok=True)
os.makedirs("static/img", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ======================================================
# DATABASE
# ======================================================
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ======================================================
# PÁGINAS BASE
# ======================================================
@app.get("/")
def index():
    return FileResponse("templates/index.html")


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# ======================================================
# REGISTRO
# ======================================================
@app.post("/form_register")
def form_register(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    exists = crud_usuarios.get_user_by_username(db, username)
    if exists:
        return RedirectResponse("/register?error=usuario_existente", status_code=303)

    usuario = schemas.UserCreate(username=username, password=password)
    crud_usuarios.create_user(db, usuario)

    return RedirectResponse("/login?created=1", status_code=303)

# ======================================================
# LOGIN – CREA COOKIE
# ======================================================
@app.post("/token")
async def login_for_access_token(
    request: Request,
    form: schemas.LoginForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_and_create_token(db, form.username, form.password)

    if not user:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

    token = user["access_token"]

    response = RedirectResponse("/dashboard", status_code=302)
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        samesite="strict",
        max_age=60 * 60
    )

    return response


# ======================================================
# LOGOUT
# ======================================================
@app.get("/logout")
def logout():
    resp = RedirectResponse("/", status_code=302)
    resp.delete_cookie("access_token")
    return resp


# ======================================================
# ESCUDERÍAS – API
# ======================================================
@app.post("/escuderias/", response_model=schemas.EscuderiaOut)
async def crear_escuderia(
    nombre: str = Form(...),
    pais: str = Form(...),
    campeonatos_constructores: int = Form(0),
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

    esc_data = schemas.EscuderiaCreate(
        nombre=nombre,
        pais=pais,
        campeonatos_constructores=campeonatos_constructores,
        foto=ruta
    )

    return crud.create_escuderia(db, esc_data, owner_id=current_user.id)


@app.get("/escuderias/", response_model=List[schemas.EscuderiaOut])
def listar_escuderias(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_escuderias(db, owner_id=current_user.id)


# ======================================================
# ESCUDERÍAS – PÁGINA HTML
# ======================================================
@app.get("/escuderias_page", response_class=HTMLResponse)
def escuderias_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    escs = crud.get_escuderias(db, owner_id=current_user.id)
    return templates.TemplateResponse(
        "escuderias.html",
        {"request": request, "user": current_user, "escuderias": escs}
    )


# ======================================================
# ESCUDERÍAS – EDITAR / ELIMINAR
# ======================================================
@app.get("/escuderias/{id}/editar_form", response_class=HTMLResponse)
def editar_escuderia_form(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    esc = crud.get_escuderia(db, id, owner_id=current_user.id)
    if not esc:
        return RedirectResponse("/escuderias_page", status_code=302)

    return templates.TemplateResponse(
        "editar_escuderia.html",
        {"request": request, "user": current_user, "escuderia": esc}
    )


@app.post("/escuderias/{id}/editar")
async def editar_escuderia(
    id: int,
    nombre: str = Form(...),
    pais: str = Form(...),
    campeonatos_constructores: int = Form(...),
    foto: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    esc = crud.get_escuderia(db, id, owner_id=current_user.id)
    if not esc:
        raise HTTPException(404, "Escudería no encontrada")

    # --- conservar foto actual ---
    ruta = esc.foto

    # --- SOLO si realmente subió foto nueva ---
    if foto and foto.filename and foto.filename.strip():
        nombre_unico = f"{uuid.uuid4()}_{foto.filename}"
        ruta = f"static/uploads/escuderias/{nombre_unico}"
        with open(ruta, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)

    data = schemas.EscuderiaCreate(
        nombre=nombre,
        pais=pais,
        campeonatos_constructores=campeonatos_constructores,
        foto=ruta
    )

    crud.update_escuderia(db, id, data, owner_id=current_user.id)

    return RedirectResponse("/escuderias_page", status_code=303)

@app.post("/escuderias/{id}/eliminar")
def eliminar_escuderia(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    eliminado = crud.delete_escuderia(db, id, owner_id=current_user.id)
    if not eliminado:
        raise HTTPException(404, "Escudería no encontrada")

    return RedirectResponse("/escuderias_page", status_code=303)


# ======================================================
# PILOTOS – API
# ======================================================
@app.post("/pilotos/", response_model=schemas.PilotoOut)
async def crear_piloto(
    nombre: str = Form(...),
    numero: int = Form(...),
    nacionalidad: str = Form(...),
    campeonatos_pilotos: int = Form(0),
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

    data = schemas.PilotoCreate(
        nombre=nombre,
        numero=numero,
        nacionalidad=nacionalidad,
        campeonatos_pilotos=campeonatos_pilotos,
        escuderia_id=escuderia_id,
        foto=ruta
    )

    return crud.create_piloto(db, data, owner_id=current_user.id)


@app.get("/pilotos/", response_model=List[schemas.PilotoOut])
def listar_pilotos(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_pilotos(db, owner_id=current_user.id)


# ======================================================
# PILOTOS – PÁGINA HTML
# ======================================================
@app.get("/pilotos_page", response_class=HTMLResponse)
def pilotos_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    pilotos = crud.get_pilotos(db, owner_id=current_user.id)
    escs = crud.get_escuderias(db, owner_id=current_user.id)

    return templates.TemplateResponse(
        "pilotos.html",
        {"request": request, "user": current_user, "pilotos": pilotos, "escuderias": escs}
    )


# ======================================================
# PILOTOS – EDITAR / ELIMINAR
# ======================================================
@app.get("/pilotos/{id}/editar_form", response_class=HTMLResponse)
def editar_piloto_form(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    piloto = db.query(models.Piloto).filter(
        models.Piloto.id == id, models.Piloto.owner_id == current_user.id
    ).first()

    if not piloto:
        return RedirectResponse("/pilotos_page", status_code=302)

    escs = crud.get_escuderias(db, owner_id=current_user.id)

    return templates.TemplateResponse(
        "editar_piloto.html",
        {"request": request, "user": current_user, "piloto": piloto, "escuderias": escs}
    )


@app.post("/pilotos/{piloto_id}/editar")
async def editar_piloto(
    piloto_id: int,
    nombre: str = Form(...),
    numero: int = Form(...),
    nacionalidad: str = Form(...),
    campeonatos_pilotos: int = Form(...),
    escuderia_id: int = Form(...),
    foto: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    piloto_db = db.query(models.Piloto).filter(
        models.Piloto.id == piloto_id,
        models.Piloto.owner_id == current_user.id
    ).first()

    if not piloto_db:
        raise HTTPException(status_code=404, detail="Piloto no encontrado")

    # conservar foto actual
    ruta = piloto_db.foto  

    # SOLO si realmente se subió una nueva foto
    if foto and foto.filename and foto.filename.strip():
        nombre_unico = f"{uuid.uuid4()}_{foto.filename}"
        ruta = f"static/uploads/pilotos/{nombre_unico}"
        with open(ruta, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)

    piloto_data = schemas.PilotoCreate(
        nombre=nombre,
        numero=numero,
        nacionalidad=nacionalidad,
        campeonatos_pilotos=campeonatos_pilotos,
        escuderia_id=escuderia_id,
        foto=ruta
    )

    actualizado = crud.update_piloto(db, piloto_id, piloto_data, owner_id=current_user.id)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Piloto no encontrado")

    return RedirectResponse("/pilotos_page", status_code=303)

@app.get("/pilotos/{piloto_id}/eliminar")
def eliminar_piloto(
    piloto_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    eliminado = crud.delete_piloto(db, piloto_id, owner_id=current_user.id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Piloto no encontrado")

    return RedirectResponse("/pilotos_page", status_code=303)



# ======================================================
# GRANDES PREMIOS
# ======================================================
@app.post("/grandes_premios/", response_model=schemas.GranPremioOut)
def crear_gp(
    gp: schemas.GranPremioCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_gran_premio(db, gp, owner_id=current_user.id)


@app.get("/grandes_premios/", response_model=List[schemas.GranPremioOut])
def listar_gp(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_grandes_premios(db, owner_id=current_user.id)


# ======================================================
# RESULTADOS
# ======================================================
@app.post("/resultados/", response_model=schemas.ResultadoOut)
def crear_resultado(
    resultado: schemas.ResultadoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_resultado(db, resultado, owner_id=current_user.id)


# ======================================================
# CAMPEONATO
# ======================================================
@app.get("/campeonato/pilotos")
def campeonato(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_campeonato_pilotos(db, owner_id=current_user.id)


# ======================================================
# DASHBOARD FINAL
# ======================================================
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    escuderias = crud.get_escuderias(db, owner_id=current_user.id)
    pilotos = crud.get_pilotos(db, owner_id=current_user.id)
    tabla = crud.get_campeonato_pilotos(db, owner_id=current_user.id)
    gps = crud.get_grandes_premios(db, owner_id=current_user.id)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": current_user,
            "escuderias": escuderias,
            "pilotos": pilotos,
            "tabla": tabla,
            "grandes_premios": gps
        }
    )


# ======================================================
# EXPORTAR EXCEL
# ======================================================
@app.get("/reportes/")
def reportes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    crud.generar_reportes(db, owner_id=current_user.id)

    return FileResponse(
        "reportes_f1.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="reportes_f1.xlsx"
    )
