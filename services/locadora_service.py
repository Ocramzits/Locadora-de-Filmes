from typing import Optional, List, Dict, Any
from PySide6.QtCore import QMutexLocker

from services.api_client import ApiClient
from storage import JsonStorage, CsvStorage, LogTxt
from utils.concurrency import mutex_arquivos

class LocadoraService:

    def __init__(self, api_client: Optional[ApiClient] = None):
        self.api_client = api_client if api_client is not None else ApiClient()
        self.json_storage = JsonStorage()
        self.csv_storage = CsvStorage()
        self.log_txt = LogTxt()

    def verificar_conexao(self) -> bool:
        return self.api_client.verificar_conexao()

    def listar_filmes(self) -> List[Dict[str, Any]]:
        with QMutexLocker(mutex_arquivos):
            return self.api_client.obter_filmes()

    def buscar_filme(self, titulo: str) -> Optional[Dict[str, Any]]:
        with QMutexLocker(mutex_arquivos):
            return self.api_client.buscar_filme(titulo)

    def cadastrar_filme(self, filme: dict) -> bool:
        with QMutexLocker(mutex_arquivos):
            sucesso = self.api_client.cadastrar_filme(filme)
            if sucesso:
                self.log_txt.registrar_cadastro_filme(filme.get("titulo", ""), filme.get("categoria", ""))
            return sucesso

    def remover_filme(self, titulo: str) -> bool:
        with QMutexLocker(mutex_arquivos):
            sucesso = self.api_client.remover_filme(titulo)
            if sucesso:
                self.log_txt.registrar_remocao_filme(titulo)
            return sucesso

    def alugar_filme(self, titulo: str, cliente: str) -> bool:
        with QMutexLocker(mutex_arquivos):
            sucesso = self.api_client.alugar_filme(titulo, cliente)
            if sucesso:
                self.csv_storage.registrar_locacao(titulo, cliente)
                self.log_txt.registrar_locacao(titulo, cliente)
            return sucesso

    def devolver_filme(self, titulo: str) -> Optional[str]:
        with QMutexLocker(mutex_arquivos):
            cliente = self.api_client.devolver_filme(titulo)
            if cliente:
                self.csv_storage.registrar_devolucao(titulo, cliente)
                self.log_txt.registrar_devolucao(titulo, cliente)
            return cliente

    def listar_clientes(self) -> List[str]:
        with QMutexLocker(mutex_arquivos):
            return self.api_client.obter_clientes()

    def adicionar_cliente(self, nome: str) -> bool:
        with QMutexLocker(mutex_arquivos):
            sucesso = self.api_client.adicionar_cliente(nome)
            if sucesso:
                self.log_txt.registrar_cadastro_cliente(nome)
            return sucesso

    def remover_cliente(self, nome: str) -> bool:
        with QMutexLocker(mutex_arquivos):
            sucesso = self.api_client.remover_cliente(nome)
            if sucesso:
                self.log_txt.registrar_remocao_cliente(nome)
            return sucesso

    def obter_resumo_relatorio(self) -> Dict[str, Any]:
        with QMutexLocker(mutex_arquivos):
            return self.api_client.obter_resumo_relatorio()

    def obter_mais_alugados(self, limite: Optional[int] = None) -> List[Dict[str, Any]]:
        with QMutexLocker(mutex_arquivos):
            return self.api_client.obter_mais_alugados(limite)

    def obter_clientes_mais_ativos(self, limite: Optional[int] = None) -> List[Dict[str, Any]]:
        with QMutexLocker(mutex_arquivos):
            return self.api_client.obter_clientes_mais_ativos(limite)
