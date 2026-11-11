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
        orm_mode = True

class ClienteBase(BaseModel):
    nome: str

class ClienteCreate(BaseModel):
    nome: str

class ClienteResponse(BaseModel):
    id: Optional[int] = None
    nome: str

    class Config:
        from_attributes = True
        orm_mode = True
