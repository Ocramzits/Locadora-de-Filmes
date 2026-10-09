# Changelog para as entregas parciais da Locadora de Filmes

## Entrega 1 - 08/10/2026

### Refatoração e Modularização (Marco Antônio)

- **Arquitetura MVC:** O código que antes estava em um único arquivo `main.py` foi reorganizado em diretórios (`models/` e `views/`).
- **Modelos (`models/`):** As classes de entidade `Filme` e `Cliente` foram extraídas e separadas (`filme.py`, `cliente.py`), isolando a lógica de negócio.
- **Camada de Visão (`views/`):** As interfaces gráficas (PySide6) foram divididas em módulos independentes (`main_window.py`, `janela_clientes.py`, `dialogo_novo_filme.py`, `dialogo_alugar.py`), facilitando a manutenção e colaboração.
- **Ponto de Entrada (`main.py`):** O arquivo principal agora atua apenas como inicializador da aplicação e das janelas modulares.

### Persistência JSON e Manipulação de Dados em Disco (Domingos de Melo)

- **Camada de Persistência (`storage/`):** Criação do pacote de armazenamento estruturado para persistência de dados sem uso de SGBD.
- **Gerenciador JSON (`storage/json_storage.py`):** Implementação da classe `JsonStorage` com leitura e gravação em formato JSON e encoding UTF-8.
- **CRUD de Filmes:** Implementação de operações completas de consulta, inserção, atualização e remoção de filmes diretamente em disco (`filmes.json`).
- **CRUD de Clientes:** Implementação de operações de consulta, cadastro e exclusão de clientes em disco (`clientes.json`).
- **Inicialização Automática de Dados:** Verificação automática e geração dos arquivos com dados padrão caso ainda não existam no diretório de dados.

### Persistência CSV/TXT e Histórico de Transações (Guylherme Santos)

- **Módulo de Log e Histórico CSV (`storage/csv_storage.py`):** Implementação da classe `CsvStorage` para persistência e registro tabular de locações e devoluções em formato CSV (`historico.csv`).
- **Registro de Log em TXT (`storage/log_txt.py`):** Implementação da classe `LogTxt` para gravação de eventos cronológicos e operacionais da locadora em arquivo de texto legível (`transacoes.txt`).
- **Consulta de Histórico e Filtros:** Implementação de métodos de leitura e consulta de transações passadas a partir de arquivos CSV, permitindo filtragem por cliente, filme, tipo de operação e período.
- **Geração de Relatórios Básicos:** Métodos analíticos para identificar filmes mais alugados, clientes mais ativos, locações pendentes de devolução e resumo estatístico geral da locadora.
- **Exportação no Pacote (`storage/__init__.py`):** Disponibilização de `CsvStorage` e `LogTxt` no pacote de armazenamento para integração com o sistema.

## Entrega 2 - 16/10/2026

(A ser documentado com a implementação de threads e sincronização)
