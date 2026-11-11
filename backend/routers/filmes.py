from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from backend.schemas import FilmeCreate, FilmeResponse
from models.filme import filmes_iniciais

router = APIRouter(prefix="/filmes", tags=["filmes"])

try:
    from backend.database import get_db
    from backend.models_db import FilmeDB
except ImportError:
    get_db = None
    FilmeDB = None

_filmes_memoria = []

def _inicializar_memoria():
    if not _filmes_memoria:
        for idx, f in enumerate(filmes_iniciais(), start=1):
            _filmes_memoria.append({
                "id": idx,
                "titulo": f["titulo"],
                "categoria": f["categoria"],
                "copias": f["copias"],
                "total_copias": f.get("total_copias", f["copias"]),
                "disponivel": f.get("disponivel", f["copias"] > 0)
            })

def obter_db_dependencia():
    if get_db is not None:
        yield from get_db()
    else:
        yield None

@router.get("", response_model=List[FilmeResponse])
@router.get("/", response_model=List[FilmeResponse])
def listar_filmes(db=Depends(obter_db_dependencia)):
    if db is not None and FilmeDB is not None:
        return db.query(FilmeDB).all()
    _inicializar_memoria()
    return _filmes_memoria

@router.post("", response_model=FilmeResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=FilmeResponse, status_code=status.HTTP_201_CREATED)
def criar_filme(filme: FilmeCreate, db=Depends(obter_db_dependencia)):
    titulo_limpo = filme.titulo.strip()
    if not titulo_limpo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Título não pode ser vazio.")

    total = filme.total_copias if filme.total_copias is not None else filme.copias
    if total < filme.copias:
        total = filme.copias
    disp = filme.copias > 0

    if db is not None and FilmeDB is not None:
        existente = db.query(FilmeDB).filter(FilmeDB.titulo.ilike(titulo_limpo)).first()
        if existente:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filme já cadastrado.")
        novo_filme = FilmeDB(
            titulo=titulo_limpo,
            categoria=filme.categoria.strip(),
            copias=filme.copias,
            total_copias=total,
            disponivel=disp
        )
        db.add(novo_filme)
        db.commit()
        db.refresh(novo_filme)
        return novo_filme

    _inicializar_memoria()
    for f in _filmes_memoria:
        if f["titulo"].strip().lower() == titulo_limpo.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filme já cadastrado.")

    novo_id = len(_filmes_memoria) + 1
    novo = {
        "id": novo_id,
        "titulo": titulo_limpo,
        "categoria": filme.categoria.strip(),
        "copias": filme.copias,
        "total_copias": total,
        "disponivel": disp
    }
    _filmes_memoria.append(novo)
    return novo

@router.get("/{titulo}", response_model=FilmeResponse)
def buscar_filme(titulo: str, db=Depends(obter_db_dependencia)):
    titulo_limpo = titulo.strip()
    if db is not None and FilmeDB is not None:
        filme = db.query(FilmeDB).filter(FilmeDB.titulo.ilike(titulo_limpo)).first()
        if not filme:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filme não encontrado.")
        return filme

    _inicializar_memoria()
    for f in _filmes_memoria:
        if f["titulo"].strip().lower() == titulo_limpo.lower():
            return f
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filme não encontrado.")

@router.delete("/{titulo}")
def remover_filme(titulo: str, db=Depends(obter_db_dependencia)):
    titulo_limpo = titulo.strip()
    if db is not None and FilmeDB is not None:
        filme = db.query(FilmeDB).filter(FilmeDB.titulo.ilike(titulo_limpo)).first()
        if not filme:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filme não encontrado.")
        db.delete(filme)
        db.commit()
        return {"mensagem": "Filme removido com sucesso."}

    _inicializar_memoria()
    for idx, f in enumerate(_filmes_memoria):
        if f["titulo"].strip().lower() == titulo_limpo.lower():
            _filmes_memoria.pop(idx)
            return {"mensagem": "Filme removido com sucesso."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filme não encontrado.")
