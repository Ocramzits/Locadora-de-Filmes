import json
import time
from pathlib import Path
from PySide6.QtCore import QThread, Signal

class BackupThread(QThread):

    backup_realizado = Signal(str)
    falha_backup = Signal(str)

    def __init__(self, service, intervalo_segundos=300, intervalo_retry=30, caminho_backup=None, parent=None):
        super().__init__(parent)
        self.service = service
        self.intervalo_segundos = intervalo_segundos
        self.intervalo_retry = intervalo_retry
        self.caminho_backup = Path(caminho_backup) if caminho_backup else Path("data") / "backup_remoto.json"
        self._rodando = True
        self._em_falha = False

    def run(self):
        while self._rodando:
            espera = self.intervalo_retry if self._em_falha else self.intervalo_segundos
            for _ in range(int(espera)):
                if not self._rodando:
                    return
                time.sleep(1)
            if not self._rodando:
                break
            try:
                filmes = self.service.listar_filmes()
                clientes = self.service.listar_clientes()
                pendentes = self.service.api_client.obter_locacoes_pendentes()
                timestamp = time.strftime("%H:%M")
                dados_snapshot = {
                    "data_hora": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "timestamp": timestamp,
                    "total_filmes": len(filmes),
                    "total_clientes": len(clientes),
                    "total_locacoes_pendentes": len(pendentes),
                    "filmes": filmes,
                    "clientes": clientes,
                    "locacoes_pendentes": pendentes,
                }
                self.caminho_backup.parent.mkdir(parents=True, exist_ok=True)
                with open(self.caminho_backup, "w", encoding="utf-8") as f:
                    json.dump(dados_snapshot, f, ensure_ascii=False, indent=2)
                self._em_falha = False
                self.backup_realizado.emit(timestamp)
            except Exception as e:
                self._em_falha = True
                self.falha_backup.emit(str(e))

    def parar(self):
        self._rodando = False
