from PySide6.QtCore import QMutexLocker

from storage import JsonStorage, CsvStorage, LogTxt
from utils.concurrency import mutex_arquivos

class LocadoraService:

    def __init__(self):
        self.json_storage = JsonStorage()
        self.csv_storage = CsvStorage()
        self.log_txt = LogTxt()

    def listar_filmes(self) -> list:
        with QMutexLocker(mutex_arquivos):
            return self.json_storage.obter_filmes()

    def cadastrar_filme(self, filme: dict) -> bool:
        with QMutexLocker(mutex_arquivos):
            return self.json_storage.adicionar_filme(filme)

    def remover_filme(self, titulo: str) -> bool:
        with QMutexLocker(mutex_arquivos):
            return self.json_storage.remover_filme(titulo)

    def alugar_filme(self, titulo: str, cliente: str) -> bool:
        with QMutexLocker(mutex_arquivos):
            filme = self.json_storage.buscar_filme(titulo)
            if filme is None or filme["copias"] <= 0:
                return False

            copias = filme["copias"] - 1
            dados = {"copias": copias}
            if copias == 0:
                dados["disponivel"] = False
            self.json_storage.atualizar_filme(titulo, dados)

            self.csv_storage.registrar_locacao(titulo, cliente)
            self.log_txt.registrar_locacao(titulo, cliente)
            return True

    def devolver_filme(self, titulo: str):
        with QMutexLocker(mutex_arquivos):
            filme = self.json_storage.buscar_filme(titulo)
            if filme is None:
                return None

            self.json_storage.atualizar_filme(
                titulo, {"copias": filme["copias"] + 1, "disponivel": True}
            )

            cliente = self._cliente_da_locacao_pendente(titulo)
            self.csv_storage.registrar_devolucao(titulo, cliente)
            self.log_txt.registrar_devolucao(titulo, cliente)
            return cliente

    def _cliente_da_locacao_pendente(self, titulo: str) -> str:
        for locacao in self.csv_storage.obter_locacoes_pendentes():
            if locacao["titulo"].strip().lower() == titulo.strip().lower():
                return locacao["cliente"]
        return "Não informado"

    def listar_clientes(self) -> list:
        with QMutexLocker(mutex_arquivos):
            return self.json_storage.obter_clientes()

    def adicionar_cliente(self, nome: str) -> bool:
        with QMutexLocker(mutex_arquivos):
            return self.json_storage.adicionar_cliente(nome)

    def remover_cliente(self, nome: str) -> bool:
        with QMutexLocker(mutex_arquivos):
            return self.json_storage.remover_cliente(nome)