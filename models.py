from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Escuderia(Base):
    __tablename__ = "escuderias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    pais = Column(String)
    campeonatos_constructores = Column(Integer, default=0)

    pilotos = relationship("Piloto", back_populates="escuderia")


class Piloto(Base):
    __tablename__ = "pilotos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    numero = Column(Integer, unique=True, index=True)
    nacionalidad = Column(String)
    campeonatos_pilotos = Column(Integer, default=0)
    escuderia_id = Column(Integer, ForeignKey("escuderias.id"))

    escuderia = relationship("Escuderia", back_populates="pilotos")
    resultados = relationship("Resultado", back_populates="piloto")


class GranPremio(Base):
    __tablename__ = "grandes_premios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    pais = Column(String)

    resultados = relationship("Resultado", back_populates="gran_premio")


class Resultado(Base):
    __tablename__ = "resultados"

    id = Column(Integer, primary_key=True, index=True)
    piloto_id = Column(Integer, ForeignKey("pilotos.id"))
    gran_premio_id = Column(Integer, ForeignKey("grandes_premios.id"))
    posicion = Column(Integer)

    piloto = relationship("Piloto", back_populates="resultados")
    gran_premio = relationship("GranPremio", back_populates="resultados")
