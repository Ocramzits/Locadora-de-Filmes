from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

try:
    from backend.models_db import FilmeDB, ClienteDB, LocacaoDB
except ImportError:
    FilmeDB = None
    ClienteDB = None
    LocacaoDB = None

_locacoes_memoria: List[Dict[str, Any]] = []

def _obter_dados_memoria_filmes():
    from backend.routers.filmes import _filmes_memoria, _inicializar_memoria
    _inicializar_memoria()
    return _filmes_memoria

def _obter_dados_memoria_clientes():
    from backend.routers.clientes import _clientes_memoria, _inicializar_memoria
    _inicializar_memoria()
    return _clientes_memoria

def alugar_filme(db: Optional[Session], titulo: str, cliente_nome: str) -> Dict[str, Any]:
    titulo_limpo = titulo.strip() if titulo else ""
    cliente_limpo = cliente_nome.strip() if cliente_nome else ""

    if not titulo_limpo:
        raise ValueError("Título do filme é obrigatório.")
    if not cliente_limpo:
        raise ValueError("Nome do cliente é obrigatório.")

    if db is not None and FilmeDB is not None and ClienteDB is not None and LocacaoDB is not None:
        filme = db.query(FilmeDB).filter(FilmeDB.titulo.ilike(titulo_limpo)).first()
        if not filme:
            raise ValueError(f"Filme '{titulo_limpo}' não encontrado.")

        if filme.copias <= 0 or not filme.disponivel:
            raise ValueError(f"Filme '{filme.titulo}' não possui cópias disponíveis.")

        cliente = db.query(ClienteDB).filter(ClienteDB.nome.ilike(cliente_limpo)).first()
        if not cliente:
            cliente = ClienteDB(nome=cliente_limpo)
            db.add(cliente)
            db.flush()

        filme.copias -= 1
        if filme.copias == 0:
            filme.disponivel = False

        locacao = LocacaoDB(
            filme_id=filme.id,
            cliente_id=cliente.id,
            data_locacao=datetime.utcnow(),
            data_devolucao=None,
            status="PENDENTE",
            observacao=""
        )
        db.add(locacao)
        db.commit()
        db.refresh(locacao)
        db.refresh(filme)

        return {
            "id": locacao.id,
            "filme_id": locacao.filme_id,
            "cliente_id": locacao.cliente_id,
            "titulo": filme.titulo,
            "cliente": cliente.nome,
            "data_locacao": locacao.data_locacao,
            "data_devolucao": locacao.data_devolucao,
            "status": locacao.status,
            "observacao": locacao.observacao or ""
        }

    filmes = _obter_dados_memoria_filmes()
    filme_alvo = None
    for f in filmes:
        if f["titulo"].strip().lower() == titulo_limpo.lower():
            filme_alvo = f
            break

    if not filme_alvo:
        raise ValueError(f"Filme '{titulo_limpo}' não encontrado.")

    if filme_alvo["copias"] <= 0 or not filme_alvo.get("disponivel", True):
        raise ValueError(f"Filme '{filme_alvo['titulo']}' não possui cópias disponíveis.")

    clientes = _obter_dados_memoria_clientes()
    cliente_alvo = None
    for c in clientes:
        if c["nome"].strip().lower() == cliente_limpo.lower():
            cliente_alvo = c
            break

    if not cliente_alvo:
        novo_cliente_id = len(clientes) + 1
        cliente_alvo = {"id": novo_cliente_id, "nome": cliente_limpo}
        clientes.append(cliente_alvo)

    filme_alvo["copias"] -= 1
    if filme_alvo["copias"] == 0:
        filme_alvo["disponivel"] = False

    nova_locacao = {
        "id": len(_locacoes_memoria) + 1,
        "filme_id": filme_alvo["id"],
        "cliente_id": cliente_alvo["id"],
        "titulo": filme_alvo["titulo"],
        "cliente": cliente_alvo["nome"],
        "data_locacao": datetime.utcnow(),
        "data_devolucao": None,
        "status": "PENDENTE",
        "observacao": ""
    }
    _locacoes_memoria.append(nova_locacao)
    return nova_locacao

def devolver_filme(db: Optional[Session], titulo: str, cliente_nome: Optional[str] = None) -> Dict[str, Any]:
    titulo_limpo = titulo.strip() if titulo else ""
    cliente_limpo = cliente_nome.strip() if cliente_nome else None

    if not titulo_limpo:
        raise ValueError("Título do filme é obrigatório.")

    if db is not None and FilmeDB is not None and ClienteDB is not None and LocacaoDB is not None:
        filme = db.query(FilmeDB).filter(FilmeDB.titulo.ilike(titulo_limpo)).first()
        if not filme:
            raise ValueError(f"Filme '{titulo_limpo}' não encontrado.")

        total = filme.total_copias if filme.total_copias is not None else filme.copias
        if filme.copias >= total:
            raise ValueError("Todas as cópias deste filme já estão na locadora.")

        consulta = db.query(LocacaoDB).filter(
            LocacaoDB.filme_id == filme.id,
            LocacaoDB.status == "PENDENTE"
        )
        if cliente_limpo:
            locacao = consulta.join(ClienteDB).filter(ClienteDB.nome.ilike(cliente_limpo)).order_by(LocacaoDB.data_locacao.asc()).first()
            if not locacao:
                locacao = db.query(LocacaoDB).filter(
                    LocacaoDB.filme_id == filme.id,
                    LocacaoDB.status == "PENDENTE"
                ).order_by(LocacaoDB.data_locacao.asc()).first()
        else:
            locacao = consulta.order_by(LocacaoDB.data_locacao.asc()).first()

        if not locacao:
            raise ValueError("Nenhuma locação pendente encontrada para este filme.")

        locacao.status = "DEVOLVIDO"
        locacao.data_devolucao = datetime.utcnow()

        filme.copias += 1
        filme.disponivel = True

        db.commit()
        db.refresh(locacao)
        db.refresh(filme)

        nome_cliente = locacao.cliente.nome if locacao.cliente else (cliente_limpo or "Não informado")

        return {
            "id": locacao.id,
            "filme_id": locacao.filme_id,
            "cliente_id": locacao.cliente_id,
            "titulo": filme.titulo,
            "cliente": nome_cliente,
            "data_locacao": locacao.data_locacao,
            "data_devolucao": locacao.data_devolucao,
            "status": locacao.status,
            "observacao": locacao.observacao or ""
        }

    filmes = _obter_dados_memoria_filmes()
    filme_alvo = None
    for f in filmes:
        if f["titulo"].strip().lower() == titulo_limpo.lower():
            filme_alvo = f
            break

    if not filme_alvo:
        raise ValueError(f"Filme '{titulo_limpo}' não encontrado.")

    total = filme_alvo.get("total_copias", filme_alvo.get("copias", 0))
    if filme_alvo["copias"] >= total:
        raise ValueError("Todas as cópias deste filme já estão na locadora.")

    locacao_alvo = None
    for loc in _locacoes_memoria:
        if loc["filme_id"] == filme_alvo["id"] and loc["status"] == "PENDENTE":
            if cliente_limpo and loc["cliente"].strip().lower() == cliente_limpo.lower():
                locacao_alvo = loc
                break

    if not locacao_alvo:
        for loc in _locacoes_memoria:
            if loc["filme_id"] == filme_alvo["id"] and loc["status"] == "PENDENTE":
                locacao_alvo = loc
                break

    if not locacao_alvo:
        raise ValueError("Nenhuma locação pendente encontrada para este filme.")

    locacao_alvo["status"] = "DEVOLVIDO"
    locacao_alvo["data_devolucao"] = datetime.utcnow()

    filme_alvo["copias"] += 1
    filme_alvo["disponivel"] = True

    return locacao_alvo
