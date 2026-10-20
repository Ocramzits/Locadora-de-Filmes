from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QHBoxLayout
)


class DialogProgress(QDialog):

    # Constrói o diálogo modal com barra de progresso, mensagem de status e botão fechar
    def __init__(self, parent=None, titulo="Exportando Relatório", mensagem="Processando exportação..."):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setFixedSize(380, 150)
        self.setModal(True)

        layout = QVBoxLayout()

        self.label_status = QLabel(mensagem)
        self.label_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_status)

        self.barra_progresso = QProgressBar()
        self.barra_progresso.setRange(0, 100)
        self.barra_progresso.setValue(0)
        self.barra_progresso.setAlignment(Qt.AlignCenter)
        self.barra_progresso.setTextVisible(True)
        layout.addWidget(self.barra_progresso)

        self.progress_bar = self.barra_progresso

        layout_botoes = QHBoxLayout()
        self.botao_fechar = QPushButton("Fechar")
        self.botao_fechar.setEnabled(False)
        self.botao_fechar.clicked.connect(self.accept)
        layout_botoes.addWidget(self.botao_fechar)
        layout.addLayout(layout_botoes)

        self.setLayout(layout)

    # Atualiza o valor da barra de progresso e habilita o botão fechar ao atingir 100%
    def atualizar_progresso(self, valor: int):
        self.barra_progresso.setValue(valor)
        if valor >= 100:
            self.label_status.setText("Exportação concluída com sucesso!")
            self.botao_fechar.setEnabled(True)

    # Define o valor numérico de progresso da barra
    def definir_progresso(self, valor: int):
        self.atualizar_progresso(valor)

    # Atualiza o texto descritivo do status
    def definir_status(self, texto: str):
        self.label_status.setText(texto)

    # Atualiza a interface indicando que a exportação foi concluída com êxito
    def ao_concluir(self, caminho_arquivo: str = ""):
        self.barra_progresso.setValue(100)
        self.label_status.setText("Exportação concluída com sucesso!")
        self.botao_fechar.setEnabled(True)

    # Atualiza a interface exibindo mensagem em caso de falha no processo
    def ao_erro(self, mensagem_erro: str):
        self.label_status.setText(f"Erro na exportação: {mensagem_erro}")
        self.botao_fechar.setEnabled(True)


DialogoProgresso = DialogProgress
