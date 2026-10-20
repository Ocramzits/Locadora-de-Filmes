from datetime import datetime
from pathlib import Path
from typing import List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = BASE_DIR / "data"


class LogTxt:

    # Inicializa o storage do log em texto puro (transacoes.txt)
    def __init__(self, data_dir: Optional[Path] = None, auto_inicializar: bool = True):
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.data_dir / "transacoes.txt"

        if auto_inicializar:
            self.inicializar_arquivo()

    # Cria o arquivo transacoes.txt se ele ainda não existir
    def inicializar_arquivo(self) -> None:
        if not self.log_path.exists():
            self.log_path.touch()

    # Formata e grava uma linha de log com timestamp, tipo, filme e cliente
    def gravar_log(self, tipo: str, titulo: str, cliente: str, observacao: str = "") -> str:
        self.inicializar_arquivo()
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tipo_formatado = tipo.strip().upper()
        obs_texto = f" | Observação: {observacao.strip()}" if observacao.strip() else ""
        linha = f"[{data_hora}] [{tipo_formatado}] Filme: '{titulo.strip()}' | Cliente: '{cliente.strip()}'{obs_texto}\n"
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(linha)
        return linha.strip()

    # Atalho para registrar log de uma LOCAÇÃO
    def registrar_locacao(self, titulo: str, cliente: str, observacao: str = "") -> str:
        return self.gravar_log("LOCACAO", titulo, cliente, observacao)

    # Atalho para registrar log de uma DEVOLUÇÃO
    def registrar_devolucao(self, titulo: str, cliente: str, observacao: str = "") -> str:
        return self.gravar_log("DEVOLUCAO", titulo, cliente, observacao)

    # Lê e retorna todas as linhas gravadas no arquivo de log
    def ler_logs(self) -> List[str]:
        if not self.log_path.exists():
            return []
        with open(self.log_path, "r", encoding="utf-8") as f:
            return [linha.strip() for linha in f if linha.strip()]

    # Limpa todo o conteúdo do arquivo transacoes.txt
    def limpar_logs(self) -> None:
        with open(self.log_path, "w", encoding="utf-8") as f:
            f.truncate(0)
