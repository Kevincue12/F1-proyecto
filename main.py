from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

import models, schemas, crud, crud_usuarios
from database import SessionLocal, engine
from auth import get_current_user, oauth2_scheme, authenticate_and_create_token

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API F1 - Pilotos, Escuderías y Grandes Premios (con usuarios)")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Autenticación y registro ----------
@app.post("/users/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud_usuarios.get_user_by_username(db, user_in.username)
    if user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe.")
    return crud_usuarios.create_user(db, user_in)


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: schemas.LoginForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint OAuth2 para obtener JWT.
    """
    token = authenticate_and_create_token(db, form_data.username, form_data.password)
    if not token:
        raise HTTPException(status_code=400, detail="Usuario o contraseña inválidos.")
    return token


# ---------- Escuderías ----------
@app.post("/escuderias/", response_model=schemas.EscuderiaOut)
def crear_escuderia(
    escuderia: schemas.EscuderiaCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_escuderia(db, escuderia, owner_id=current_user.id)


@app.get("/escuderias/", response_model=List[schemas.EscuderiaOut])
def listar_escuderias(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_escuderias(db, owner_id=current_user.id)


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


# ---------- Pilotos ----------
@app.post("/pilotos/", response_model=schemas.PilotoOut)
def crear_piloto(
    piloto: schemas.PilotoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_piloto(db, piloto, owner_id=current_user.id)


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


# ---------- Grandes Premios ----------
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


# ---------- Resultados ----------
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


@app.get("/reportes/")
def generar_reportes_excel(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    mensaje = crud.generar_reportes(db, owner_id=current_user.id)
    return FileResponse(
        "reportes_f1.xlsx",
        filename="reportes_f1.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
