from PySide6.QtCore import QThread, Signal

class IOThread(QThread):

    concluido = Signal(object)
    erro = Signal(str)

    # Recebe uma função demorada e seus argumentos para executar assincronamente
    def __init__(self, funcao, *args, parent=None):
        super().__init__(parent)
        self.funcao = funcao
        self.args = args

    # Executa a função na thread secundária e emite o resultado ou eventual exceção
    def run(self):
        try:
            resultado = self.funcao(*self.args)
        except Exception as e:
            self.erro.emit(str(e))
            return

        self.concluido.emit(resultado)