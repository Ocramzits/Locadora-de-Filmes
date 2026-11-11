from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from backend.schemas import ClienteCreate, ClienteResponse
from models.cliente import clientes_iniciais

router = APIRouter(prefix="/clientes", tags=["clientes"])

try:
    from backend.database import get_db
    from backend.models_db import ClienteDB
except ImportError:
    get_db = None
    ClienteDB = None

_clientes_memoria = []

def _inicializar_memoria():
    if not _clientes_memoria:
        for idx, nome in enumerate(clientes_iniciais(), start=1):
            _clientes_memoria.append({
                "id": idx,
                "nome": nome
            })

def obter_db_dependencia():
    if get_db is not None:
        yield from get_db()
    else:
        yield None

@router.get("", response_model=List[ClienteResponse])
@router.get("/", response_model=List[ClienteResponse])
def listar_clientes(db=Depends(obter_db_dependencia)):
    if db is not None and ClienteDB is not None:
        return db.query(ClienteDB).all()
    _inicializar_memoria()
    return _clientes_memoria

@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_cliente(cliente: ClienteCreate, db=Depends(obter_db_dependencia)):
    nome_limpo = cliente.nome.strip()
    if not nome_limpo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nome não pode ser vazio.")

    if db is not None and ClienteDB is not None:
        existente = db.query(ClienteDB).filter(ClienteDB.nome.ilike(nome_limpo)).first()
        if existente:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cliente já cadastrado.")
        novo_cliente = ClienteDB(nome=nome_limpo)
        db.add(novo_cliente)
        db.commit()
        db.refresh(novo_cliente)
        return novo_cliente

    _inicializar_memoria()
    for c in _clientes_memoria:
        if c["nome"].strip().lower() == nome_limpo.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cliente já cadastrado.")

    novo_id = len(_clientes_memoria) + 1
    novo = {
        "id": novo_id,
        "nome": nome_limpo
    }
    _clientes_memoria.append(novo)
    return novo

@router.delete("/{nome}")
def remover_cliente(nome: str, db=Depends(obter_db_dependencia)):
    nome_limpo = nome.strip()
    if db is not None and ClienteDB is not None:
        cliente = db.query(ClienteDB).filter(ClienteDB.nome.ilike(nome_limpo)).first()
        if not cliente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")
        db.delete(cliente)
        db.commit()
        return {"mensagem": "Cliente removido com sucesso."}

    _inicializar_memoria()
    for idx, c in enumerate(_clientes_memoria):
        if c["nome"].strip().lower() == nome_limpo.lower():
            _clientes_memoria.pop(idx)
            return {"mensagem": "Cliente removido com sucesso."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")
