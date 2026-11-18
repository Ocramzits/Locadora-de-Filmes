import requests
from typing import List, Dict, Any, Optional

class ApiClient:

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        base_url: Optional[str] = None,
        timeout: float = 5.0
    ):
        if base_url:
            self.base_url = base_url.rstrip("/")
        else:
            self.base_url = f"http://{host}:{port}"
        self.timeout = timeout
        self.session = requests.Session()

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _tratar_requisicao(self, metodo: str, path: str, **kwargs):
        url = self._url(path)
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        try:
            return self.session.request(metodo, url, **kwargs)
        except requests.exceptions.Timeout as e:
            raise TimeoutError("Tempo limite de conexão com o servidor remoto esgotado.") from e
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError("Servidor remoto inacessível. Verifique a conexão com a API.") from e
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Erro na comunicação com a API: {e}") from e

    def verificar_conexao(self) -> bool:
        try:
            resp = self.session.get(self._url("/health"), timeout=self.timeout)
            return resp.status_code == 200
        except Exception:
            return False

    def health_check(self) -> Dict[str, Any]:
        resp = self._tratar_requisicao("GET", "/health")
        resp.raise_for_status()
        return resp.json()

    def obter_filmes(self) -> List[Dict[str, Any]]:
        resp = self._tratar_requisicao("GET", "/filmes")
        resp.raise_for_status()
        return resp.json()

    def buscar_filme(self, titulo: str) -> Optional[Dict[str, Any]]:
        resp = self._tratar_requisicao("GET", f"/filmes/{titulo}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def cadastrar_filme(self, filme: Dict[str, Any]) -> bool:
        resp = self._tratar_requisicao("POST", "/filmes", json=filme)
        return resp.status_code in (200, 201)

    def adicionar_filme(self, filme: Dict[str, Any]) -> bool:
        return self.cadastrar_filme(filme)

    def remover_filme(self, titulo: str) -> bool:
        resp = self._tratar_requisicao("DELETE", f"/filmes/{titulo}")
        return resp.status_code == 200

    def obter_clientes(self) -> List[str]:
        resp = self._tratar_requisicao("GET", "/clientes")
        resp.raise_for_status()
        dados = resp.json()
        nomes = []
        for item in dados:
            if isinstance(item, dict) and "nome" in item:
                nomes.append(item["nome"])
            elif isinstance(item, str):
                nomes.append(item)
        return nomes

    def obter_clientes_detalhes(self) -> List[Dict[str, Any]]:
        resp = self._tratar_requisicao("GET", "/clientes")
        resp.raise_for_status()
        return resp.json()

    def adicionar_cliente(self, nome: str) -> bool:
        resp = self._tratar_requisicao("POST", "/clientes", json={"nome": nome})
        return resp.status_code in (200, 201)

    def remover_cliente(self, nome: str) -> bool:
        resp = self._tratar_requisicao("DELETE", f"/clientes/{nome}")
        return resp.status_code == 200

    def alugar_filme(self, titulo: str, cliente: str) -> bool:
        payload = {"titulo": titulo, "cliente": cliente}
        resp = self._tratar_requisicao("POST", "/locacoes/alugar", json=payload)
        return resp.status_code in (200, 201)

    def alugar_filme_detalhes(self, titulo: str, cliente: str) -> Dict[str, Any]:
        payload = {"titulo": titulo, "cliente": cliente}
        resp = self._tratar_requisicao("POST", "/locacoes/alugar", json=payload)
        resp.raise_for_status()
        return resp.json()

    def devolver_filme(self, titulo: str, cliente: Optional[str] = None) -> Optional[str]:
        payload = {"titulo": titulo}
        if cliente:
            payload["cliente"] = cliente
        resp = self._tratar_requisicao("POST", "/locacoes/devolver", json=payload)
        if resp.status_code == 200:
            dados = resp.json()
            return dados.get("cliente") or "Não informado"
        return None

    def devolver_filme_detalhes(self, titulo: str, cliente: Optional[str] = None) -> Dict[str, Any]:
        payload = {"titulo": titulo}
        if cliente:
            payload["cliente"] = cliente
        resp = self._tratar_requisicao("POST", "/locacoes/devolver", json=payload)
        resp.raise_for_status()
        return resp.json()

    def obter_locacoes_pendentes(self) -> List[Dict[str, Any]]:
        resp = self._tratar_requisicao("GET", "/locacoes/pendentes")
        resp.raise_for_status()
        return resp.json()

    def obter_historico_locacoes(self, limite: Optional[int] = None) -> List[Dict[str, Any]]:
        params = {}
        if limite is not None:
            params["limite"] = limite
        resp = self._tratar_requisicao("GET", "/locacoes", params=params)
        resp.raise_for_status()
        return resp.json()
