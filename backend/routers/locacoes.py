from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from backend.schemas import LocacaoCreate, DevolucaoCreate, LocacaoResponse
from backend import crud

router = APIRouter(prefix="/locacoes", tags=["locacoes"])

try:
    from backend.database import get_db
except ImportError:
    get_db = None

def obter_db_dependencia():
    if get_db is not None:
        yield from get_db()
    else:
        yield None

@router.post("/alugar", response_model=LocacaoResponse, status_code=status.HTTP_201_CREATED)
def alugar_filme(dados: LocacaoCreate, db=Depends(obter_db_dependencia)):
    titulo = dados.titulo or dados.filme_titulo or ""
    cliente = dados.cliente or dados.cliente_nome or ""
    try:
        return crud.alugar_filme(db, titulo=titulo, cliente_nome=cliente)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/devolver", response_model=LocacaoResponse, status_code=status.HTTP_200_OK)
def devolver_filme(dados: DevolucaoCreate, db=Depends(obter_db_dependencia)):
    titulo = dados.titulo or dados.filme_titulo or ""
    cliente = dados.cliente or dados.cliente_nome or None
    try:
        return crud.devolver_filme(db, titulo=titulo, cliente_nome=cliente)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/pendentes", response_model=List[LocacaoResponse])
def listar_locacoes_pendentes(db=Depends(obter_db_dependencia)):
    return crud.obter_locacoes_pendentes(db)

@router.get("", response_model=List[LocacaoResponse])
@router.get("/", response_model=List[LocacaoResponse])
@router.get("/historico", response_model=List[LocacaoResponse])
def listar_historico_locacoes(limite: Optional[int] = None, db=Depends(obter_db_dependencia)):
    return crud.obter_historico_locacoes(db, limite=limite)
