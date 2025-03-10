# MailMass
Este projeto é um disparador de emails em massa com funcionalidades de personalização e gerenciamento de contatos.

## Funcionalidades

- **Envio de emails em massa**: Envie milhares de emails com apenas um clique.
- **Envio de emails personalizados**: Personalize cada email com informações específicas de cada contato.
- **Gerenciamento de contatos**: Insira, visualize, edite e exclua contatos facilmente.
- **Importação de contatos**: Importe contatos a partir de arquivos CSV de forma rápida e prática.
- **Configuração de servidor SMTP**: Configure seu servidor SMTP diretamente na interface do aplicativo.

## Requisitos

- **Python 3.x**
- Bibliotecas: `smtplib`, `time`, `threading`, `email`, `os`, `tkinter`, `sqlite3`, `configparser`

## Como usar

### Configuração

1. Clone o repositório:
    ```bash
    git clone https://github.com/seu-usuario/EmailBoom.git
    cd EmailBoom
    ```

2. Instale as dependências necessárias:
    ```bash
    pip install configparser
    ```

3. Configure o servidor SMTP na aba "Configurações" da interface.

### Envio de Emails

1. Preencha os campos necessários na aba "Envio de Emails".
2. Clique em "Iniciar Envio" para enviar emails em massa.
3. Clique em "Iniciar Envio Personalizado" para enviar emails personalizados.

### Gerenciamento de Contatos

1. Use a aba "Contatos" para inserir, visualizar, editar e excluir contatos.
2. Importe contatos a partir de arquivos CSV clicando em "Importar arquivo CSV".

## Estrutura do Projeto

- `main.py`: Arquivo principal que contém a interface e as funcionalidades.
- `banco.db`: Banco de dados SQLite para armazenar os contatos.
- `config.ini`: Arquivo de configuração para armazenar as configurações do servidor SMTP.

## Contribuição

Sinta-se à vontade para contribuir com o projeto. Faça um fork do repositório, crie uma branch para suas alterações e envie um pull request.

## Contato

Para mais informações, entre em contato com [felipes4nt@gmail.com](mailto:felipes4nt@gmail.com).

## Agradecimentos

Agradecemos a todos os contribuidores e usuários que ajudaram a melhorar este projeto.
