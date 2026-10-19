# Locadora de Filmes — Sistema Desktop com PySide6

Sistema Desktop completo para gerenciamento de catálogo, clientes e locações de uma locadora de filmes, desenvolvido em Python utilizando a biblioteca gráfica **PySide6 (Qt para Python)**.

Projeto desenvolvido para a disciplina de **Programação Orientada a Objetos II (POO II)** do curso de **Bacharelado em Sistemas de Informação** da **Universidade Federal do Piauí (UFPI) — Campus Senador Helvídio Nunes de Barros (CSHNB)**.

## Equipe de Desenvolvimento

- **Marco Antônio**
- **Domingos de Melo**
- **Guylherme Santos**

## Sumário

1. [Arquitetura de Software: Padrão MVC](#-arquitetura-de-software-padrão-mvc)
   - [O que é o padrão MVC?](#o-que-é-o-padrão-mvc)
   - [Como o MVC foi aplicado neste projeto?](#como-o-mvc-foi-aplicado-neste-projeto)
   - [Por que usamos o padrão MVC? (Vantagens)](#por-que-usamos-o-padrão-mvc-vantagens)
2. [Concorrência, Multithreading e Sincronização (2ª Entrega)](#-concorrência-multithreading-e-sincronização-2ª-entrega)
   - [O Problema do Congelamento da Interface (GUI)](#o-problema-do-congelamento-da-interface-gui)
   - [A Solução com Threads e Signals/Slots](#a-solução-com-threads-e-signalsslots)
   - [Sincronização com QMutex e Prevenção de Condições de Corrida](#sincronização-com-qmutex-e-prevenção-de-condições-de-corrida)
   - [As Três Threads do Sistema](#as-três-threads-do-sistema)
3. [Persistência de Dados Poliglota (Sem SGBD)](#-persistência-de-dados-poliglota-sem-sgbd)
4. [Funcionalidades do Sistema](#-funcionalidades-do-sistema)
5. [Estrutura do Projeto](#-estrutura-do-projeto)
6. [Atalhos de Teclado](#-atalhos-de-teclado)

## Arquitetura de Software: Padrão MVC

### O que é o padrão MVC?

O **MVC (Model-View-Controller)** é um dos padrões de arquitetura de software mais consolidados na engenharia de computação. Sua finalidade principal é a **Separação de Responsabilidades (Separation of Concerns - SoC)**, dividindo o software em três camadas fundamentais:

```text
               ┌────────────────────────┐
               │         VIEW           │
               │ (Interface com Usuário)│
               └───────────┬────────────┘
                    ▲      │
       Notifica via │      │ Dispara Ações/Eventos
      Signals/Slots │      ▼
               ┌────┴───────────────────┐
               │ CONTROLLER / SERVICE   │
               │  (Regras e Mediação)   │
               └───────────┬────────────┘
                    ▲      │
      Atualiza/Lê   │      │ Persiste/Modifica
                    │      ▼
               ┌────────────────────────┐
               │         MODEL          │
               │ (Dados e Persistência) │
               └────────────────────────┘
```

1. **Model (Modelo):** Representa o núcleo do domínio, a estrutura dos dados e os mecanismos que garantem a integridade das informações persistidas. Não tem conhecimento sobre botões, cores ou janelas.
2. **View (Visão):** Representa a interface visual com a qual o usuário interage. É responsável por renderizar tabelas, caixas de diálogo, capturar cliques e teclas, repassando essas intenções sem executar diretamente operações de persistência ou regras de negócio complexas.
3. **Controller (Controlador / Camada de Serviço):** Atua como o maestro do sistema. Recebe os estímulos da _View_, processa as regras de negócio pertinentes, consulta ou altera o _Model_, orquestra chamadas assíncronas e devolve os dados mastigados para que a _View_ apenas os exiba.

### Como o MVC foi aplicado neste projeto?

No nosso projeto, a estrutura de pastas e módulos reflete diretamente essa divisão:

- **Camada de Model (`models/` e `storage/`):**
  - `models/filme.py` e `models/cliente.py`: Definem as entidades, categorias padrão e geradores de dados iniciais.
  - `storage/json_storage.py`: CRUD dos filmes e clientes estruturados em arquivos JSON (`data/filmes.json` e `data/clientes.json`).
  - `storage/csv_storage.py`: Estruturação tabular de transações (`data/historico.csv`) e relatórios analíticos.
  - `storage/log_txt.py`: Log de auditoria cronológica em texto legível (`data/transacoes.txt`).

- **Camada de View (`views/`):**
  - `views/main_window.py`: Tela principal contendo a tabela de filmes, menus, barra de ferramentas, botões de ação e barra de status.
  - `views/janela_clientes.py`: Janela dedicada para gerenciar a lista de clientes cadastrados.
  - `views/dialogo_novo_filme.py`: Modal de cadastro de novo título com validações de entrada.
  - `views/dialogo_alugar.py`: Modal de confirmação e seleção de cliente para locação.
  - `views/dialog_progress.py`: Diálogo modal com `QProgressBar` para exibir o avanço percentual da exportação de relatórios.

- **Camada de Controller / Service (`services/` e mediadores nas Views):**
  - `services/locadora_service.py`: Centraliza a lógica de negócios da locadora (locação, devolução com baixa inteligente de cliente pendente, controle de cópias e atomicidade de operações). Funciona como o controlador de domínio, isolando a interface gráfica dos detalhes dos arquivos.
  - O fluxo da `MainWindow` recebe os eventos da interface, despacha as tarefas para as threads e conecta os sinais de retorno aos slots de atualização da tela.

### Por que usamos o padrão MVC? (Vantagens)

1. **Baixo Acoplamento:** A interface gráfica não sabe se os dados estão em JSON, CSV ou em um banco relacional SQLite/PostgreSQL. Caso decidamos trocar o formato de arquivo no futuro, a camada `views/` não precisará de nenhuma alteração.
2. **Alta Coesão:** Cada classe possui uma responsabilidade única e bem definida. Por exemplo, a classe `DialogProgress` preocupa-se apenas em desenhar e animar a barra de progresso; ela não precisa saber como o relatório é calculado.
3. **Facilidade no Trabalho Colaborativo:** O MVC permitiu que três desenvolvedores trabalhassem simultaneamente em branches separadas sem causar conflitos de mesclagem (merge conflicts), dividindo tarefas entre telas, armazenamento e regras de negócio.
4. **Manutenibilidade e Testabilidade:** Falhas em regras de cálculo ou na escrita em disco podem ser testadas e depuradas isoladamente, sem precisar instanciar componentes visuais complexos da interface gráfica.

## Concorrência, Multithreading e Sincronização (2ª Entrega)

### O Problema do Congelamento da Interface (GUI)

Aplicações gráficas baseadas em Qt operam em torno de um **Event Loop** que roda na chamada **Thread Principal (GUI Thread)**. Quando uma operação de leitura/escrita em disco (I/O) ou um processamento matemático pesado é executado dentro da thread principal:

- O loop de eventos congela;
- A janela deixa de responder ao sistema operacional (o cursor vira "ampulheta" ou "roda de espera");
- Eventos de clique, rolagem e repintura de tela deixam de ser processados;
- O usuário tem a impressão de que o sistema travou ("Não respondendo").

### A Solução com Threads e Signals/Slots

Para manter a interface **100% fluida e responsiva**, todas as operações de disco e processamento analítico foram migradas para threads secundárias utilizando a classe `QThread` do PySide6.

A comunicação entre threads segue o paradigma seguro do Qt:

- **Threads secundárias nunca manipulam diretamente widgets da interface** (o que geraria falhas de segmentação ou comportamentos imprevisíveis).
- As threads secundárias processam os dados e emitem **Signals** (`concluido`, `erro`, `progresso`).
- A thread principal conecta esses sinais a **Slots** (métodos da interface), atualizando a tela com total segurança e sem travamento.

### Sincronização com QMutex e Prevenção de Condições de Corrida

Com múltiplos processos concorrentes rodando em paralelo (ex: o usuário alugando um filme enquanto o auto-backup salva os dados e o gerador de relatórios lê o catálogo), surge o risco crítico de **Condição de Corrida (Race Condition)** e corrupção de arquivos.

Para garantir a consistência das informações:

- Criamos um objeto `QMutex` global em `utils/concurrency.py` (`mutex_arquivos`).
- Na camada `LocadoraService`, toda leitura, alteração e gravação é envolvida em um bloco protegido por **`QMutexLocker(mutex_arquivos)`**.
- O `QMutexLocker` utiliza o idioma RAII (_Resource Acquisition Is Initialization_): ao entrar no bloco `with`, ele trava o mutex (_lock_); ao sair do bloco (mesmo em caso de exceção), ele destrava automaticamente (_unlock_).
- Isso garante a **atomicidade** das operações críticas de ler -> validar -> decrementar estoque -> gravar em JSON e registrar em CSV/TXT.

### As Três Threads do Sistema

| Thread                     | Classe         | Arquivo                    | Responsável      | Papel no Sistema                                                                                                                                                                                           |
| :------------------------- | :------------- | :------------------------- | :--------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **I/O Assíncrono**         | `IOThread`     | `threads/io_thread.py`     | Marco Antônio    | Executa cargas iniciais, cadastro, remoção, locação e devolução sem travar a janela principal. Desabilita momentaneamente os botões de ação e os reabilita ao término.                                     |
| **Auto-Backup**            | `BackupThread` | `threads/backup_thread.py` | Domingos de Melo | Roda continuamente em background a cada intervalo configurável (padrão: 5 minutos), lendo os dados de forma sincronizada e atualizando a barra de status com a mensagem `"Último backup: HH:MM"`.          |
| **Exportação & Progresso** | `ExportThread` | `threads/export_thread.py` | Guylherme Santos | Compila estatísticas pesadas (filmes mais alugados, clientes mais ativos, pendências), emite sinais percentuais (`0% -> 25% -> 50% -> 75% -> 100%`) e aciona a barra de progresso visual `DialogProgress`. |

## Persistência de Dados Poliglota (Sem SGBD)

O sistema cumpre integralmente a exigência de manipulação de múltiplos formatos de arquivo em disco sem uso de banco de dados relacional:

1. **JSON (`data/filmes.json`, `data/clientes.json`):**
   - Utilizado para dados estruturados com atributos ricos (título, categoria, total de cópias, cópias disponíveis, status booleano de disponibilidade).
   - Manipulado pela classe `JsonStorage` com encoding `utf-8` e indentação legível.
   - Gera automaticamente dados de demonstração caso os arquivos ainda não existam no primeiro boot.

2. **CSV (`data/historico.csv`):**
   - Utilizado para registros transacionais em formato tabular delimitado por vírgulas.
   - Colunas: `id_transacao`, `data_hora`, `tipo` (LOCACAO / DEVOLUCAO), `titulo`, `cliente`.
   - Manipulado pela classe `CsvStorage`, oferecendo métodos analíticos para ranking de mais alugados, histórico de pendências e estatísticas da locadora.

3. **TXT (`data/transacoes.txt` e `data/relatorio_exportado.txt`):**
   - Utilizado para auditoria cronológica em linguagem natural via `LogTxt` (ex: `"[16/10/2026 14:32:10] LOCAÇÃO: Filme 'Toy Story' alugado para 'Marco Antônio'"`).
   - Utilizado também pelo `ExportThread` para gerar um relatório textual formatado e pronto para impressão ou leitura por humanos.

## Funcionalidades do Sistema

### Catálogo e Gestão de Filmes

- **Listagem Dinâmica:** Tabela com redimensionamento automático de colunas, exibindo Título, Categoria, Cópias e Status ("Disponível" ou "Alugado").
- **Cadastro Completo (`Ctrl+N`):** Modal com seleção de categoria, ajuste de cópias (1 a 50) e validação de títulos duplicados (_case-insensitive_).
- **Locação Inteligente:** Seleção de cliente cadastrado, decremento de estoque e bloqueio automático quando as cópias se esgotam.
- **Devolução com Rastreamento:** Incrementa o acervo respeitando o limite original de cópias e identifica automaticamente qual cliente estava com a locação pendente através do CSV.
- **Exclusão Segura (`Delete`):** Confirmação prévia via `QMessageBox` antes da remoção definitiva do acervo.

### Gerenciamento de Clientes

- **Janela Dedicada:** Interface de clientes com contagem em tempo real na barra de status.
- **Inclusão e Remoção:** Adição rápida com validação contra nomes repetidos e suporte ao atalho `Delete` para remoção com confirmação.

### Relatórios e Processamento em Background

- **Exportação com Barra de Progresso (`Ctrl+E`):** Diálogo modal com `QProgressBar` sincronizado com os sinais da `ExportThread`, gerando `data/relatorio_exportado.txt`.
- **Auto-Backup Periódico:** Salvamento silencioso em background com notificação suave na barra de status.
- **Encerramento Seguro:** Diálogo de confirmação de saída que aguarda o término de todas as threads ativas antes de finalizar o processo.

## Estrutura do Projeto

```text
.
├── main.py                          # Ponto de entrada (QApplication e loop principal)
├── models/                          # CAMADA MODEL (Definição das entidades de domínio)
│   ├── __init__.py
│   ├── filme.py                     # Entidade Filme, categorias e dados padrão
│   └── cliente.py                   # Entidade Cliente e dados padrão
├── views/                           # CAMADA VIEW (Interfaces gráficas PySide6)
│   ├── __init__.py
│   ├── main_window.py               # Janela principal (tabela, menus, atalhos, barra de status)
│   ├── janela_clientes.py           # Janela de visualização e cadastro de clientes
│   ├── dialogo_novo_filme.py        # Diálogo modal para cadastro de títulos
│   ├── dialogo_alugar.py            # Diálogo modal para locação de filme
│   └── dialog_progress.py           # Diálogo modal com QProgressBar para relatórios
├── services/                        # CAMADA CONTROLLER / SERVICE (Regras de negócio)
│   ├── __init__.py
│   └── locadora_service.py          # Serviço unificado com isolamento e QMutexLocker
├── storage/                         # CAMADA DE PERSISTÊNCIA (Arquivos em disco sem SGBD)
│   ├── __init__.py
│   ├── json_storage.py              # Leitura e escrita JSON (filmes e clientes)
│   ├── csv_storage.py               # Transações em CSV e relatórios analíticos
│   └── log_txt.py                   # Log cronológico de transações em TXT
├── threads/                         # CONCORRÊNCIA E MULTITHREADING (QThread)
│   ├── __init__.py
│   ├── io_thread.py                 # Thread genérica para operações assíncronas de I/O
│   ├── backup_thread.py             # Thread de auto-backup temporizado em segundo plano
│   └── export_thread.py             # Thread de exportação de relatório com progresso percentual
├── utils/                           # UTILITÁRIOS COMPARTILHADOS
│   ├── __init__.py
│   └── concurrency.py               # Instância global do QMutex para proteção de arquivos
├── data/                            # DIRETÓRIO DE DADOS (Gerado em tempo de execução)
│   ├── filmes.json
│   ├── clientes.json
│   ├── historico.csv
│   ├── transacoes.txt
│   └── relatorio_exportado.txt
├── CHANGELOG.md                     # Histórico detalhado das entregas parciais
└── README.md                        # Documentação oficial do projeto
```

## Atalhos de Teclado

| Atalho     | Ação                                                                              |
| :--------- | :-------------------------------------------------------------------------------- |
| `Ctrl + N` | Abre o diálogo para cadastrar um novo filme no catálogo                           |
| `Ctrl + E` | Inicia a exportação assíncrona do relatório com barra de progresso                |
| `Delete`   | Remove o filme selecionado na tabela principal ou o cliente na janela de clientes |
