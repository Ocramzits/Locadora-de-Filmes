import csv
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = BASE_DIR / "data"


class CsvStorage:

    CABECALHO = ["id", "data_hora", "tipo", "titulo", "cliente", "observacao"]

    def __init__(self, data_dir: Optional[Path] = None, auto_inicializar: bool = True):
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path = self.data_dir / "historico.csv"

        if auto_inicializar:
            self.inicializar_arquivo()

    def inicializar_arquivo(self) -> None:
        if not self.csv_path.exists() or self.csv_path.stat().st_size == 0:
            with open(self.csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.CABECALHO)
                writer.writeheader()

    def registrar_transacao(self, tipo: str, titulo: str, cliente: str, observacao: str = "") -> Dict[str, str]:
        self.inicializar_arquivo()
        registro = {
            "id": str(uuid.uuid4())[:8],
            "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": tipo.strip().upper(),
            "titulo": titulo.strip(),
            "cliente": cliente.strip(),
            "observacao": observacao.strip()
        }
        with open(self.csv_path, "a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.CABECALHO)
            writer.writerow(registro)
        return registro

    def registrar_locacao(self, titulo: str, cliente: str, observacao: str = "") -> Dict[str, str]:
        return self.registrar_transacao("LOCACAO", titulo, cliente, observacao)

    def registrar_devolucao(self, titulo: str, cliente: str, observacao: str = "") -> Dict[str, str]:
        return self.registrar_transacao("DEVOLUCAO", titulo, cliente, observacao)
