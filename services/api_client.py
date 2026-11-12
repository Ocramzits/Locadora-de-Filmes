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

    def verificar_conexao(self) -> bool:
        try:
            resp = self.session.get(self._url("/health"), timeout=self.timeout)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def health_check(self) -> Dict[str, Any]:
        resp = self.session.get(self._url("/health"), timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def obter_filmes(self) -> List[Dict[str, Any]]:
        resp = self.session.get(self._url("/filmes"), timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def buscar_filme(self, titulo: str) -> Optional[Dict[str, Any]]:
        resp = self.session.get(self._url(f"/filmes/{titulo}"), timeout=self.timeout)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def cadastrar_filme(self, filme: Dict[str, Any]) -> bool:
        try:
            resp = self.session.post(self._url("/filmes"), json=filme, timeout=self.timeout)
            return resp.status_code in (200, 201)
        except requests.RequestException:
            return False

    def adicionar_filme(self, filme: Dict[str, Any]) -> bool:
        return self.cadastrar_filme(filme)

    def remover_filme(self, titulo: str) -> bool:
        try:
            resp = self.session.delete(self._url(f"/filmes/{titulo}"), timeout=self.timeout)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def obter_clientes(self) -> List[str]:
        resp = self.session.get(self._url("/clientes"), timeout=self.timeout)
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
        resp = self.session.get(self._url("/clientes"), timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def adicionar_cliente(self, nome: str) -> bool:
        try:
            resp = self.session.post(self._url("/clientes"), json={"nome": nome}, timeout=self.timeout)
            return resp.status_code in (200, 201)
        except requests.RequestException:
            return False

    def remover_cliente(self, nome: str) -> bool:
        try:
            resp = self.session.delete(self._url(f"/clientes/{nome}"), timeout=self.timeout)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def alugar_filme(self, titulo: str, cliente: str) -> bool:
        try:
            payload = {"titulo": titulo, "cliente": cliente}
            resp = self.session.post(self._url("/locacoes/alugar"), json=payload, timeout=self.timeout)
            return resp.status_code in (200, 201)
        except requests.RequestException:
            return False

    def alugar_filme_detalhes(self, titulo: str, cliente: str) -> Dict[str, Any]:
        payload = {"titulo": titulo, "cliente": cliente}
        resp = self.session.post(self._url("/locacoes/alugar"), json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def devolver_filme(self, titulo: str, cliente: Optional[str] = None) -> Optional[str]:
        try:
            payload = {"titulo": titulo}
            if cliente:
                payload["cliente"] = cliente
            resp = self.session.post(self._url("/locacoes/devolver"), json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                dados = resp.json()
                return dados.get("cliente") or "Não informado"
            return None
        except requests.RequestException:
            return None

    def devolver_filme_detalhes(self, titulo: str, cliente: Optional[str] = None) -> Dict[str, Any]:
        payload = {"titulo": titulo}
        if cliente:
            payload["cliente"] = cliente
        resp = self.session.post(self._url("/locacoes/devolver"), json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def obter_locacoes_pendentes(self) -> List[Dict[str, Any]]:
        resp = self.session.get(self._url("/locacoes/pendentes"), timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def obter_historico_locacoes(self, limite: Optional[int] = None) -> List[Dict[str, Any]]:
        params = {}
        if limite is not None:
            params["limite"] = limite
        resp = self.session.get(self._url("/locacoes"), params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
