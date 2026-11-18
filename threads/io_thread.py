from PySide6.QtCore import QThread, Signal

class IOThread(QThread):

    concluido = Signal(object)
    erro = Signal(str)
    erro_conexao = Signal(str)

    def __init__(self, funcao, *args, parent=None):
        super().__init__(parent)
        self.funcao = funcao
        self.args = args

    def run(self):
        try:
            resultado = self.funcao(*self.args)
        except (ConnectionError, TimeoutError) as e:
            msg = str(e) or "Falha de conexão com o servidor remoto."
            self.erro_conexao.emit(msg)
            return
        except Exception as e:
            self.erro.emit(str(e))
            return

        self.concluido.emit(resultado)
