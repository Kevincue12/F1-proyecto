from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Escuderia(Base):
    __tablename__ = "escuderias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    pais = Column(String, nullable=False)
    campeonatos_constructores = Column(Integer, default=0)

    pilotos = relationship("Piloto", back_populates="escuderia")


class Piloto(Base):
    __tablename__ = "pilotos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    numero = Column(Integer, unique=True, nullable=False)
    nacionalidad = Column(String, nullable=False)
    campeonatos_pilotos = Column(Integer, default=0)
    escuderia_id = Column(Integer, ForeignKey("escuderias.id"))

    escuderia = relationship("Escuderia", back_populates="pilotos")

