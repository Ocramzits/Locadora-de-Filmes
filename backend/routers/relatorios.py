from typing import List, Optional
from fastapi import APIRouter, Depends
from backend.schemas import ResumoRelatorioResponse, ItemMaisAlugado, ItemClienteAtivo
from backend import crud

router = APIRouter(prefix="/relatorios", tags=["relatorios"])

try:
    from backend.database import get_db
except ImportError:
    get_db = None

def obter_db_dependencia():
    if get_db is not None:
        yield from get_db()
    else:
        yield None

@router.get("/resumo", response_model=ResumoRelatorioResponse)
def obter_resumo(db=Depends(obter_db_dependencia)):
    return crud.obter_resumo_geral(db)

@router.get("/mais-alugados", response_model=List[ItemMaisAlugado])
def obter_mais_alugados(limite: Optional[int] = None, db=Depends(obter_db_dependencia)):
    return crud.obter_mais_alugados(db, limite=limite)

@router.get("/clientes-ativos", response_model=List[ItemClienteAtivo])
def obter_clientes_ativos(limite: Optional[int] = None, db=Depends(obter_db_dependencia)):
    return crud.obter_clientes_ativos(db, limite=limite)
