# Changelog para as entregas parciais da Locadora de Filmes

## Entrega 1 - 08/10/2026

### Refatoração e Modularização (Marco Antônio)

- **Arquitetura MVC:** O código que antes estava em um único arquivo `main.py` foi reorganizado em diretórios (`models/` e `views/`).
- **Modelos (`models/`):** As classes de entidade `Filme` e `Cliente` foram extraídas e separadas (`filme.py`, `cliente.py`), isolando a lógica de negócio.
- **Camada de Visão (`views/`):** As interfaces gráficas (PySide6) foram divididas em módulos independentes (`main_window.py`, `janela_clientes.py`, `dialogo_novo_filme.py`, `dialogo_alugar.py`), facilitando a manutenção e colaboração.
- **Ponto de Entrada (`main.py`):** O arquivo principal agora atua apenas como inicializador da aplicação e das janelas modulares.

## Entrega 2 - 16/10/2026

(bla bla bla)
