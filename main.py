# Grupo: Marco Antônio, Domingos de Melo, Guylherme Santos

import sys
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QListWidget,
    QMessageBox, QDialogButtonBox, QHeaderView
)

CATEGORIAS = ["Ação", "Comédia", "Drama", "Terror", "Ficção Científica", "Animação"]

def filmes_iniciais():
    return [
        {"titulo": "O Poderoso Chefão", "categoria": "Drama", "copias": 3, "total_copias": 3, "disponivel": True},
        {"titulo": "De Volta para o Futuro", "categoria": "Ficção Científica", "copias": 2, "total_copias": 2, "disponivel": True},
        {"titulo": "Toy Story", "categoria": "Animação", "copias": 4, "total_copias": 4, "disponivel": True},
        {"titulo": "O Iluminado", "categoria": "Terror", "copias": 1, "total_copias": 1, "disponivel": True},
        {"titulo": "Sonic The Hedgehog 3", "categoria": "Ação", "copias": 5, "total_copias": 5, "disponivel": True},
    ]

def clientes_iniciais():
    return ["Marco Antônio", "Domingos de Melo", "Guylherme Santos"]

class DialogoNovoFilme(QDialog):

    filme_cadastrado = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastrar Filme")
        self.setFixedSize(320, 220)

        self.campo_titulo = QLineEdit()
        self.campo_titulo.setPlaceholderText("Ex: Interestelar")

        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(CATEGORIAS)

        self.spin_copias = QSpinBox()
        self.spin_copias.setRange(1, 50)
        self.spin_copias.setValue(1)

        self.check_disponivel = QCheckBox("Disponível para locação")
        self.check_disponivel.setChecked(True)

        formulario = QFormLayout()
        formulario.addRow("Título:", self.campo_titulo)
        formulario.addRow("Categoria:", self.combo_categoria)
        formulario.addRow("Cópias:", self.spin_copias)
        formulario.addRow("", self.check_disponivel)

        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botoes.accepted.connect(self.confirmar_cadastro)
        botoes.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(formulario)
        layout.addWidget(botoes)
        self.setLayout(layout)

    def confirmar_cadastro(self):
        titulo = self.campo_titulo.text().strip()

        if not titulo:
            QMessageBox.warning(self, "Campo obrigatório", "Informe o título do filme.")
            return

        novo_filme = {
            "titulo": titulo,
            "categoria": self.combo_categoria.currentText(),
            "copias": self.spin_copias.value(),
            "total_copias": self.spin_copias.value(),
            "disponivel": self.check_disponivel.isChecked(),
        }

        self.filme_cadastrado.emit(novo_filme)
        QMessageBox.information(self, "Sucesso", f"Filme '{titulo}' cadastrado!")
        self.accept()

class DialogoAlugarFilme(QDialog):

    filme_alugado = Signal(str, str)  

    def __init__(self, titulo_filme: str, lista_clientes: list, parent=None):
        super().__init__(parent)
        self.titulo_filme = titulo_filme
        self.setWindowTitle("Alugar Filme")
        self.setFixedSize(300, 160)

        self.combo_cliente = QComboBox()
        self.combo_cliente.addItems(lista_clientes)

        botao_confirmar = QPushButton("Confirmar Locação")
        botao_confirmar.clicked.connect(self.confirmar_locacao)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Filme: {titulo_filme}"))
        layout.addWidget(QLabel("Cliente:"))
        layout.addWidget(self.combo_cliente)
        layout.addWidget(botao_confirmar)
        self.setLayout(layout)

    def confirmar_locacao(self):
        cliente = self.combo_cliente.currentText()
        resposta = QMessageBox.question(
            self,
            "Confirmar locação",
            f"Alugar '{self.titulo_filme}' para {cliente}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resposta == QMessageBox.Yes:
            self.filme_alugado.emit(self.titulo_filme, cliente)
            self.accept()

class JanelaClientes(QMainWindow):

    cliente_adicionado = Signal(str)
    cliente_removido = Signal(str)

    def __init__(self, lista_clientes: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clientes Cadastrados")
        self.setFixedSize(320, 300)

        self.lista_widget = QListWidget()
        self.lista_widget.addItems(lista_clientes)

        self.campo_novo_cliente = QLineEdit()
        self.campo_novo_cliente.setPlaceholderText("Nome do novo cliente...")

        botao_adicionar = QPushButton("Adicionar Cliente")
        botao_adicionar.clicked.connect(self.adicionar_cliente)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Clientes da locadora:"))
        layout.addWidget(self.lista_widget)
        layout.addWidget(self.campo_novo_cliente)
        layout.addWidget(botao_adicionar)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


        barra = self.addToolBar("Clientes")
        acao_remover = QAction("Remover Selecionado", self)
        acao_remover.triggered.connect(self.remover_cliente_selecionado)
        barra.addAction(acao_remover)

        self.statusBar().showMessage(f"{self.lista_widget.count()} cliente(s) cadastrado(s)")

    def adicionar_cliente(self):
        nome = self.campo_novo_cliente.text().strip()
        if not nome:
            QMessageBox.warning(self, "Campo vazio", "Digite o nome do cliente.")
            return

        for i in range(self.lista_widget.count()):
            if self.lista_widget.item(i).text() == nome:
                QMessageBox.warning(self, "Cliente existente", "Este cliente já está cadastrado.")
                return

        self.lista_widget.addItem(nome)
        self.cliente_adicionado.emit(nome)
        self.campo_novo_cliente.clear()
        self.statusBar().showMessage(f"{self.lista_widget.count()} cliente(s) cadastrado(s)")

    def remover_cliente_selecionado(self):
        item_atual = self.lista_widget.currentItem()
        if item_atual is None:
            QMessageBox.warning(self, "Nenhuma seleção", "Selecione um cliente para remover.")
            return

        resposta = QMessageBox.question(
            self, "Confirmar remoção",
            f"Remover o cliente '{item_atual.text()}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resposta == QMessageBox.Yes:
            nome_cliente = item_atual.text()
            linha = self.lista_widget.row(item_atual)
            self.lista_widget.takeItem(linha)
            self.cliente_removido.emit(nome_cliente)
            self.statusBar().showMessage(f"{self.lista_widget.count()} cliente(s) cadastrado(s)")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.remover_cliente_selecionado()
        super().keyPressEvent(event)

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Locadora de Filmes")
        self.resize(700, 450)

        self.filmes = filmes_iniciais()
        self.clientes = clientes_iniciais()
        self.janela_clientes = None  

        self._montar_interface()
        self._montar_toolbar()
        self._montar_menu()

        self.statusBar().showMessage("Pronto")


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

        acao_novo_filme = QAction("Novo Filme", self)
        acao_novo_filme.setShortcut(QKeySequence("Ctrl+N"))
        acao_novo_filme.triggered.connect(self.abrir_dialogo_novo_filme)
        barra.addAction(acao_novo_filme)

        barra.addSeparator()

        acao_clientes = QAction("Clientes", self)
        acao_clientes.triggered.connect(self.abrir_janela_clientes)
        barra.addAction(acao_clientes)

    def _montar_menu(self):
        
        menu_arquivo = self.menuBar().addMenu("Arquivo")

        acao_novo = QAction("Novo Filme", self)
        acao_novo.setShortcut(QKeySequence("Ctrl+N"))
        acao_novo.triggered.connect(self.abrir_dialogo_novo_filme)
        menu_arquivo.addAction(acao_novo)

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
        dialogo = DialogoNovoFilme(self)
        dialogo.filme_cadastrado.connect(self.cadastrar_filme)
        dialogo.exec()

    def cadastrar_filme(self, filme: dict):
        self.filmes.append(filme)
        self._atualizar_tabela()
        self.statusBar().showMessage(f"Filme '{filme['titulo']}' cadastrado", 4000)

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
        for filme in self.filmes:
            if filme["titulo"] == titulo:
                if filme["copias"] > 0:
                    filme["copias"] -= 1
                
                if filme["copias"] == 0:
                    filme["disponivel"] = False
                break

        self._atualizar_tabela()
        self.statusBar().showMessage(f"'{titulo}' alugado para {cliente}", 5000)

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
            filme["copias"] += 1
            filme["disponivel"] = True
            self._atualizar_tabela()
            self.statusBar().showMessage(f"Cópia de '{filme['titulo']}' devolvida", 4000)

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
            self.filmes.pop(linha)
            self._atualizar_tabela()
            self.statusBar().showMessage("Filme removido", 4000)

    def abrir_janela_clientes(self):
        if self.janela_clientes is None:
            self.janela_clientes = JanelaClientes(self.clientes, self)
            self.janela_clientes.cliente_adicionado.connect(self.registrar_novo_cliente)
            self.janela_clientes.cliente_removido.connect(self.remover_cliente_lista)

        self.janela_clientes.show()
        self.janela_clientes.raise_()
        self.janela_clientes.activateWindow()

    def registrar_novo_cliente(self, nome: str):
        if nome not in self.clientes:
            self.clientes.append(nome)

    def remover_cliente_lista(self, nome: str):
        if nome in self.clientes:
            self.clientes.remove(nome)

    def mostrar_sobre(self):
        QMessageBox.about(
            self, "Sobre",
            "Sistema de Locadora de Filmes\n"
            "Trabalho de POO II - PySide6\n",
        )


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
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())