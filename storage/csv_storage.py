import csv
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = BASE_DIR / "data"


class CsvStorage:

    CABECALHO = ["id", "data_hora", "tipo", "titulo", "cliente", "observacao"]

    # Inicializa o storage CSV e cria o diretório/arquivo se necessário
    def __init__(self, data_dir: Optional[Path] = None, auto_inicializar: bool = True):
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path = self.data_dir / "historico.csv"

        if auto_inicializar:
            self.inicializar_arquivo()

    # Cria o arquivo CSV com o cabeçalho se ele ainda não existir
    def inicializar_arquivo(self) -> None:
        if not self.csv_path.exists() or self.csv_path.stat().st_size == 0:
            with open(self.csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.CABECALHO)
                writer.writeheader()

    # Grava uma nova transação com ID único e data/hora no arquivo CSV
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

    # Atalho para registrar uma transação de LOCAÇÃO no CSV
    def registrar_locacao(self, titulo: str, cliente: str, observacao: str = "") -> Dict[str, str]:
        return self.registrar_transacao("LOCACAO", titulo, cliente, observacao)

    # Atalho para registrar uma transação de DEVOLUÇÃO no CSV
    def registrar_devolucao(self, titulo: str, cliente: str, observacao: str = "") -> Dict[str, str]:
        return self.registrar_transacao("DEVOLUCAO", titulo, cliente, observacao)

    # Lê todas as linhas do CSV e retorna como lista de dicionários
    def carregar_transacoes(self) -> List[Dict[str, str]]:
        if not self.csv_path.exists() or self.csv_path.stat().st_size == 0:
            return []
        try:
            with open(self.csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                return [linha for linha in reader]
        except (csv.Error, OSError):
            return []

    # Retorna o histórico completo de transações
    def obter_transacoes(self) -> List[Dict[str, str]]:
        return self.carregar_transacoes()

    # Filtra as transações realizadas por um determinado cliente
    def buscar_por_cliente(self, cliente: str) -> List[Dict[str, str]]:
        cliente_alvo = cliente.strip().lower()
        return [
            t for t in self.carregar_transacoes()
            if t.get("cliente", "").strip().lower() == cliente_alvo
        ]

    # Filtra as transações relacionadas a um filme específico
    def buscar_por_filme(self, titulo: str) -> List[Dict[str, str]]:
        titulo_alvo = titulo.strip().lower()
        return [
            t for t in self.carregar_transacoes()
            if t.get("titulo", "").strip().lower() == titulo_alvo
        ]

    # Filtra as transações por tipo (LOCACAO ou DEVOLUCAO)
    def buscar_por_tipo(self, tipo: str) -> List[Dict[str, str]]:
        tipo_alvo = tipo.strip().upper()
        return [
            t for t in self.carregar_transacoes()
            if t.get("tipo", "").strip().upper() == tipo_alvo
        ]

    # Filtra as transações dentro de um intervalo de datas
    def buscar_por_periodo(self, data_inicio: str, data_fim: str) -> List[Dict[str, str]]:
        inicio = data_inicio.strip()
        fim = data_fim.strip()
        transacoes = self.carregar_transacoes()
        resultado = []
        for t in transacoes:
            data_t = t.get("data_hora", "")
            data_comparacao = data_t[:len(inicio)] if len(inicio) <= 10 else data_t
            if inicio <= data_comparacao <= fim:
                resultado.append(t)
        return resultado

    # Gera ranking com os filmes mais alugados a partir do CSV
    def gerar_relatorio_mais_alugados(self, limite: Optional[int] = None) -> List[Dict[str, Any]]:
        locacoes = [t["titulo"] for t in self.carregar_transacoes() if t.get("tipo") == "LOCACAO"]
        contagem = Counter(locacoes)
        ranking = [
            {"titulo": titulo, "total_locacoes": qtd}
            for titulo, qtd in contagem.most_common(limite)
        ]
        return ranking

    # Gera ranking com os clientes que mais realizaram locações
    def gerar_relatorio_clientes_mais_ativos(self, limite: Optional[int] = None) -> List[Dict[str, Any]]:
        clientes = [t["cliente"] for t in self.carregar_transacoes() if t.get("tipo") == "LOCACAO"]
        contagem = Counter(clientes)
        ranking = [
            {"cliente": cliente, "total_locacoes": qtd}
            for cliente, qtd in contagem.most_common(limite)
        ]
        return ranking

    # Identifica e retorna as locações pendentes (alugadas sem devolução correspondente)
    def obter_locacoes_pendentes(self) -> List[Dict[str, str]]:
        transacoes = self.carregar_transacoes()
        pendencias = []
        for t in transacoes:
            tipo = t.get("tipo", "").upper()
            if tipo == "LOCACAO":
                pendencias.append(t)
            elif tipo == "DEVOLUCAO":
                for i, p in enumerate(pendencias):
                    if (
                        p.get("titulo", "").strip().lower() == t.get("titulo", "").strip().lower()
                        and p.get("cliente", "").strip().lower() == t.get("cliente", "").strip().lower()
                    ):
                        pendencias.pop(i)
                        break
        return pendencias

    # Gera dados estatísticos gerais da locadora para relatórios
    def gerar_resumo_geral(self) -> Dict[str, Any]:
        transacoes = self.carregar_transacoes()
        total_locacoes = sum(1 for t in transacoes if t.get("tipo") == "LOCACAO")
        total_devolucoes = sum(1 for t in transacoes if t.get("tipo") == "DEVOLUCAO")
        clientes_distintos = len(set(t.get("cliente") for t in transacoes if t.get("cliente")))
        filmes_distintos = len(set(t.get("titulo") for t in transacoes if t.get("titulo")))
        pendentes = len(self.obter_locacoes_pendentes())
        return {
            "total_transacoes": len(transacoes),
            "total_locacoes": total_locacoes,
            "total_devolucoes": total_devolucoes,
            "locacoes_pendentes": pendentes,
            "total_clientes_distintos": clientes_distintos,
            "total_filmes_distintos": filmes_distintos,
        }
