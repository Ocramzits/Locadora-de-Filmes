from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox
)

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
