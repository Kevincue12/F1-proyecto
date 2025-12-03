from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
import shutil
import uuid
import os

import models, schemas, crud, crud_usuarios
from database import SessionLocal, engine
from auth import get_current_user, authenticate_and_create_token

# ----------------------------------------------------
# APP
# ----------------------------------------------------
app = FastAPI(title="API F1 - Pilotos, Escuderías y Grandes Premios (con usuarios)")

# ----------------------------------------------------
# ARCHIVOS ESTÁTICOS Y TEMPLATES
# ----------------------------------------------------
# asegúrate de tener: static/uploads/escuderias  y static/uploads/pilotos  y static/img
os.makedirs("static/uploads/escuderias", exist_ok=True)
os.makedirs("static/uploads/pilotos", exist_ok=True)
os.makedirs("static/img", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ----------------------------------------------------
# DATABASE
# ----------------------------------------------------
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------------------------------
# FRONTEND - PAGES: index, login, register
# ----------------------------------------------------
@app.get("/", response_class=FileResponse)
def serve_index_html():
    # si prefieres usar template: return templates.TemplateResponse("index.html", {"request": request})
    return FileResponse("templates/index.html")


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# Form handler para registro desde el formulario HTML (usa Form, luego redirige a login)
@app.post("/form_register")
def form_register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = crud_usuarios.get_user_by_username(db, username)
    if user:
        # redirigir de vuelta a register con mensaje (simple)
        return RedirectResponse(url="/register?error=usuario_existente", status_code=303)
    # crear usuario
    user_in = schemas.UserCreate(username=username, password=password)
    new_user = crud_usuarios.create_user(db, user_in)
    return RedirectResponse(url="/login?created=1", status_code=303)


# ----------------------------------------------------
# USUARIOS (AUTH) - API
# ----------------------------------------------------
@app.post("/users/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud_usuarios.get_user_by_username(db, user_in.username)
    if user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe.")
    return crud_usuarios.create_user(db, user_in)


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: schemas.LoginForm = Depends(), db: Session = Depends(get_db)):
    token = authenticate_and_create_token(db, form_data.username, form_data.password)
    if not token:
        raise HTTPException(status_code=400, detail="Usuario o contraseña inválidos.")
    return token

# ----------------------------------------------------
# ESCUDERÍAS (CON FOTO)
# ----------------------------------------------------
@app.post("/escuderias/", response_model=schemas.EscuderiaOut)
async def crear_escuderia(
    nombre: str = Form(...),
    pais: str = Form(...),
    campeonatos_constructores: int = Form(...),
    foto: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ruta_foto = None

    if foto:
        nombre_unico = f"{uuid.uuid4()}_{foto.filename}"
        ruta_foto = f"static/uploads/escuderias/{nombre_unico}"

        with open(ruta_foto, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)

    escuderia_data = schemas.EscuderiaCreate(
        nombre=nombre,
        pais=pais,
        campeonatos_constructores=campeonatos_constructores,
        foto=ruta_foto,
    )

    return crud.create_escuderia(db, escuderia_data, owner_id=current_user.id)


@app.get("/escuderias/", response_model=List[schemas.EscuderiaOut])
def listar_escuderias(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_escuderias(db, owner_id=current_user.id)


# ----------------------------------------------------
# PILOTOS (CON FOTO)
# ----------------------------------------------------
@app.post("/pilotos/", response_model=schemas.PilotoOut)
async def crear_piloto(
    nombre: str = Form(...),
    numero: int = Form(...),
    nacionalidad: str = Form(...),
    campeonatos_pilotos: int = Form(...),
    escuderia_id: int = Form(...),
    foto: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ruta_foto = None

    if foto:
        nombre_unico = f"{uuid.uuid4()}_{foto.filename}"
        ruta_foto = f"static/uploads/pilotos/{nombre_unico}"

        with open(ruta_foto, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)

    piloto_data = schemas.PilotoCreate(
        nombre=nombre,
        numero=numero,
        nacionalidad=nacionalidad,
        campeonatos_pilotos=campeonatos_pilotos,
        escuderia_id=escuderia_id,
        foto=ruta_foto
    )

    return crud.create_piloto(db, piloto_data, owner_id=current_user.id)


@app.get("/pilotos/", response_model=List[schemas.PilotoOut])
def listar_pilotos(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_pilotos(db, owner_id=current_user.id)


@app.get("/pilotos/numero/{numero}", response_model=schemas.PilotoOut)
def buscar_por_numero(
    numero: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    piloto = crud.get_piloto_por_numero(db, numero, owner_id=current_user.id)
    if not piloto:
        raise HTTPException(status_code=404, detail="Piloto no encontrado")
    return piloto

# ----------------------------------------------------
# CRUD ESCUDERÍAS Y PILOTOS
# ----------------------------------------------------
@app.put("/escuderias/{escuderia_id}", response_model=schemas.EscuderiaOut)
def editar_escuderia(
    escuderia_id: int,
    escuderia: schemas.EscuderiaCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    result = crud.update_escuderia(db, escuderia_id, escuderia, owner_id=current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Escudería no encontrada")
    return result


@app.delete("/escuderias/{escuderia_id}")
def eliminar_escuderia(
    escuderia_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    result = crud.delete_escuderia(db, escuderia_id, owner_id=current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Escudería no encontrada")
    return {"mensaje": "Escudería eliminada correctamente"}


@app.put("/pilotos/{piloto_id}", response_model=schemas.PilotoOut)
def editar_piloto(
    piloto_id: int,
    piloto: schemas.PilotoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    result = crud.update_piloto(db, piloto_id, piloto, owner_id=current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Piloto no encontrado")
    return result


@app.delete("/pilotos/{piloto_id}")
def eliminar_piloto(
    piloto_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    result = crud.delete_piloto(db, piloto_id, owner_id=current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Piloto no encontrado")
    return {"mensaje": "Piloto eliminado correctamente"}


# ----------------------------------------------------
# GRANDES PREMIOS
# ----------------------------------------------------
@app.post("/grandes_premios/", response_model=schemas.GranPremioOut)
def crear_gran_premio(
    gp: schemas.GranPremioCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_gran_premio(db, gp, owner_id=current_user.id)


@app.get("/grandes_premios/", response_model=List[schemas.GranPremioOut])
def listar_grandes_premios(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_grandes_premios(db, owner_id=current_user.id)


# ----------------------------------------------------
# RESULTADOS
# ----------------------------------------------------
@app.post("/resultados/", response_model=schemas.ResultadoOut)
def agregar_resultado(
    resultado: schemas.ResultadoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_resultado(db, resultado, owner_id=current_user.id)


@app.get("/resultados/gp/{gp_id}", response_model=List[schemas.ResultadoTabla])
def listar_resultados_gp(
    gp_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    resultados = crud.get_resultados_por_gp(db, gp_id, owner_id=current_user.id)
    if not resultados:
        raise HTTPException(status_code=404, detail="No hay resultados para este Gran Premio")

    tabla = [
        {
            "posicion": r.posicion,
            "piloto": r.piloto.nombre,
            "numero": r.piloto.numero,
            "escuderia": r.piloto.escuderia.nombre if r.piloto.escuderia else None,
        }
        for r in resultados
    ]

    return sorted(tabla, key=lambda x: x["posicion"])


@app.get("/campeonato/pilotos", response_model=List[schemas.CampeonatoFila])
def campeonato_pilotos(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_campeonato_pilotos(db, owner_id=current_user.id)


# ----------------------------------------------------
# DASHBOARD (FRONTEND) - requiere autenticación
# ----------------------------------------------------
@app.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    escuderias = crud.get_escuderias(db, owner_id=current_user.id)
    pilotos = crud.get_pilotos(db, owner_id=current_user.id)

    # Normalize image urls for template (if stored like "static/..." we want "/static/...")
    def norm(path):
        return ("/" + path) if path and not path.startswith("/") else path

    esc_data = [
        {"id": e.id, "nombre": e.nombre, "pais": e.pais, "foto": norm(e.foto)}
        for e in escuderias
    ]
    pil_data = [
        {"id": p.id, "nombre": p.nombre, "numero": p.numero, "escuderia": p.escuderia.nombre if p.escuderia else None, "foto": norm(p.foto)}
        for p in pilotos
    ]

    return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user, "escuderias": esc_data, "pilotos": pil_data})


# ----------------------------------------------------
# REPORTES EXCEL
# ----------------------------------------------------
@app.get("/reportes/")
def generar_reportes_excel(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    crud.generar_reportes(db, owner_id=current_user.id)
    return FileResponse(
        "reportes_f1.xlsx",
        filename="reportes_f1.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
