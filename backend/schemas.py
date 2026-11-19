from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class FilmeBase(BaseModel):
    titulo: str
    categoria: str
    copias: int = 1
    total_copias: Optional[int] = None
    disponivel: bool = True

class FilmeCreate(BaseModel):
    titulo: str
    categoria: str
    copias: int = 1
    total_copias: Optional[int] = None

class FilmeResponse(BaseModel):
    id: Optional[int] = None
    titulo: str
    categoria: str
    copias: int
    total_copias: int
    disponivel: bool

    class Config:
        from_attributes = True

class ClienteBase(BaseModel):
    nome: str

class ClienteCreate(BaseModel):
    nome: str

class ClienteResponse(BaseModel):
    id: Optional[int] = None
    nome: str

    class Config:
        from_attributes = True

class LocacaoCreate(BaseModel):
    titulo: Optional[str] = None
    filme_titulo: Optional[str] = None
    cliente: Optional[str] = None
    cliente_nome: Optional[str] = None

class DevolucaoCreate(BaseModel):
    titulo: Optional[str] = None
    filme_titulo: Optional[str] = None
    cliente: Optional[str] = None
    cliente_nome: Optional[str] = None

class LocacaoResponse(BaseModel):
    id: Optional[int] = None
    filme_id: Optional[int] = None
    cliente_id: Optional[int] = None
    titulo: Optional[str] = None
    cliente: Optional[str] = None
    data_locacao: Optional[datetime] = None
    data_devolucao: Optional[datetime] = None
    status: str
    observacao: Optional[str] = ""

    class Config:
        from_attributes = True

class ResumoRelatorioResponse(BaseModel):
    total_transacoes: int
    total_locacoes: int
    total_devolucoes: int
    locacoes_pendentes: int
    total_clientes_distintos: int
    total_filmes_distintos: int

class ItemMaisAlugado(BaseModel):
    titulo: str
    total_locacoes: int

class ItemClienteAtivo(BaseModel):
    cliente: str
    total_locacoes: int
