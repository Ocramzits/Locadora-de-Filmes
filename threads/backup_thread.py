import time
from PySide6.QtCore import QThread, Signal


class BackupThread(QThread):

    backup_realizado = Signal(str)

    def __init__(self, service, intervalo_segundos=300, parent=None):
        super().__init__(parent)
        self.service = service
        self.intervalo_segundos = intervalo_segundos
        self._rodando = True

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

    def parar(self):
        self._rodando = False
