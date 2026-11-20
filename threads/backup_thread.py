import json
import time
from pathlib import Path
from PySide6.QtCore import QThread, Signal

class BackupThread(QThread):

    backup_realizado = Signal(str)

    def __init__(self, service, intervalo_segundos=300, caminho_backup=None, parent=None):
        super().__init__(parent)
        self.service = service
        self.intervalo_segundos = intervalo_segundos
        self.caminho_backup = Path(caminho_backup) if caminho_backup else Path("data") / "backup_remoto.json"
        self._rodando = True

    def run(self):
        while self._rodando:
            for _ in range(int(self.intervalo_segundos)):
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
                self.backup_realizado.emit(timestamp)
            except Exception:
                pass

    def parar(self):
        self._rodando = False
