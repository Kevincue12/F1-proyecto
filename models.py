from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

class Escuderia(Base):
    __tablename__ = "escuderias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, index=True)
    pais = Column(String(100))
    campeonatos_constructores = Column(Integer, default=0)

    pilotos = relationship("Piloto", back_populates="escuderia")


class Piloto(Base):
    __tablename__ = "pilotos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True)
    numero = Column(Integer, unique=True, index=True)
    nacionalidad = Column(String(100))
    campeonatos_pilotos = Column(Integer, default=0)
    escuderia_id = Column(Integer, ForeignKey("escuderias.id"))

    escuderia = relationship("Escuderia", back_populates="pilotos")
    resultados = relationship("Resultado", back_populates="piloto")


class GranPremio(Base):
    __tablename__ = "grandes_premios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True)
    pais = Column(String(100))
    fecha = Column(Date, nullable=False)

    resultados = relationship("Resultado", back_populates="gran_premio")


class Resultado(Base):
    __tablename__ = "resultados"

    id = Column(Integer, primary_key=True, index=True)
    piloto_id = Column(Integer, ForeignKey("pilotos.id"))
    gran_premio_id = Column(Integer, ForeignKey("grandes_premios.id"))
    posicion = Column(Integer)

    piloto = relationship("Piloto", back_populates="resultados")
    gran_premio = relationship("GranPremio", back_populates="resultados")
