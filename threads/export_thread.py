import time
from pathlib import Path
from PySide6.QtCore import QThread, Signal, QMutexLocker

from services.locadora_service import LocadoraService
from utils.concurrency import mutex_arquivos


class ExportThread(QThread):

    progresso = Signal(int)
    porcentagem = Signal(int)
    concluido = Signal(str)
    erro = Signal(str)

    def __init__(self, service=None, caminho_destino=None, parent=None):
        super().__init__(parent)
        self.service = service if service is not None else LocadoraService()
        self.caminho_destino = Path(caminho_destino) if caminho_destino else Path("data") / "relatorio_exportado.txt"

    def run(self):
        try:
            self.progresso.emit(0)
            self.porcentagem.emit(0)
            time.sleep(0.1)

            filmes = self.service.listar_filmes()
            clientes = self.service.listar_clientes()

            self.progresso.emit(25)
            self.porcentagem.emit(25)
            time.sleep(0.15)

            with QMutexLocker(mutex_arquivos):
                mais_alugados = self.service.csv_storage.gerar_relatorio_mais_alugados()
                clientes_ativos = self.service.csv_storage.gerar_relatorio_clientes_mais_ativos()
                pendentes = self.service.csv_storage.obter_locacoes_pendentes()
                resumo = self.service.csv_storage.gerar_resumo_geral()

            self.progresso.emit(50)
            self.porcentagem.emit(50)
            time.sleep(0.15)

            linhas = [
                "=" * 60,
                "RELATÓRIO GERAL DA LOCADORA DE FILMES",
                f"Data de emissão: {time.strftime('%d/%m/%Y %H:%M:%S')}",
                "=" * 60,
                "",
                "--- RESUMO OPERACIONAL ---",
                f"Total de Transações: {resumo.get('total_transacoes', 0)}",
                f"Total de Locações: {resumo.get('total_locacoes', 0)}",
                f"Total de Devoluções: {resumo.get('total_devolucoes', 0)}",
                f"Locações Pendentes: {resumo.get('locacoes_pendentes', 0)}",
                f"Clientes Cadastrados: {len(clientes)}",
                f"Filmes no Catálogo: {len(filmes)}",
                "",
                "--- FILMES MAIS ALUGADOS ---"
            ]

            for item in mais_alugados:
                linhas.append(f"- {item.get('titulo')}: {item.get('total_locacoes')} locações")

            linhas.append("")
            linhas.append("--- CLIENTES MAIS ATIVOS ---")
            for item in clientes_ativos:
                linhas.append(f"- {item.get('cliente')}: {item.get('total_locacoes')} locações")

            linhas.append("")
            linhas.append("--- LOCAÇÕES PENDENTES ---")
            for item in pendentes:
                linhas.append(f"- Filme: {item.get('titulo')} | Cliente: {item.get('cliente')} | Data: {item.get('data_hora')}")

            linhas.append("")
            linhas.append("--- CATÁLOGO COMPLETO ---")
            for f in filmes:
                status = "Disponível" if f.get("disponivel") else "Indisponível"
                linhas.append(f"- {f.get('titulo')} | Categoria: {f.get('categoria')} | Cópias: {f.get('copias')} | Status: {status}")

            linhas.append("")
            linhas.append("=" * 60)

            self.progresso.emit(75)
            self.porcentagem.emit(75)
            time.sleep(0.15)

            self.caminho_destino.parent.mkdir(parents=True, exist_ok=True)
            with open(self.caminho_destino, "w", encoding="utf-8") as f:
                f.write("\n".join(linhas) + "\n")

            self.progresso.emit(100)
            self.porcentagem.emit(100)
            time.sleep(0.05)
            self.concluido.emit(str(self.caminho_destino))

        except Exception as e:
            self.erro.emit(str(e))
