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

### Integração Interface Gráfica e Persistência (Marco Antônio)

- **Camada de Serviço (`services/locadora_service.py`):** Criação da classe `LocadoraService`, que centraliza o uso de `JsonStorage`, `CsvStorage` e `LogTxt` e isola a interface dos detalhes de armazenamento.
- **Carregamento na Inicialização:** A `MainWindow` agora carrega filmes e clientes dos arquivos JSON ao abrir o aplicativo, em vez de usar listas fixas em memória.
- **Persistência Automática:** Cadastro, remoção, locação e devolução de filmes, bem como adição e remoção de clientes, são gravados imediatamente em disco.
- **Histórico de Transações:** Cada locação e devolução é registrada em `historico.csv` e em `transacoes.txt`; na devolução, o cliente é identificado pela locação pendente no histórico.
- **Prevenção de Duplicatas:** Os diálogos de novo filme e de clientes verificam títulos e nomes repetidos sem diferenciar maiúsculas e minúsculas.
- **Controle de Versão:** A pasta `data/` foi adicionada ao `.gitignore`, pois os arquivos são gerados em tempo de execução.

### I/O Assíncrono e Sincronização com QMutex (Marco Antônio)

- **Controle de Concorrência (`utils/concurrency.py`):** Criação do `mutex_arquivos` (`QMutex`), compartilhado por todo o sistema para proteger a leitura e a gravação dos arquivos da pasta `data/` contra condições de corrida.
- **Serviço Sincronizado (`services/locadora_service.py`):** Cada operação do `LocadoraService` passou a ser executada dentro de `QMutexLocker`, garantindo que as sequências de ler, alterar e gravar (locação e devolução) sejam atômicas.
- **Thread de I/O (`threads/io_thread.py`):** Implementação da classe `IOThread` (herda de `QThread`), que executa qualquer operação de arquivo em segundo plano e comunica o resultado à interface pelos sinais `concluido` e `erro`.
- **Interface Sem Travamentos (`views/main_window.py`):** Carregamento inicial, cadastro, locação, devolução e remoção passaram a rodar em `IOThread`. A interface é desabilitada durante a operação, é atualizada pelo slot ao receber o sinal e, ao fechar a janela, aguarda as threads em andamento.

### Auto-Backup em Background (Domingos de Melo)

- **Thread de Backup Temporizada (`threads/backup_thread.py`):** Implementação da classe `BackupThread` (herda de `QThread`), que roda em segundo plano e executa ciclos automáticos de salvamento do estado do sistema em intervalos configuráveis (padrão: 5 minutos), sem intervenção do usuário. Ao concluir cada ciclo, emite o sinal `backup_realizado` com o horário do último backup.
- **Indicativo Visual na Barra de Status (`views/main_window.py`):** A `MainWindow` instancia e inicia a `BackupThread` durante sua inicialização. O sinal `backup_realizado` está conectado ao slot `_ao_backup_realizado`, que exibe na barra de status da janela a mensagem "Último backup: HH:MM" por 10 segundos. O encerramento da aplicação interrompe a thread de backup de forma segura via `parar()` e `wait()`.
