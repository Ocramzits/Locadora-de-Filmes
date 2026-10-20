from PySide6.QtCore import QMutexLocker

from storage import JsonStorage, CsvStorage, LogTxt
from utils.concurrency import mutex_arquivos

class LocadoraService:

    # Inicializa o serviço e as instâncias de persistência (JSON, CSV e TXT)
    def __init__(self):
        self.json_storage = JsonStorage()
        self.csv_storage = CsvStorage()
        self.log_txt = LogTxt()

    # Retorna a lista de filmes salvos (com proteção de concorrência por Mutex)
    def listar_filmes(self) -> list:
        with QMutexLocker(mutex_arquivos):
            return self.json_storage.obter_filmes()

    # Cadastra um novo filme no sistema
    def cadastrar_filme(self, filme: dict) -> bool:
        with QMutexLocker(mutex_arquivos):
            return self.json_storage.adicionar_filme(filme)

    # Remove um filme do catálogo pelo título
    def remover_filme(self, titulo: str) -> bool:
        with QMutexLocker(mutex_arquivos):
            return self.json_storage.remover_filme(titulo)

    # Realiza a locação: decrementa cópias do filme e registra no histórico CSV e no log TXT
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

    # Realiza a devolução: incrementa cópias do filme e registra a devolução no CSV e TXT
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

    # Busca no histórico CSV o nome do cliente que possui locação pendente deste filme
    def _cliente_da_locacao_pendente(self, titulo: str) -> str:
        for locacao in self.csv_storage.obter_locacoes_pendentes():
            if locacao["titulo"].strip().lower() == titulo.strip().lower():
                return locacao["cliente"]
        return "Não informado"

    # Retorna a lista de clientes cadastrados (protegido por Mutex)
    def listar_clientes(self) -> list:
        with QMutexLocker(mutex_arquivos):
            return self.json_storage.obter_clientes()

    # Adiciona um novo cliente no cadastro
    def adicionar_cliente(self, nome: str) -> bool:
        with QMutexLocker(mutex_arquivos):
            return self.json_storage.adicionar_cliente(nome)

    # Remove um cliente do cadastro pelo nome
    def remover_cliente(self, nome: str) -> bool:
        with QMutexLocker(mutex_arquivos):
            return self.json_storage.remover_cliente(nome)