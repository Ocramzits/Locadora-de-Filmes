from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QListWidget,
    QLineEdit, QPushButton, QMessageBox
)

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
