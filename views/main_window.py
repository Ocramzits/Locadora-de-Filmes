from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
)

from services.locadora_service import LocadoraService
from threads.io_thread import IOThread
from threads.backup_thread import BackupThread
from threads.export_thread import ExportThread
from views.dialogo_novo_filme import DialogoNovoFilme
from views.dialogo_alugar import DialogoAlugarFilme
from views.janela_clientes import JanelaClientes
from views.dialog_progress import DialogProgress

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Locadora de Filmes")
        self.resize(700, 450)

        self.service = LocadoraService()
        self.filmes = []
        self.clientes = []
        self.janela_clientes = None
        self.dialogo_progresso = None
        self.export_thread = None
        self.threads_ativas = []
        self.operacoes_pendentes = 0

        self._montar_interface()
        self._montar_toolbar()
        self._montar_menu()

        self.backup_thread = BackupThread(self.service, intervalo_segundos=300)
        self.backup_thread.backup_realizado.connect(self._ao_backup_realizado)
        self.backup_thread.start()

        self.statusBar().showMessage("Carregando dados...")
        self._executar_em_thread(self._tarefa_carregar)

    def _montar_interface(self):

        self.tabela_filmes = QTableWidget(0, 4)
        self.tabela_filmes.setHorizontalHeaderLabels(
            ["Título", "Categoria", "Cópias", "Status"]
        )
        self.tabela_filmes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela_filmes.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela_filmes.itemSelectionChanged.connect(self.atualizar_botoes_acao)

        self._atualizar_tabela()

        self.botao_alugar = QPushButton("Alugar Selecionado")
        self.botao_alugar.clicked.connect(self.abrir_dialogo_alugar)
        self.botao_alugar.setEnabled(False)

        self.botao_devolver = QPushButton("Devolver Selecionado")
        self.botao_devolver.clicked.connect(self.devolver_filme)
        self.botao_devolver.setEnabled(False)

        self.botao_remover = QPushButton("Remover Selecionado")
        self.botao_remover.clicked.connect(self.remover_filme_selecionado)
        self.botao_remover.setEnabled(False)

        grade_botoes = QGridLayout()
        grade_botoes.addWidget(self.botao_alugar, 0, 0)
        grade_botoes.addWidget(self.botao_devolver, 0, 1)
        grade_botoes.addWidget(self.botao_remover, 0, 2)

        layout_principal = QVBoxLayout()
        layout_principal.addWidget(QLabel("Filmes disponíveis na locadora:"))
        layout_principal.addWidget(self.tabela_filmes)
        layout_principal.addLayout(grade_botoes)

        container = QWidget()
        container.setLayout(layout_principal)
        self.setCentralWidget(container)

    def _montar_toolbar(self):

        barra = self.addToolBar("Principal")
        self.barra_ferramentas = barra

        acao_novo_filme = QAction("Novo Filme", self)
        acao_novo_filme.setShortcut(QKeySequence("Ctrl+N"))
        acao_novo_filme.triggered.connect(self.abrir_dialogo_novo_filme)
        barra.addAction(acao_novo_filme)

        barra.addSeparator()

        acao_clientes = QAction("Clientes", self)
        acao_clientes.triggered.connect(self.abrir_janela_clientes)
        barra.addAction(acao_clientes)

        barra.addSeparator()

        acao_exportar = QAction("Exportar Relatório", self)
        acao_exportar.setShortcut(QKeySequence("Ctrl+E"))
        acao_exportar.triggered.connect(self.exportar_relatorio)
        barra.addAction(acao_exportar)

    def _montar_menu(self):

        menu_arquivo = self.menuBar().addMenu("Arquivo")

        acao_novo = QAction("Novo Filme", self)
        acao_novo.setShortcut(QKeySequence("Ctrl+N"))
        acao_novo.triggered.connect(self.abrir_dialogo_novo_filme)
        menu_arquivo.addAction(acao_novo)

        acao_exportar = QAction("Exportar Relatório", self)
        acao_exportar.setShortcut(QKeySequence("Ctrl+E"))
        acao_exportar.triggered.connect(self.exportar_relatorio)
        menu_arquivo.addAction(acao_exportar)

        menu_arquivo.addSeparator()

        acao_sair = QAction("Sair", self)
        acao_sair.triggered.connect(self.close)
        menu_arquivo.addAction(acao_sair)

        menu_cadastro = self.menuBar().addMenu("Cadastro")

        acao_ver_clientes = QAction("Ver Clientes", self)
        acao_ver_clientes.triggered.connect(self.abrir_janela_clientes)
        menu_cadastro.addAction(acao_ver_clientes)

        menu_ajuda = self.menuBar().addMenu("Ajuda")

        acao_sobre = QAction("Sobre", self)
        acao_sobre.triggered.connect(self.mostrar_sobre)
        menu_ajuda.addAction(acao_sobre)

    def _executar_em_thread(self, tarefa, *args):
        self.threads_ativas = [t for t in self.threads_ativas if not t.isFinished()]

        thread = IOThread(self._rodar_tarefa, tarefa, *args)
        thread.concluido.connect(self._ao_concluir)
        thread.erro.connect(self._ao_erro)
        thread.finished.connect(self._operacao_finalizada)

        self.threads_ativas.append(thread)
        self.operacoes_pendentes += 1
        self._definir_ocupado(True)
        thread.start()

    def _rodar_tarefa(self, tarefa, *args):
        mensagem = tarefa(*args)
        return mensagem, self.service.listar_filmes(), self.service.listar_clientes()

    def _ao_concluir(self, resultado):
        mensagem, filmes, clientes = resultado
        self.filmes = filmes
        self.clientes = clientes
        self._atualizar_tabela()
        self.statusBar().showMessage(mensagem, 5000)

    def _ao_erro(self, mensagem: str):
        QMessageBox.critical(self, "Erro", f"Falha ao acessar os arquivos: {mensagem}")

    def _operacao_finalizada(self):
        self.operacoes_pendentes -= 1
        if self.operacoes_pendentes == 0:
            self._definir_ocupado(False)

    def _definir_ocupado(self, ocupado: bool):
        self.centralWidget().setEnabled(not ocupado)
        self.menuBar().setEnabled(not ocupado)
        self.barra_ferramentas.setEnabled(not ocupado)

    def _ao_backup_realizado(self, timestamp: str):
        self.statusBar().showMessage(f"Último backup: {timestamp}", 10000)

    def _tarefa_carregar(self):
        return "Dados carregados"

    def _tarefa_cadastrar_filme(self, filme: dict):
        if self.service.cadastrar_filme(filme):
            return f"Filme '{filme['titulo']}' cadastrado"
        return "Não foi possível cadastrar: filme já existe"

    def _tarefa_alugar(self, titulo: str, cliente: str):
        if self.service.alugar_filme(titulo, cliente):
            return f"'{titulo}' alugado para {cliente}"
        return "Não há cópias disponíveis para locação"

    def _tarefa_devolver(self, titulo: str):
        cliente = self.service.devolver_filme(titulo)
        return f"Cópia de '{titulo}' devolvida por {cliente}"

    def _tarefa_remover_filme(self, titulo: str):
        self.service.remover_filme(titulo)
        return "Filme removido"

    def _tarefa_adicionar_cliente(self, nome: str):
        self.service.adicionar_cliente(nome)
        return f"Cliente '{nome}' salvo"

    def _tarefa_remover_cliente(self, nome: str):
        self.service.remover_cliente(nome)
        return f"Cliente '{nome}' removido"

    def _atualizar_tabela(self):

        self.tabela_filmes.setRowCount(0)
        for filme in self.filmes:
            linha = self.tabela_filmes.rowCount()
            self.tabela_filmes.insertRow(linha)
            self.tabela_filmes.setItem(linha, 0, QTableWidgetItem(filme["titulo"]))
            self.tabela_filmes.setItem(linha, 1, QTableWidgetItem(filme["categoria"]))
            self.tabela_filmes.setItem(linha, 2, QTableWidgetItem(str(filme["copias"])))
            status = "Disponível" if filme["disponivel"] else "Alugado"
            self.tabela_filmes.setItem(linha, 3, QTableWidgetItem(status))

    def atualizar_botoes_acao(self):

        linha = self.tabela_filmes.currentRow()
        tem_selecao = linha >= 0
        self.botao_remover.setEnabled(tem_selecao)

        if tem_selecao:
            copias = self.filmes[linha]["copias"]
            self.botao_alugar.setEnabled(copias > 0)
            self.botao_devolver.setEnabled(True)
        else:
            self.botao_alugar.setEnabled(False)
            self.botao_devolver.setEnabled(False)

    def abrir_dialogo_novo_filme(self):
        titulos = [f["titulo"] for f in self.filmes]
        dialogo = DialogoNovoFilme(titulos, self)
        dialogo.filme_cadastrado.connect(self.cadastrar_filme)
        dialogo.exec()

    def cadastrar_filme(self, filme: dict):
        self.statusBar().showMessage("Salvando filme...")
        self._executar_em_thread(self._tarefa_cadastrar_filme, filme)

    def abrir_dialogo_alugar(self):
        linha = self.tabela_filmes.currentRow()
        if linha < 0:
            return

        if not self.clientes:
            QMessageBox.warning(self, "Aviso", "Não há clientes cadastrados para realizar a locação.")
            return

        titulo = self.filmes[linha]["titulo"]
        dialogo = DialogoAlugarFilme(titulo, self.clientes, self)
        dialogo.filme_alugado.connect(self.registrar_locacao)
        dialogo.exec()

    def registrar_locacao(self, titulo: str, cliente: str):
        self.statusBar().showMessage("Registrando locação...")
        self._executar_em_thread(self._tarefa_alugar, titulo, cliente)

    def devolver_filme(self):
        linha = self.tabela_filmes.currentRow()
        if linha < 0:
            return

        filme = self.filmes[linha]

        if filme.get("copias", 0) >= filme.get("total_copias", filme.get("copias", 0)):
            QMessageBox.warning(self, "Erro", "Todas as cópias deste filme já estão na locadora.")
            return

        resposta = QMessageBox.question(
            self, "Confirmar devolução",
            f"Confirmar devolução de uma cópia de '{filme['titulo']}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resposta == QMessageBox.Yes:
            self.statusBar().showMessage("Registrando devolução...")
            self._executar_em_thread(self._tarefa_devolver, filme["titulo"])

    def remover_filme_selecionado(self):
        linha = self.tabela_filmes.currentRow()
        if linha < 0:
            return

        filme = self.filmes[linha]
        resposta = QMessageBox.question(
            self, "Confirmar remoção",
            f"Remover '{filme['titulo']}' do catálogo?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resposta == QMessageBox.Yes:
            self.statusBar().showMessage("Removendo filme...")
            self._executar_em_thread(self._tarefa_remover_filme, filme["titulo"])

    def abrir_janela_clientes(self):
        if self.janela_clientes is None:
            self.janela_clientes = JanelaClientes(self.clientes, self)
            self.janela_clientes.cliente_adicionado.connect(self.registrar_novo_cliente)
            self.janela_clientes.cliente_removido.connect(self.remover_cliente_lista)

        self.janela_clientes.show()
        self.janela_clientes.raise_()
        self.janela_clientes.activateWindow()

    def registrar_novo_cliente(self, nome: str):
        self._executar_em_thread(self._tarefa_adicionar_cliente, nome)

    def remover_cliente_lista(self, nome: str):
        self._executar_em_thread(self._tarefa_remover_cliente, nome)

    def mostrar_sobre(self):
        QMessageBox.about(
            self, "Sobre",
            "Sistema de Locadora de Filmes\n"
            "Trabalho de POO II - PySide6\n",
        )

    def exportar_relatorio(self):
        self.dialogo_progresso = DialogProgress(self)
        self.export_thread = ExportThread(self.service, parent=self)
        self.export_thread.progresso.connect(self.dialogo_progresso.atualizar_progresso)
        self.export_thread.concluido.connect(self._ao_exportacao_concluida)
        self.export_thread.erro.connect(self._ao_exportacao_erro)
        self.export_thread.finished.connect(self._ao_exportacao_finalizada)
        self.threads_ativas.append(self.export_thread)
        self.dialogo_progresso.show()
        self.export_thread.start()

    def _ao_exportacao_concluida(self, caminho: str):
        if self.dialogo_progresso:
            self.dialogo_progresso.ao_concluir(caminho)
        self.statusBar().showMessage(f"Relatório exportado para: {caminho}", 5000)

    def _ao_exportacao_erro(self, mensagem: str):
        if self.dialogo_progresso:
            self.dialogo_progresso.ao_erro(mensagem)
        QMessageBox.critical(self, "Erro na Exportação", f"Falha ao exportar relatório: {mensagem}")

    def _ao_exportacao_finalizada(self):
        self.threads_ativas = [t for t in self.threads_ativas if not t.isFinished()]

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.remover_filme_selecionado()
        super().keyPressEvent(event)

    def resizeEvent(self, event):
        tamanho = event.size()
        self.statusBar().showMessage(
            f"Janela redimensionada: {tamanho.width()}x{tamanho.height()}", 2000
        )
        super().resizeEvent(event)

    def closeEvent(self, event):
        resposta = QMessageBox.question(
            self, "Confirmar saída",
            "Tem certeza que deseja fechar a Locadora de Filmes?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resposta == QMessageBox.Yes:
            self.backup_thread.parar()
            self.backup_thread.wait()
            for thread in self.threads_ativas:
                thread.wait()
            event.accept()
        else:
            event.ignore()