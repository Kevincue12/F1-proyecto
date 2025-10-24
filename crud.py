from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import Escuderia, Piloto, GranPremio, Resultado
from schemas import (
    EscuderiaCreate,
    PilotoCreate,
    GranPremioCreate,
    ResultadoCreate
)


def get_escuderias(db: Session):
    return db.query(Escuderia).all()


def get_escuderia(db: Session, escuderia_id: int):
    return db.query(Escuderia).filter(Escuderia.id == escuderia_id).first()


def create_escuderia(db: Session, escuderia: EscuderiaCreate):
    db_esc = Escuderia(**escuderia.dict())
    db.add(db_esc)
    db.commit()
    db.refresh(db_esc)
    return db_esc


def delete_escuderia(db: Session, escuderia_id: int):
    esc = get_escuderia(db, escuderia_id)
    if esc:
        db.delete(esc)
        db.commit()
        return esc
    return None


def update_escuderia(db: Session, escuderia_id: int, escuderia_data: EscuderiaCreate):
    esc = get_escuderia(db, escuderia_id)
    if not esc:
        return None
    for key, value in escuderia_data.dict().items():
        setattr(esc, key, value)
    db.commit()
    db.refresh(esc)
    return esc



def get_pilotos(db: Session):
    return db.query(Piloto).all()


def get_piloto_por_numero(db: Session, numero: int):
    return db.query(Piloto).filter(Piloto.numero == numero).first()


def create_piloto(db: Session, piloto: PilotoCreate):
    if not piloto.escuderia_id:
        raise HTTPException(status_code=400, detail="Debe seleccionar una escudería válida.")

    escuderia = db.query(Escuderia).filter(Escuderia.id == piloto.escuderia_id).first()
    if not escuderia:
        raise HTTPException(status_code=404, detail="La escudería seleccionada no existe.")

    if len(escuderia.pilotos) >= 2:
        raise HTTPException(status_code=400, detail=f"La escudería '{escuderia.nombre}' ya tiene 2 pilotos registrados.")

    piloto_existente = db.query(Piloto).filter(Piloto.numero == piloto.numero).first()
    if piloto_existente:
        raise HTTPException(status_code=400, detail=f"Ya existe un piloto con el número {piloto.numero}.")

    db_piloto = Piloto(**piloto.dict())
    db.add(db_piloto)
    db.commit()
    db.refresh(db_piloto)
    return db_piloto


def delete_piloto(db: Session, piloto_id: int):
    piloto = db.query(Piloto).filter(Piloto.id == piloto_id).first()
    if piloto:
        db.delete(piloto)
        db.commit()
        return piloto
    return None


def update_piloto(db: Session, piloto_id: int, piloto_data: PilotoCreate):
    piloto = db.query(Piloto).filter(Piloto.id == piloto_id).first()
    if not piloto:
        return None

    escuderia = db.query(Escuderia).filter(Escuderia.id == piloto_data.escuderia_id).first()
    if not escuderia:
        raise HTTPException(status_code=404, detail="La escudería seleccionada no existe.")

    pilotos_escuderia = [p for p in escuderia.pilotos if p.id != piloto_id]
    if len(pilotos_escuderia) >= 2:
        raise HTTPException(status_code=400, detail="La escudería ya tiene 2 pilotos registrados.")

    for key, value in piloto_data.dict().items():
        setattr(piloto, key, value)
    db.commit()
    db.refresh(piloto)
    return piloto


def create_gran_premio(db: Session, gp: GranPremioCreate):
    nuevo_gp = GranPremio(**gp.dict())
    db.add(nuevo_gp)
    db.commit()
    db.refresh(nuevo_gp)
    return nuevo_gp


def get_grandes_premios(db: Session):
    return db.query(GranPremio).all()



def create_resultado(db: Session, resultado: ResultadoCreate):
    """Agrega un resultado de un GP verificando que no se duplique la posición o el piloto en ese GP"""

    if not resultado.posicion or not resultado.gran_premio_id or not resultado.piloto_numero:
        raise HTTPException(status_code=400, detail="Todos los campos (posición, piloto y Gran Premio) son obligatorios.")

    piloto = db.query(Piloto).filter(Piloto.numero == resultado.piloto_numero).first()
    if not piloto:
        raise HTTPException(status_code=404, detail="Piloto no encontrado.")

    gp = db.query(GranPremio).filter(GranPremio.id == resultado.gran_premio_id).first()
    if not gp:
        raise HTTPException(status_code=404, detail="Gran Premio no encontrado.")

    existente = db.query(Resultado).filter(
        Resultado.piloto_id == piloto.id,
        Resultado.gran_premio_id == gp.id
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="El piloto ya tiene un resultado en este GP.")

    posicion_ocupada = db.query(Resultado).filter(
        Resultado.gran_premio_id == gp.id,
        Resultado.posicion == resultado.posicion
    ).first()
    if posicion_ocupada:
        raise HTTPException(status_code=400, detail=f"La posición {resultado.posicion} ya está ocupada en este GP.")

    nuevo_res = Resultado(
        piloto_id=piloto.id,
        gran_premio_id=gp.id,
        posicion=resultado.posicion
    )
    db.add(nuevo_res)
    db.commit()
    db.refresh(nuevo_res)
    return nuevo_res


def get_resultados_por_gp(db: Session, gp_id: int):
    """Obtiene todos los resultados de un Gran Premio específico."""
    return db.query(Resultado).filter(Resultado.gran_premio_id == gp_id).all()


def get_campeonato_pilotos(db: Session):
    """
    Calcula la tabla de posiciones del campeonato de pilotos según
    los puntos acumulados por cada posición.
    """
    puntos_por_posicion = {
        1: 25, 2: 18, 3: 15, 4: 12, 5: 10,
        6: 8, 7: 6, 8: 4, 9: 2, 10: 1
    }

    pilotos = db.query(Piloto).all()
    tabla = []

    for p in pilotos:
        puntos = sum(puntos_por_posicion.get(r.posicion, 0) for r in p.resultados)
        tabla.append({
            "piloto": p.nombre,
            "numero": p.numero,
            "escuderia": p.escuderia.nombre if p.escuderia else None,
            "puntos": puntos
        })

    tabla_ordenada = sorted(tabla, key=lambda x: x["puntos"], reverse=True)
    for i, piloto in enumerate(tabla_ordenada, start=1):
        piloto["puesto"] = i

    return tabla_ordenada
