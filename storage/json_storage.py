import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from models.filme import filmes_iniciais
from models.cliente import clientes_iniciais

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = BASE_DIR / "data"


class JsonStorage:

    # Inicializa o storage JSON definindo os caminhos dos arquivos filmes.json e clientes.json
    def __init__(self, data_dir: Optional[Path] = None, auto_inicializar: bool = True):
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.filmes_path = self.data_dir / "filmes.json"
        self.clientes_path = self.data_dir / "clientes.json"

        if auto_inicializar:
            self.inicializar_dados_padrao()

    # Cria e preenche os arquivos JSON com dados iniciais se não existirem
    def inicializar_dados_padrao(self) -> None:
        if not self.filmes_path.exists() or self.filmes_path.stat().st_size == 0:
            self.salvar_filmes(filmes_iniciais())

        if not self.clientes_path.exists() or self.clientes_path.stat().st_size == 0:
            self.salvar_clientes(clientes_iniciais())

    # Lê o arquivo filmes.json e retorna a lista de filmes
    def carregar_filmes(self) -> List[Dict[str, Any]]:
        if not self.filmes_path.exists():
            return []

        try:
            with open(self.filmes_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    # Grava a lista completa de filmes no arquivo filmes.json
    def salvar_filmes(self, filmes: List[Dict[str, Any]]) -> None:
        with open(self.filmes_path, "w", encoding="utf-8") as f:
            json.dump(filmes, f, indent=4, ensure_ascii=False)

    # Retorna todos os filmes cadastrados no arquivo JSON
    def obter_filmes(self) -> List[Dict[str, Any]]:
        return self.carregar_filmes()

    # Busca um filme pelo título (case-insensitive)
    def buscar_filme(self, titulo: str) -> Optional[Dict[str, Any]]:
        filmes = self.carregar_filmes()
        for f in filmes:
            if f.get("titulo", "").lower() == titulo.strip().lower():
                return f
        return None

    # Adiciona um novo filme ao arquivo JSON se não houver duplicidade
    def adicionar_filme(self, novo_filme: Dict[str, Any]) -> bool:
        filmes = self.carregar_filmes()
        titulo_novo = novo_filme.get("titulo", "").strip().lower()

        for f in filmes:
            if f.get("titulo", "").strip().lower() == titulo_novo:
                return False

        filmes.append(novo_filme)
        self.salvar_filmes(filmes)
        return True

    # Atualiza as informações de um filme existente no arquivo JSON
    def atualizar_filme(self, titulo: str, dados_atualizados: Dict[str, Any]) -> bool:
        filmes = self.carregar_filmes()
        titulo_alvo = titulo.strip().lower()

        for i, f in enumerate(filmes):
            if f.get("titulo", "").strip().lower() == titulo_alvo:
                filmes[i].update(dados_atualizados)
                self.salvar_filmes(filmes)
                return True
        return False

    # Remove um filme do arquivo JSON pelo título
    def remover_filme(self, titulo: str) -> bool:
        filmes = self.carregar_filmes()
        titulo_alvo = titulo.strip().lower()
        tamanho_original = len(filmes)

        filmes = [f for f in filmes if f.get("titulo", "").strip().lower() != titulo_alvo]
        if len(filmes) < tamanho_original:
            self.salvar_filmes(filmes)
            return True
        return False

    # Lê o arquivo clientes.json e retorna a lista de nomes dos clientes
    def carregar_clientes(self) -> List[str]:
        if not self.clientes_path.exists():
            return []

        try:
            with open(self.clientes_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    # Grava a lista de nomes de clientes no arquivo clientes.json
    def salvar_clientes(self, clientes: List[str]) -> None:
        with open(self.clientes_path, "w", encoding="utf-8") as f:
            json.dump(clientes, f, indent=4, ensure_ascii=False)

    # Retorna todos os clientes cadastrados no arquivo JSON
    def obter_clientes(self) -> List[str]:
        return self.carregar_clientes()

    # Busca um cliente cadastrado pelo nome
    def buscar_cliente(self, nome: str) -> Optional[str]:
        clientes = self.carregar_clientes()
        nome_alvo = nome.strip().lower()
        for c in clientes:
            if c.strip().lower() == nome_alvo:
                return c
        return None

    # Adiciona um novo cliente no JSON caso o nome não seja repetido
    def adicionar_cliente(self, nome: str) -> bool:
        nome_limpo = nome.strip()
        if not nome_limpo:
            return False

        clientes = self.carregar_clientes()
        if any(c.strip().lower() == nome_limpo.lower() for c in clientes):
            return False

        clientes.append(nome_limpo)
        self.salvar_clientes(clientes)
        return True

    # Remove um cliente da lista salva no arquivo JSON
    def remover_cliente(self, nome: str) -> bool:
        nome_alvo = nome.strip().lower()
        clientes = self.carregar_clientes()
        tamanho_original = len(clientes)

        clientes = [c for c in clientes if c.strip().lower() != nome_alvo]
        if len(clientes) < tamanho_original:
            self.salvar_clientes(clientes)
            return True
        return False

