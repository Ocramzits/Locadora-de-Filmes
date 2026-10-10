from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QSpinBox, QCheckBox, QDialogButtonBox, QMessageBox
)
from models.filme import CATEGORIAS

class DialogoNovoFilme(QDialog):

    filme_cadastrado = Signal(dict)

    def __init__(self, titulos_existentes=None, parent=None):
        super().__init__(parent)
        self.titulos_existentes = titulos_existentes or []
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

        if titulo.lower() in [t.strip().lower() for t in self.titulos_existentes]:
            QMessageBox.warning(self, "Filme existente", "Este filme já está cadastrado.")
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