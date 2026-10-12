# Locadora de Filmes

Sistema Desktop para gerenciamento de catálogo e locações de uma locadora de filmes, desenvolvido em Python utilizando a biblioteca gráfica **PySide6**.

## Integrantes do Grupo

- Marco Antônio
- Domingos de Melo
- Guylherme Santos

## Funcionalidades

### Gerenciamento de Filmes

- **Catálogo Interativo:** Exibição em tabela com Título, Categoria, Cópias Disponíveis e Status.
- **Cadastro de Filmes:** Inclusão de novos títulos especificando categoria, quantidade inicial de cópias e status de disponibilidade, com prevenção de títulos duplicados.
- **Locação de Filmes:** Associação da locação a um cliente cadastrado, atualizando as cópias disponíveis em tempo real.
- **Devolução de Filmes:** Controle e incremento de cópias disponíveis respeitando o total do acervo.
- **Remoção de Títulos:** Exclusão de filmes via interface gráfica ou atalho de teclado (`Delete`).

### Gerenciamento de Clientes

- **Janela Dedicada:** Interface exclusiva para gerenciamento dos clientes cadastrados.
- **Adição e Remoção:** Adição de novos clientes (com prevenção de duplicatas, sem diferenciar maiúsculas e minúsculas) e remoção com janela de confirmação (suporta tecla `Delete`).

### Recursos da Interface (GUI)

- **Barra de Ferramentas e Menu:** Navegação por menus (_Arquivo_, _Cadastro_, _Ajuda_) e atalhos de teclado (ex: `Ctrl+N` para cadastrar filme).
- **Feedback ao Usuário:** Notificações, caixas de diálogo de aviso/confirmação (`QMessageBox`) e atualização contínua da barra de status.
- **Layout Responsivo:** Redimensionamento automático das colunas da tabela.

### Persistência de Dados

- **Arquivos em disco (sem SGBD):** filmes e clientes em JSON (`data/filmes.json`, `data/clientes.json`); histórico de locações e devoluções em CSV (`data/historico.csv`) e log cronológico em TXT (`data/transacoes.txt`).
- **Carregamento automático:** ao abrir o app os dados são lidos do disco; se os arquivos não existirem, são criados com dados iniciais.
- **Gravação imediata:** cadastro, remoção, locação e devolução de filmes, e adição e remoção de clientes, são gravados em disco a cada operação.
- **Histórico e relatórios:** consulta de transações por cliente, filme, tipo e período, ranking de filmes mais alugados, clientes mais ativos e locações pendentes.
- **Camada de serviço:** `services/locadora_service.py` liga a interface aos três storages.

### Concorrência e Threads

- **I/O assíncrono (`QThread`):** a leitura e a gravação dos arquivos rodam em segundo plano pela classe `IOThread` (`threads/io_thread.py`), evitando o congelamento da interface.
- **Comunicação por sinais e slots:** a thread emite os sinais `concluido` e `erro`; somente a thread principal atualiza os widgets.
- **Estado da interface:** enquanto uma operação de arquivo está em andamento, a janela fica desabilitada e a barra de status informa o progresso; ao fechar o aplicativo, as threads em execução são aguardadas.
- **Sincronização (`QMutex`):** o `mutex_arquivos` (`utils/concurrency.py`) protege o acesso aos arquivos da pasta `data/`, evitando condição de corrida entre threads. As operações do `LocadoraService` são executadas dentro de `QMutexLocker`, tornando atômicas as sequências de ler, alterar e gravar.

## Estrutura do Projeto

```text
main.py                      Ponto de entrada da aplicação
models/                      Entidades e dados iniciais (filme.py, cliente.py)
storage/                     Persistência em arquivos
    json_storage.py          Filmes e clientes (JSON)
    csv_storage.py           Histórico de transações e relatórios (CSV)
    log_txt.py               Log de eventos (TXT)
services/
    locadora_service.py      Regras de locação/devolução e acesso aos storages
threads/
    io_thread.py             QThread genérica para operações de I/O
utils/
    concurrency.py           QMutex compartilhado para proteção dos arquivos
views/                       Telas PySide6 (janela principal, clientes, diálogos)
data/                        Gerada automaticamente em tempo de execução
pdfs/                        Requisitos do projeto
CHANGELOG.md                 Histórico das entregas parciais
```
