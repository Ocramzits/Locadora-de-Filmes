from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from backend.database import Base


class FilmeDB(Base):
    __tablename__ = "filmes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String, unique=True, index=True, nullable=False)
    categoria = Column(String, nullable=False)
    copias = Column(Integer, nullable=False, default=1)
    total_copias = Column(Integer, nullable=False, default=1)
    disponivel = Column(Boolean, nullable=False, default=True)

    locacoes = relationship("LocacaoDB", back_populates="filme", cascade="all, delete-orphan")


class ClienteDB(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, unique=True, index=True, nullable=False)

    locacoes = relationship("LocacaoDB", back_populates="cliente", cascade="all, delete-orphan")


class LocacaoDB(Base):
    __tablename__ = "locacoes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filme_id = Column(Integer, ForeignKey("filmes.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    data_locacao = Column(DateTime, nullable=False, default=datetime.utcnow)
    data_devolucao = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="PENDENTE")
    observacao = Column(String, nullable=True, default="")

    filme = relationship("FilmeDB", back_populates="locacoes")
    cliente = relationship("ClienteDB", back_populates="locacoes")
