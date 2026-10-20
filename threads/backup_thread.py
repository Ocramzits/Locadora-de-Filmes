import time
from PySide6.QtCore import QThread, Signal


class BackupThread(QThread):

    backup_realizado = Signal(str)

    # Inicializa a thread de backup periódico em background com intervalo definido
    def __init__(self, service, intervalo_segundos=300, parent=None):
        super().__init__(parent)
        self.service = service
        self.intervalo_segundos = intervalo_segundos
        self._rodando = True

    # Loop de execução da thread: aguarda o intervalo e emite o sinal com o horário do backup
    def run(self):
        while self._rodando:
            time.sleep(self.intervalo_segundos)
            if not self._rodando:
                break
            try:
                filmes = self.service.listar_filmes()
                clientes = self.service.listar_clientes()
                timestamp = time.strftime("%H:%M")
                self.backup_realizado.emit(timestamp)
            except Exception:
                pass

    # Sinaliza para a thread parar a execução do seu loop com segurança
    def parar(self):
        self._rodando = False
