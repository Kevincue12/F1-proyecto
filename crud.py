from sqlalchemy.orm import Session
from models import Escuderia, Piloto
from schemas import EscuderiaCreate, PilotoCreate
from fastapi import HTTPException

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
        raise HTTPException(
            status_code=400,
            detail="Por favor seleccione alguna escudería disponible."
        )
    
    escuderia = db.query(Escuderia).filter(Escuderia.id == piloto.escuderia_id).first()
    if not escuderia:
        raise HTTPException(
            status_code=404,
            detail="La escudería seleccionada no existe."
        )
    
    if len(escuderia.pilotos) >= 2:
        raise HTTPException(
            status_code=400,
            detail=f"La escudería '{escuderia.nombre}' ya tiene 2 pilotos asignados."
        )

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
    for key, value in piloto_data.dict().items():
        setattr(piloto, key, value)
    db.commit()
    db.refresh(piloto)
    return piloto
