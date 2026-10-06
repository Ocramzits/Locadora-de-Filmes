# Locadora de Filmes

Sistema Desktop para gerenciamento de catálogo e locações de uma locadora de filmes, desenvolvido em Python utilizando a biblioteca gráfica **PySide6**.

## Integrantes do Grupo

- Marco Antônio
- Domingos de Melo
- Guylherme Santos

## Funcionalidades

### Gerenciamento de Filmes

- **Catálogo Interativo:** Exibição em tabela com Título, Categoria, Cópias Disponíveis e Status.
- **Cadastro de Filmes:** Inclusão de novos títulos especificando categoria, quantidade inicial de cópias e status de disponibilidade.
- **Locação de Filmes:** Associação da locação a um cliente cadastrado, atualizando as cópias disponíveis em tempo real.
- **Devolução de Filmes:** Controle e incremento de cópias disponíveis respeitando o total do acervo.
- **Remoção de Títulos:** Exclusão de filmes via interface gráfica ou atalho de teclado (`Delete`).

### Gerenciamento de Clientes

- **Janela Dedicada:** Interface exclusiva para gerenciamento dos clientes cadastrados.
- **Adição e Remoção:** Adição de novos clientes (com prevenção de duplicatas) e remoção com janela de confirmação (suporta tecla `Delete`).

### Recursos da Interface (GUI)

- **Barra de Ferramentas e Menu:** Navegação por menus (_Arquivo_, _Cadastro_, _Ajuda_) e atalhos de teclado (ex: `Ctrl+N` para cadastrar filme).
- **Feedback ao Usuário:** Notificações, caixas de diálogo de aviso/confirmação (`QMessageBox`) e atualização contínua da barra de status.
- **Layout Responsivo:** Redimensionamento automático das colunas da tabela.
