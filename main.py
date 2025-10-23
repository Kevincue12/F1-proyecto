from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API F1 - Pilotos y Escuderías")


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
        raise HTTPException(
            status_code=400,
            detail="Por favor seleccione alguna escudería disponible."
        )

    escuderia = db.query(models.Escuderia).filter(models.Escuderia.id == piloto.escuderia_id).first()
    if not escuderia:
        raise HTTPException(
            status_code=404,
            detail="La escudería seleccionada no existe."
        )

    if len(escuderia.pilotos) >= 2:
        raise HTTPException(
            status_code=400,
            detail="La escudería ya tiene 2 pilotos registrados."
        )

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

    if not piloto.escuderia_id:
        raise HTTPException(
            status_code=400,
            detail="Debe seleccionar una escudería válida para el piloto."
        )

    escuderia = db.query(models.Escuderia).filter(models.Escuderia.id == piloto.escuderia_id).first()
    if not escuderia:
        raise HTTPException(
            status_code=404,
            detail="La escudería seleccionada no existe."
        )

    pilotos_escuderia = [p for p in escuderia.pilotos if p.id != piloto_id]
    if len(pilotos_escuderia) >= 2:
        raise HTTPException(
            status_code=400,
            detail="La escudería ya tiene 2 pilotos registrados."
        )

    result = crud.update_piloto(db, piloto_id, piloto)
    if not result:
        raise HTTPException(status_code=404, detail="Piloto no encontrado")
    return result


@app.delete("/pilotos/{piloto_id}")
def eliminar_piloto(piloto_id: int, db: Session = Depends(get_db)):
    result = crud.delete_piloto(db, piloto_id)
    if not result:
        raise HTTPException(status_code=404, detail="Piloto no encontrado")
    return {"mensaje": "Piloto eliminado correctamente"}
