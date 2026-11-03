# Testes automatizados – Biblioteca Luiz Brasil

Suíte E2E em **Python + pytest + Playwright**, escrita a partir do front React (Vite) enviado.

## Pré-requisitos
- Python 3.10+ e Node 18+
- Projeto React em `../biblioteca-react` (ou defina `APP_DIR`)

## Instalação
```bash
pip install -r requirements.txt
playwright install chromium
```

## Execução
```bash
pytest                       # sobe o `npm run dev` sozinho (porta 5173)
pytest -m smoke              # só os fluxos essenciais
pytest --headed --slowmo 300 # vendo o navegador
pytest -n 4                  # em paralelo (pip install pytest-xdist)
pytest --browser firefox     # outros navegadores

# usando um servidor já rodando
BASE_URL=http://localhost:5173 pytest
# projeto React em outro caminho
APP_DIR=/caminho/biblioteca-react pytest
```

## Organização
| Arquivo | Cobre |
|---|---|
| `tests/test_navegacao.py` | rotas por hash, menu, reset de busca/aba |
| `tests/test_livros_listagem_busca.py` | cards, disponibilidade, abas, busca (sem acento/caixa), detalhe |
| `tests/test_cadastro_livro.py` | **RF1** cadastro: sucesso, obrigatórios, ano, exemplares, ISBN único |
| `tests/test_emprestimo.py` | **RF3** empréstimo: CPF, prazo de 14 dias, limite de 2, sem exemplar, indisponível |
| `tests/test_emprestimos_devolucao.py` | lista/abas/busca de empréstimos, detalhe, **RF4** devolução |
| `tests/test_persistencia_config.py` | localStorage e "Restaurar dados iniciais" (`#config`) |
| `pages/biblioteca_page.py` | Page Object (seletores e ações reutilizáveis) |

## Observações
- Cada teste roda num contexto novo do navegador, então o `localStorage` começa vazio e a app carrega o **seed** (6 livros, 6 leitores, 4 empréstimos). Os testes dependem desses dados.
- Datas (hoje, +14 dias) são formatadas no próprio navegador com a mesma função da aplicação, evitando divergência de fuso/idioma.
- A tela de Configurações não tem item no menu; é acessada via `#config`.
