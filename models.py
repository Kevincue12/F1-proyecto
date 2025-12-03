from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Relaciones inversas
    escuderias = relationship("Escuderia", back_populates="owner", cascade="all, delete")
    pilotos = relationship("Piloto", back_populates="owner", cascade="all, delete")
    grandes_premios = relationship("GranPremio", back_populates="owner", cascade="all, delete")
    resultados = relationship("Resultado", back_populates="owner", cascade="all, delete")


class Escuderia(Base):
    __tablename__ = "escuderias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True)
    pais = Column(String(100))
    campeonatos_constructores = Column(Integer, default=0)

    # CAMPO DE FOTO CORREGIDO:
    logo = Column(String(255), nullable=True)   # ← DEBE COINCIDIR CON EL main.py

    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    owner = relationship("User", back_populates="escuderias")

    pilotos = relationship("Piloto", back_populates="escuderia", cascade="all, delete")


class Piloto(Base):
    __tablename__ = "pilotos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True)
    numero = Column(Integer, index=True)
    nacionalidad = Column(String(100))
    campeonatos_pilotos = Column(Integer, default=0)

    escuderia_id = Column(Integer, ForeignKey("escuderias.id", ondelete="CASCADE"))

    foto = Column(String(255), nullable=True)  # ← CORRECTO, COINCIDE CON main.py

    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    owner = relationship("User", back_populates="pilotos")

    escuderia = relationship("Escuderia", back_populates="pilotos")
    resultados = relationship("Resultado", back_populates="piloto", cascade="all, delete")


class GranPremio(Base):
    __tablename__ = "grandes_premios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True)
    pais = Column(String(100))
    fecha = Column(Date, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    owner = relationship("User", back_populates="grandes_premios")

    resultados = relationship("Resultado", back_populates="gran_premio", cascade="all, delete")


class Resultado(Base):
    __tablename__ = "resultados"

    id = Column(Integer, primary_key=True, index=True)
    piloto_id = Column(Integer, ForeignKey("pilotos.id", ondelete="CASCADE"))
    gran_premio_id = Column(Integer, ForeignKey("grandes_premios.id", ondelete="CASCADE"))
    posicion = Column(Integer)

    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    owner = relationship("User", back_populates="resultados")

    piloto = relationship("Piloto", back_populates="resultados")
    gran_premio = relationship("GranPremio", back_populates="resultados")
