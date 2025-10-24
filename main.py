from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
from fastapi.responses import FileResponse

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API F1 - Pilotos, Escuderías y Grandes Premios")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/escuderias/", response_model=schemas.Escuderia)
def crear_escuderia(escuderia: schemas.EscuderiaCreate, db: Session = Depends(get_db)):
    return crud.create_escuderia(db, escuderia)


@app.get("/escuderias/", response_model=list[schemas.Escuderia])
def listar_escuderias(db: Session = Depends(get_db)):
    return crud.get_escuderias(db)


@app.put("/escuderias/{escuderia_id}", response_model=schemas.Escuderia)
def editar_escuderia(escuderia_id: int, escuderia: schemas.EscuderiaCreate, db: Session = Depends(get_db)):
    result = crud.update_escuderia(db, escuderia_id, escuderia)
    if not result:
        raise HTTPException(status_code=404, detail="Escudería no encontrada")
    return result


@app.delete("/escuderias/{escuderia_id}")
def eliminar_escuderia(escuderia_id: int, db: Session = Depends(get_db)):
    result = crud.delete_escuderia(db, escuderia_id)
    if not result:
        raise HTTPException(status_code=404, detail="Escudería no encontrada")
    return {"mensaje": "Escudería eliminada correctamente"}


@app.post("/pilotos/", response_model=schemas.PilotoOut)
def crear_piloto(piloto: schemas.PilotoCreate, db: Session = Depends(get_db)):

    if not piloto.escuderia_id:
        raise HTTPException(status_code=400, detail="Debe seleccionar una escudería válida.")

    escuderia = db.query(models.Escuderia).filter(models.Escuderia.id == piloto.escuderia_id).first()
    if not escuderia:
        raise HTTPException(status_code=404, detail="La escudería seleccionada no existe.")

    piloto_existente = db.query(models.Piloto).filter(models.Piloto.numero == piloto.numero).first()
    if piloto_existente:
        raise HTTPException(status_code=400, detail=f"Ya existe un piloto con el número {piloto.numero}.")

    if len(escuderia.pilotos) >= 2:
        raise HTTPException(status_code=400, detail="La escudería ya tiene 2 pilotos registrados.")

    return crud.create_piloto(db, piloto)


@app.get("/pilotos/", response_model=list[schemas.PilotoOut])
def listar_pilotos(db: Session = Depends(get_db)):
    return crud.get_pilotos(db)


@app.get("/pilotos/numero/{numero}", response_model=schemas.PilotoOut)
def buscar_por_numero(numero: int, db: Session = Depends(get_db)):
    piloto = crud.get_piloto_por_numero(db, numero)
    if not piloto:
        raise HTTPException(status_code=404, detail="Piloto no encontrado")
    return piloto


@app.put("/pilotos/{piloto_id}", response_model=schemas.PilotoOut)
def editar_piloto(piloto_id: int, piloto: schemas.PilotoCreate, db: Session = Depends(get_db)):

    piloto_existente = db.query(models.Piloto).filter(models.Piloto.id == piloto_id).first()
    if not piloto_existente:
        raise HTTPException(status_code=404, detail="El piloto no existe.")

    if not piloto.escuderia_id:
        raise HTTPException(status_code=400, detail="Debe seleccionar una escudería válida para el piloto.")

    escuderia = db.query(models.Escuderia).filter(models.Escuderia.id == piloto.escuderia_id).first()
    if not escuderia:
        raise HTTPException(status_code=404, detail="La escudería seleccionada no existe.")

    pilotos_escuderia = [p for p in escuderia.pilotos if p.id != piloto_id]
    if len(pilotos_escuderia) >= 2:
        raise HTTPException(status_code=400, detail="La escudería ya tiene 2 pilotos registrados.")

    result = crud.update_piloto(db, piloto_id, piloto)
    return result


@app.delete("/pilotos/{piloto_id}")
def eliminar_piloto(piloto_id: int, db: Session = Depends(get_db)):
    result = crud.delete_piloto(db, piloto_id)
    if not result:
        raise HTTPException(status_code=404, detail="Piloto no encontrado")
    return {"mensaje": "Piloto eliminado correctamente"}


@app.post("/grandes_premios/", response_model=schemas.GranPremioOut)
def crear_gran_premio(gp: schemas.GranPremioCreate, db: Session = Depends(get_db)):
    return crud.create_gran_premio(db, gp)


@app.get("/grandes_premios/", response_model=list[schemas.GranPremioOut])
def listar_grandes_premios(db: Session = Depends(get_db)):
    return crud.get_grandes_premios(db)


@app.post("/resultados/", response_model=schemas.ResultadoOut)
def agregar_resultado(resultado: schemas.ResultadoCreate, db: Session = Depends(get_db)):

    piloto = db.query(models.Piloto).filter(models.Piloto.numero == resultado.piloto_numero).first()
    gp = db.query(models.GranPremio).filter(models.GranPremio.id == resultado.gran_premio_id).first()

    if not piloto:
        raise HTTPException(status_code=404, detail="Piloto no encontrado.")
    if not gp:
        raise HTTPException(status_code=404, detail="Gran Premio no encontrado.")

    resultado_existente = db.query(models.Resultado).filter(
        models.Resultado.gran_premio_id == resultado.gran_premio_id,
        models.Resultado.posicion == resultado.posicion
    ).first()
    if resultado_existente:
        raise HTTPException(
            status_code=400,
            detail=f"Ya hay un piloto registrado en la posición {resultado.posicion} para este GP."
        )

    return crud.create_resultado(db, resultado)


@app.get("/resultados/gp/{gp_id}")
def listar_resultados_gp(gp_id: int, db: Session = Depends(get_db)):
    resultados = crud.get_resultados_por_gp(db, gp_id)
    if not resultados:
        raise HTTPException(status_code=404, detail="No hay resultados para este Gran Premio")
    tabla = [
        {
            "posicion": r.posicion,
            "piloto": r.piloto.nombre,
            "numero": r.piloto.numero,
            "escuderia": r.piloto.escuderia.nombre if r.piloto.escuderia else None
        }
        for r in resultados
    ]
    return sorted(tabla, key=lambda x: x["posicion"])


@app.get("/campeonato/pilotos")
def campeonato_pilotos(db: Session = Depends(get_db)):
    """
    Devuelve la tabla de posiciones del campeonato de pilotos,
    calculando los puntos acumulados según los resultados registrados.
    """
    return crud.get_campeonato_pilotos(db)

@app.get("/reportes/")
def generar_reportes_excel(db: Session = Depends(get_db)):
    mensaje = crud.generar_reportes(db)
    return FileResponse("reportes_f1.xlsx", filename="reportes_f1.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")