import os
import sys
import time
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from services.api_client import ApiClient

def iniciar_servidor_local(host: str, port: int):
    client = ApiClient(host=host, port=port, timeout=1.0)
    if client.verificar_conexao():
        return None

    import uvicorn
    from backend.main import app

    config = uvicorn.Config(app=app, host=host, port=port, log_level="error")
    server = uvicorn.Server(config=config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    limite = time.time() + 6.0
    while time.time() < limite:
        if client.verificar_conexao():
            return server
        time.sleep(0.1)

    return server

def executar_testes():
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))

    server = iniciar_servidor_local(host, port)
    client = ApiClient(host=host, port=port, timeout=5.0)

    print(f"Testando conexao com a API em http://{host}:{port}...")

    assert client.verificar_conexao() is True, "Falha na verificacao de conexao (/health)"
    health = client.health_check()
    assert health.get("status") == "ok", f"Health check inesperado: {health}"
    print("[OK] Health check /health respondendo com status 200")

    filmes = client.obter_filmes()
    assert isinstance(filmes, list) and len(filmes) > 0, "Nenhum filme retornado na listagem"
    print(f"[OK] Listagem de filmes retornou {len(filmes)} registros")

    clientes = client.obter_clientes()
    assert isinstance(clientes, list) and len(clientes) > 0, "Nenhum cliente retornado na listagem"
    print(f"[OK] Listagem de clientes retornou {len(clientes)} nomes")

    filme_teste = filmes[0]["titulo"]
    detalhes_filme = client.buscar_filme(filme_teste)
    assert detalhes_filme is not None, f"Falha ao buscar detalhes de {filme_teste}"
    print(f"[OK] Busca individual do filme '{filme_teste}' bem-sucedida")

    cliente_teste = clientes[0]
    resultado_aluguel = client.alugar_filme_detalhes(filme_teste, cliente_teste)
    assert resultado_aluguel.get("status") == "PENDENTE", f"Status de locacao invalido: {resultado_aluguel}"
    print(f"[OK] Locacao realizada com sucesso: '{filme_teste}' para {cliente_teste}")

    pendentes = client.obter_locacoes_pendentes()
    assert any(p["titulo"].strip().lower() == filme_teste.strip().lower() for p in pendentes), "Locacao nao consta na lista de pendentes"
    print(f"[OK] Consulta de pendentes validada ({len(pendentes)} locacao(oes) pendente(s))")

    resultado_devolucao = client.devolver_filme_detalhes(filme_teste, cliente_teste)
    assert resultado_devolucao.get("status") == "DEVOLVIDO", f"Status de devolucao invalido: {resultado_devolucao}"
    print(f"[OK] Devolucao realizada com sucesso para '{filme_teste}'")

    historico = client.obter_historico_locacoes()
    assert isinstance(historico, list) and len(historico) > 0, "Historico transacional vazio"
    print(f"[OK] Historico transacional consultado com sucesso ({len(historico)} registros)")

    print("Todos os testes de conexao de rede e integracao foram concluidos com sucesso!")

    if server is not None:
        server.should_exit = True

if __name__ == "__main__":
    try:
        executar_testes()
        sys.exit(0)
    except Exception as erro:
        print(f"[ERRO] Falha no teste de conexao com a API: {erro}")
        sys.exit(1)
