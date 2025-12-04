from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List

from models import Escuderia, Piloto, GranPremio, Resultado
from schemas import EscuderiaCreate, PilotoCreate, GranPremioCreate, ResultadoCreate
import pandas as pd


# ===================== ESCUDERÍAS =====================
def get_escuderias(db: Session, owner_id: int) -> List[Escuderia]:
    return db.query(Escuderia).filter(Escuderia.owner_id == owner_id).all()


def get_escuderia(db: Session, escuderia_id: int, owner_id: int):
    return (
        db.query(Escuderia)
        .filter(Escuderia.id == escuderia_id, Escuderia.owner_id == owner_id)
        .first()
    )


def create_escuderia(db: Session, escuderia: EscuderiaCreate, owner_id: int):
    existente = (
        db.query(Escuderia)
        .filter(Escuderia.owner_id == owner_id, Escuderia.nombre == escuderia.nombre)
        .first()
    )
    if existente:
        raise HTTPException(status_code=400, detail="Ya tienes una escudería con ese nombre.")

    db_esc = Escuderia(
        owner_id=owner_id,
        nombre=escuderia.nombre,
        pais=escuderia.pais,
        campeonatos_constructores=escuderia.campeonatos_constructores,
        foto=escuderia.foto
    )

    db.add(db_esc)
    db.commit()
    db.refresh(db_esc)
    return db_esc


def update_escuderia(db: Session, escuderia_id: int, escuderia_data: EscuderiaCreate, owner_id: int):
    esc = get_escuderia(db, escuderia_id, owner_id)
    if not esc:
        return None

    if escuderia_data.nombre != esc.nombre:
        dup = (
            db.query(Escuderia)
            .filter(Escuderia.owner_id == owner_id, Escuderia.nombre == escuderia_data.nombre)
            .first()
        )
        if dup:
            raise HTTPException(status_code=400, detail="Ya tienes una escudería con ese nombre.")

    data = escuderia_data.dict()
    for key, value in data.items():
        if key == "foto" and value is None:
            continue
        setattr(esc, key, value)

    db.commit()
    db.refresh(esc)
    return esc


def delete_escuderia(db: Session, escuderia_id: int, owner_id: int):
    esc = get_escuderia(db, escuderia_id, owner_id)
    if esc:
        db.delete(esc)
        db.commit()
        return esc
    return None


# ===================== PILOTOS =====================
def get_pilotos(db: Session, owner_id: int):
    return db.query(Piloto).filter(Piloto.owner_id == owner_id).all()


# 🚀 ESTA ES LA FUNCIÓN QUE HACÍA FALTA
def get_piloto(db: Session, piloto_id: int, owner_id: int):
    return (
        db.query(Piloto)
        .filter(Piloto.id == piloto_id, Piloto.owner_id == owner_id)
        .first()
    )


def get_piloto_por_numero(db: Session, numero: int, owner_id: int):
    return (
        db.query(Piloto)
        .filter(Piloto.owner_id == owner_id, Piloto.numero == numero)
        .first()
    )


def create_piloto(db: Session, piloto: PilotoCreate, owner_id: int):
    if not piloto.escuderia_id:
        raise HTTPException(status_code=400, detail="Debe seleccionar una escudería válida.")

    escuderia = (
        db.query(Escuderia)
        .filter(Escuderia.id == piloto.escuderia_id, Escuderia.owner_id == owner_id)
        .first()
    )
    if not escuderia:
        raise HTTPException(status_code=404, detail="La escudería seleccionada no existe.")

    if len(escuderia.pilotos) >= 2:
        raise HTTPException(status_code=400, detail=f"La escudería '{escuderia.nombre}' ya tiene 2 pilotos.")

    exist = (
        db.query(Piloto)
        .filter(Piloto.owner_id == owner_id, Piloto.numero == piloto.numero)
        .first()
    )
    if exist:
        raise HTTPException(status_code=400, detail=f"Ya tienes un piloto con el número {piloto.numero}.")

    db_piloto = Piloto(
        owner_id=owner_id,
        nombre=piloto.nombre,
        numero=piloto.numero,
        nacionalidad=piloto.nacionalidad,
        campeonatos_pilotos=piloto.campeonatos_pilotos,
        escuderia_id=piloto.escuderia_id,
        foto=piloto.foto
    )

    db.add(db_piloto)
    db.commit()
    db.refresh(db_piloto)
    return db_piloto


def update_piloto(db: Session, piloto_id: int, piloto_data: PilotoCreate, owner_id: int):
    piloto = get_piloto(db, piloto_id, owner_id)
    if not piloto:
        return None

    escuderia = (
        db.query(Escuderia)
        .filter(Escuderia.id == piloto_data.escuderia_id, Escuderia.owner_id == owner_id)
        .first()
    )
    if not escuderia:
        raise HTTPException(status_code=404, detail="La escudería seleccionada no existe.")

    pilotos_esc = [p for p in escuderia.pilotos if p.id != piloto_id]
    if len(pilotos_esc) >= 2:
        raise HTTPException(status_code=400, detail="La escudería ya tiene 2 pilotos.")

    if piloto.numero != piloto_data.numero:
        dup = (
            db.query(Piloto)
            .filter(Piloto.owner_id == owner_id, Piloto.numero == piloto_data.numero)
            .first()
        )
        if dup:
            raise HTTPException(status_code=400, detail=f"Ya tienes un piloto con el número {piloto_data.numero}.")

    data = piloto_data.dict()
    for key, value in data.items():
        if key == "foto" and value is None:
            continue
        setattr(piloto, key, value)

    db.commit()
    db.refresh(piloto)
    return piloto


def delete_piloto(db: Session, piloto_id: int, owner_id: int):
    piloto = get_piloto(db, piloto_id, owner_id)
    if piloto:
        db.delete(piloto)
        db.commit()
        return piloto
    return None


# ===================== GRANDES PREMIOS =====================
def create_gran_premio(db: Session, gp: GranPremioCreate, owner_id: int):
    existente = (
        db.query(GranPremio)
        .filter(GranPremio.owner_id == owner_id, GranPremio.nombre == gp.nombre)
        .first()
    )
    if existente:
        raise HTTPException(status_code=400, detail="Ya tienes un GP con ese nombre.")

    nuevo_gp = GranPremio(owner_id=owner_id, **gp.dict())
    db.add(nuevo_gp)
    db.commit()
    db.refresh(nuevo_gp)
    return nuevo_gp


def get_grandes_premios(db: Session, owner_id: int):
    return db.query(GranPremio).filter(GranPremio.owner_id == owner_id).all()


def get_gran_premio(db: Session, gp_id: int, owner_id: int):
    return (
        db.query(GranPremio)
        .filter(GranPremio.id == gp_id, GranPremio.owner_id == owner_id)
        .first()
    )


# ===================== RESULTADOS =====================
def create_resultado(db: Session, resultado: ResultadoCreate, owner_id: int):
    piloto = (
        db.query(Piloto)
        .filter(Piloto.owner_id == owner_id, Piloto.numero == resultado.piloto_numero)
        .first()
    )
    if not piloto:
        raise HTTPException(status_code=404, detail="Piloto no encontrado.")

    gp = (
        db.query(GranPremio)
        .filter(GranPremio.owner_id == owner_id, GranPremio.id == resultado.gran_premio_id)
        .first()
    )
    if not gp:
        raise HTTPException(status_code=404, detail="Gran Premio no encontrado.")

    conflict = (
        db.query(Resultado)
        .filter(
            Resultado.owner_id == owner_id,
            Resultado.gran_premio_id == gp.id,
            Resultado.piloto_id == piloto.id
        )
        .first()
    )
    if conflict:
        raise HTTPException(status_code=400, detail="El piloto ya tiene resultado en este GP.")

    pos = (
        db.query(Resultado)
        .filter(
            Resultado.owner_id == owner_id,
            Resultado.gran_premio_id == gp.id,
            Resultado.posicion == resultado.posicion
        )
        .first()
    )
    if pos:
        raise HTTPException(status_code=400, detail=f"La posición {resultado.posicion} ya está ocupada.")

    nuevo_res = Resultado(
        owner_id=owner_id,
        piloto_id=piloto.id,
        gran_premio_id=gp.id,
        posicion=resultado.posicion,
    )
    db.add(nuevo_res)
    db.commit()
    db.refresh(nuevo_res)
    return nuevo_res


def get_resultados_por_gp(db: Session, gp_id: int, owner_id: int):
    return (
        db.query(Resultado)
        .filter(Resultado.gran_premio_id == gp_id, Resultado.owner_id == owner_id)
        .all()
    )


# ===================== CAMPEONATO =====================
def get_campeonato_pilotos(db: Session, owner_id: int):
    puntos = {1:25,2:18,3:15,4:12,5:10,6:8,7:6,8:4,9:2,10:1}

    pilotos = db.query(Piloto).filter(Piloto.owner_id == owner_id).all()
    tabla = []

    for p in pilotos:
        total = 0
        for r in p.resultados:
            if r.owner_id == owner_id:
                total += puntos.get(r.posicion, 0)

        tabla.append({
            "piloto": p.nombre,
            "numero": p.numero,
            "escuderia": p.escuderia.nombre if p.escuderia else None,
            "puntos": total,
        })

    tabla = sorted(tabla, key=lambda x: x["puntos"], reverse=True)
    for i, fila in enumerate(tabla, start=1):
        fila["puesto"] = i

    return tabla


# ===================== REPORTES =====================
def generar_reportes(db: Session, owner_id: int):
    esc = db.query(Escuderia).filter(Escuderia.owner_id == owner_id).all()
    df1 = pd.DataFrame(
        [{"ID": e.id, "Nombre": e.nombre, "Pais": e.pais} for e in esc]
    )

    pil = db.query(Piloto).filter(Piloto.owner_id == owner_id).all()
    df2 = pd.DataFrame(
        [
            {
                "ID": p.id,
                "Nombre": p.nombre,
                "Número": p.numero,
                "Escudería": p.escuderia.nombre if p.escuderia else None,
            }
            for p in pil
        ]
    )

    gps = db.query(GranPremio).filter(GranPremio.owner_id == owner_id).all()
    df3 = pd.DataFrame(
        [{"ID": gp.id, "Nombre": gp.nombre, "Pais": gp.pais, "Fecha": gp.fecha} for gp in gps]
    )

    res = db.query(Resultado).filter(Resultado.owner_id == owner_id).all()
    df4 = pd.DataFrame(
        [
            {
                "GP": r.gran_premio.nombre if r.gran_premio else None,
                "Piloto": r.piloto.nombre if r.piloto else None,
                "Escudería": r.piloto.escuderia.nombre if r.piloto and r.piloto.escuderia else None,
                "Posición": r.posicion,
            }
            for r in res
        ]
    )

    puntos = {1:25,2:18,3:15,4:12,5:10,6:8,7:6,8:4,9:2,10:1}
    tabla = []

    for p in pil:
        total = sum(puntos.get(r.posicion, 0) for r in p.resultados if r.owner_id == owner_id)
        tabla.append({
            "Puesto": None,
            "Piloto": p.nombre,
            "Número": p.numero,
            "Escudería": p.escuderia.nombre if p.escuderia else None,
            "Puntos": total,
        })

    tabla = sorted(tabla, key=lambda x: x["Puntos"], reverse=True)
    for i, fila in enumerate(tabla, start=1):
        fila["Puesto"] = i

    df5 = pd.DataFrame(tabla)

    with pd.ExcelWriter("reportes_f1.xlsx", engine="openpyxl") as writer:
        if not df1.empty:
            df1.to_excel(writer, sheet_name="Escuderías", index=False)
        if not df2.empty:
            df2.to_excel(writer, sheet_name="Pilotos", index=False)
        if not df3.empty:
            df3.to_excel(writer, sheet_name="Grandes Premios", index=False)
        if not df4.empty:
            df4.to_excel(writer, sheet_name="Resultados", index=False)
        if not df5.empty:
            df5.to_excel(writer, sheet_name="Campeonato Pilotos", index=False)

    return "Reporte generado"
