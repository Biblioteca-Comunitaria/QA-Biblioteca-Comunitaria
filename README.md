# 📚 Biblioteca – Testes Automatizados

Repositório destinado ao desenvolvimento e à execução de testes automatizados da aplicação **Biblioteca**, utilizando Python, Pytest e Playwright.

O projeto tem como objetivo validar as principais funcionalidades do sistema, garantindo maior confiabilidade, qualidade e estabilidade da aplicação.

## 🎯 Objetivo

Automatizar cenários de teste funcionais para verificar o comportamento da aplicação, incluindo cadastro de livros, empréstimos, devoluções, pesquisas, navegação e persistência de dados.

## 🛠️ Tecnologias utilizadas

- **Python 3** – Linguagem utilizada na implementação dos testes.
- **Pytest** – Framework para execução e organização dos testes.
- **Playwright** – Automação de navegadores e interações com a aplicação.
- **Chromium** – Navegador utilizado na execução dos testes.

## 📂 Estrutura do projeto

```text
biblioteca-testes/
│
├── pages/
│   └── Componentes e páginas utilizadas nos testes
│
├── tests/
│   ├── test_cadastro_livro.py
│   ├── test_emprestimo.py
│   ├── test_emprestimos_devolucao.py
│   ├── test_livros_listagem_busca.py
│   ├── test_navegacao.py
│   └── test_persistencia_config.py
│
├── conftest.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## ⚙️ Pré-requisitos

Antes de executar os testes, é necessário ter instalado:

- Python 3
- Node.js e npm
- Git

A aplicação Biblioteca deve estar disponível localmente para que os testes possam ser executados.

## 🚀 Instalação

**1. Clone o repositório:**

```bash
git clone URL_DO_REPOSITORIO
```

**2. Acesse a pasta:**

```bash
cd biblioteca-testes
```

**3. Crie um ambiente virtual:**

```bash
python -m venv .venv
```

**4. Ative o ambiente virtual:**

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

**5. Instale as dependências:**

```bash
python -m pip install -r requirements.txt
```

**6. Instale o navegador do Playwright:**

```bash
python -m playwright install chromium
```

## ▶️ Executando os testes

Primeiro, inicie a aplicação Biblioteca em outro terminal.

Em seguida, configure a URL da aplicação:

```powershell
$env:BASE_URL="http://localhost:5174"
```

Execute a suíte completa:

```bash
python -m pytest -v
```

Para executar um arquivo específico:

```bash
python -m pytest tests/test_cadastro_livro.py -v
```

## 📊 Resultado da execução

Na execução de validação realizada durante o desenvolvimento, foram obtidos os seguintes resultados:

- **110 testes executados**
- **110 testes aprovados**
- **0 falhas**
- **Tempo de execução:** aproximadamente 102 segundos.

## 🧪 Cenários contemplados

| Módulo | Cenários testados |
|---|---|
| Cadastro de livros | Validações, campos obrigatórios, ISBN e persistência |
| Empréstimos | Cadastro, CPF, disponibilidade e limites |
| Devoluções | Listagem, status, devolução e liberação de exemplares |
| Listagem e busca | Exibição, filtros, pesquisas e detalhes |
| Navegação | Rotas, menus e navegação entre telas |
| Persistência e configuração | LocalStorage, recarregamento e restauração de dados |

## 📌 Observações

- Os testes utilizam automação de navegador para interagir com a aplicação.
- A aplicação precisa estar em execução antes de iniciar a suíte.
- A variável `BASE_URL` permite configurar o endereço utilizado pelos testes.
- O ambiente virtual `.venv` não deve ser enviado ao GitHub.

---

**Projeto:** Biblioteca – Testes Automatizados  
**Finalidade:** Qualidade de software e automação de testes funcionais.
