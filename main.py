from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
import uuid, shutil, os

import models, schemas, crud, crud_usuarios
from database import SessionLocal, engine
from auth import authenticate_and_create_token, get_current_user


# ======================================================
# FASTAPI
# ======================================================
app = FastAPI(title="F1 Manager")

# STATIC
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ======================================================
# DB SESSION
# ======================================================
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ======================================================
# INDEX
# ======================================================
@app.get("/")
def index():
    return FileResponse("templates/index.html")


# ======================================================
# LOGIN / REGISTER
# ======================================================
@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/form_register")
def form_register(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    if crud_usuarios.get_user_by_username(db, username):
        return RedirectResponse("/register?error=usuario_existente", status_code=303)

    user = schemas.UserCreate(username=username, password=password)
    crud_usuarios.create_user(db, user)

    return RedirectResponse("/login?created=1", status_code=303)


@app.post("/token")
async def login(
    request: Request,
    form: schemas.LoginForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_and_create_token(db, form.username, form.password)

    if not user:
        raise HTTPException(400, "Usuario o contraseña incorrectos")

    token = user["access_token"]

    response = RedirectResponse("/dashboard", status_code=302)
    response.set_cookie("access_token", token, httponly=True, samesite="strict", max_age=3600)
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("access_token")
    return response


# ======================================================
# SAVE IMAGE
# ======================================================
def save_image(upload: UploadFile, folder: str) -> str:
    if not upload:
        return None

    path = f"static/img/{folder}"
    os.makedirs(path, exist_ok=True)

    ext = upload.filename.split(".")[-1]
    name = f"{uuid.uuid4()}.{ext}"

    file_path = f"{path}/{name}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(upload.file, f)

    return name


def get_image_url(request: Request, folder: str, filename: str):
    if not filename:
        return None
    return f"{request.url.scheme}://{request.url.netloc}/static/img/{folder}/{filename}"


# ======================================================
# ESCUDERÍAS
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
    filename = save_image(foto, "escuderias")

    data = schemas.EscuderiaCreate(
        nombre=nombre,
        pais=pais,
        campeonatos_constructores=campeonatos_constructores,
        foto=filename
    )

    return crud.create_escuderia(db, data, owner_id=current_user.id)


@app.get("/escuderias_page", response_class=HTMLResponse)
def escuderias_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    escs = crud.get_escuderias(db, owner_id=current_user.id)

    for esc in escs:
        esc.foto_url = get_image_url(request, "escuderias", esc.foto)

    return templates.TemplateResponse(
        "escuderias.html",
        {"request": request, "user": current_user, "escuderias": escs}
    )


@app.get("/escuderias/{id}/editar_form", response_class=HTMLResponse)
def editar_escuderia_form(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    escuderia = crud.get_escuderia(db, id, owner_id=current_user.id)
    if not escuderia:
        raise HTTPException(404, "Escudería no encontrada")

    escuderia.foto_url = get_image_url(request, "escuderias", escuderia.foto)

    return templates.TemplateResponse(
        "editar_escuderia.html",
        {"request": request, "user": current_user, "escuderia": escuderia}
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

    filename = esc.foto
    if foto and foto.filename.strip():
        filename = save_image(foto, "escuderias")

    data = schemas.EscuderiaCreate(
        nombre=nombre,
        pais=pais,
        campeonatos_constructores=campeonatos_constructores,
        foto=filename
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
# PILOTOS
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

    filename = save_image(foto, "pilotos")

    data = schemas.PilotoCreate(
        nombre=nombre,
        numero=numero,
        nacionalidad=nacionalidad,
        campeonatos_pilotos=campeonatos_pilotos,
        escuderia_id=escuderia_id,
        foto=filename
    )

    return crud.create_piloto(db, data, owner_id=current_user.id)


@app.get("/pilotos_page", response_class=HTMLResponse)
def pilotos_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    pilotos = crud.get_pilotos(db, owner_id=current_user.id)
    escs = crud.get_escuderias(db, owner_id=current_user.id)

    for p in pilotos:
        p.foto_url = get_image_url(request, "pilotos", p.foto)

    return templates.TemplateResponse(
        "pilotos.html",
        {"request": request, "user": current_user, "pilotos": pilotos, "escuderias": escs}
    )


@app.get("/pilotos/{piloto_id}/editar_form", response_class=HTMLResponse)
def editar_piloto_form(
    piloto_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    piloto = crud.get_piloto(db, piloto_id, owner_id=current_user.id)
    if not piloto:
        raise HTTPException(404, "Piloto no encontrado")

    piloto.foto_url = get_image_url(request, "pilotos", piloto.foto)
    escuderias = crud.get_escuderias(db, owner_id=current_user.id)

    return templates.TemplateResponse(
        "editar_piloto.html",
        {"request": request, "user": current_user, "piloto": piloto, "escuderias": escuderias}
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

    piloto_db = crud.get_piloto(db, piloto_id, owner_id=current_user.id)
    if not piloto_db:
        raise HTTPException(404, "Piloto no encontrado")

    filename = piloto_db.foto
    if foto and foto.filename.strip():
        filename = save_image(foto, "pilotos")

    data = schemas.PilotoCreate(
        nombre=nombre,
        numero=numero,
        nacionalidad=nacionalidad,
        campeonatos_pilotos=campeonatos_pilotos,
        escuderia_id=escuderia_id,
        foto=filename
    )

    crud.update_piloto(db, piloto_id, data, owner_id=current_user.id)
    return RedirectResponse("/pilotos_page", status_code=303)


@app.get("/pilotos/{piloto_id}/eliminar")
def eliminar_piloto(
    piloto_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    eliminado = crud.delete_piloto(db, piloto_id, owner_id=current_user.id)
    if not eliminado:
        raise HTTPException(404, "Piloto no encontrado")
    return RedirectResponse("/pilotos_page", status_code=303)


# ======================================================
# GRANDES PREMIOS
# ======================================================
@app.post("/grandes_premios/", response_model=schemas.GranPremioOut)
def crear_gp(
    nombre: str = Form(...),
    fecha: str = Form(...),
    pais: str = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    fecha_date = datetime.strptime(fecha, "%Y-%m-%d").date()
    gp = schemas.GranPremioCreate(nombre=nombre, fecha=fecha_date, pais=pais)

    return crud.create_gran_premio(db, gp, owner_id=current_user.id)


@app.get("/grandes_premios_page", response_class=HTMLResponse)
def grandes_premios_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    gps = crud.get_grandes_premios(db, owner_id=current_user.id)

    return templates.TemplateResponse(
        "grandes_premios.html",
        {"request": request, "user": current_user, "grandes_premios": gps}
    )


# ======================================================
# RESULTADOS
# ======================================================
@app.get("/resultados_page", response_class=HTMLResponse)
def resultados_page(
    request: Request,
    gp_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    gp = crud.get_gran_premio(db, gp_id, owner_id=current_user.id)
    if not gp:
        return RedirectResponse("/grandes_premios_page", status_code=302)

    pilotos = crud.get_pilotos(db, owner_id=current_user.id)
    resultados = crud.get_resultados_por_gp(db, gp_id, owner_id=current_user.id)

    return templates.TemplateResponse(
        "resultados.html",
        {"request": request, "user": current_user, "gp": gp, "pilotos": pilotos, "resultados": resultados}
    )


@app.post("/resultados/", response_model=schemas.ResultadoOut)
def crear_resultado(
    gran_premio_id: int = Form(...),
    piloto_numero: int = Form(...),
    posicion: int = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    data = schemas.ResultadoCreate(
        gran_premio_id=gran_premio_id,
        piloto_numero=piloto_numero,
        posicion=posicion
    )

    return crud.create_resultado(db, data, owner_id=current_user.id)


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
# DASHBOARD
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

    # ASIGNAR URLs de imágenes
    for p in pilotos:
        p.foto_url = get_image_url(request, "pilotos", p.foto)
    for e in escuderias:
        e.foto_url = get_image_url(request, "escuderias", e.foto)

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
# EXPORT
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
