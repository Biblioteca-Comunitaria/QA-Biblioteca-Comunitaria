"""Page Object único da aplicação Biblioteca Luiz Brasil."""
from playwright.sync_api import Page, Locator, expect

# CPFs dos leitores do seed
CPF = {
    "Renally": "111.222.333-44",   # 1 empréstimo ativo (atrasado)
    "Abigail": "222.333.444-55",   # 2 empréstimos ativos (limite atingido)
    "Joao": "333.444.555-66",      # 0 ativos
    "Maria": "444.555.666-77",     # 0 ativos
}


class BibliotecaPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    # ---------- navegação ----------
    def abrir(self, rota: str = "livros"):
        self.page.goto(f"{self.base_url}/#{rota}")
        expect(self.page.locator("h1")).to_be_visible()

    def ir_para_hash(self, rota: str):
        self.page.evaluate("r => { location.hash = r }", rota)

    def menu(self, nome: str):
        self.page.locator("nav").get_by_role("button", name=nome, exact=True).click()

    @property
    def titulo(self) -> Locator:
        return self.page.locator("h1")

    @property
    def toast(self) -> Locator:
        return self.page.get_by_role("status")

    def aba(self, nome: str):
        self.page.locator(".tabs").get_by_role("button", name=nome, exact=True).click()

    def buscar(self, texto: str):
        self.page.locator("input.search").fill(texto)

    # ---------- livros ----------
    @property
    def cards_livros(self) -> Locator:
        return self.page.locator("button.card.bk")

    def card_livro(self, titulo: str) -> Locator:
        return self.cards_livros.filter(has_text=titulo)

    def abrir_livro(self, titulo: str):
        self.card_livro(titulo).click()
        expect(self.page.get_by_role("heading", name=titulo, level=2)).to_be_visible()

    def voltar(self):
        self.page.get_by_role("button", name="Voltar").click()

    # ---------- empréstimo (detalhe do livro) ----------
    @property
    def btn_salvar(self) -> Locator:
        return self.page.get_by_role("button", name="Salvar")

    def emprestar(self, cpf: str):
        self.page.locator("#cpf").fill(cpf)
        self.btn_salvar.click()

    def emprestar_livro(self, titulo: str, cpf: str):
        """Abre o livro, empresta e volta para a lista."""
        self.abrir_livro(titulo)
        self.emprestar(cpf)
        expect(self.toast).to_contain_text("Empréstimo feito")
        self.voltar()

    @property
    def painel_info(self) -> Locator:
        return self.page.locator(".panel")

    # ---------- cadastro de livro ----------
    def novo_livro(self):
        self.page.get_by_role("button", name="+ Novo livro").click()
        expect(self.titulo).to_have_text("Cadastro de novo livro")

    def preencher_livro(self, **campos):
        dados = dict(titulo="Grande Sertão: Veredas", autor="João Guimarães Rosa",
                     genero="Romance", editora="Companhia das Letras",
                     ano="1956", isbn="978-0000-0099", exemplares="2", status="Disponível")
        dados.update(campos)
        p = self.page
        p.get_by_label("Título", exact=True).fill(dados["titulo"])
        p.get_by_label("Nome do autor(a)").fill(dados["autor"])
        p.get_by_label("Gênero").fill(dados["genero"])
        p.get_by_label("Editora").fill(dados["editora"])
        p.get_by_label("Ano de publicação").fill(dados["ano"])
        p.get_by_label("ISBN (único)").fill(dados["isbn"])
        p.get_by_label("Exemplares disponíveis").fill(dados["exemplares"])
        p.get_by_label("Status").select_option(dados["status"])

    def cadastrar_livro(self):
        self.page.get_by_role("button", name="Cadastrar novo livro").click()

    # ---------- empréstimos (lista/detalhe) ----------
    @property
    def cards_emprestimos(self) -> Locator:
        return self.page.locator("button.card.loan")

    def card_emprestimo(self, titulo: str) -> Locator:
        return self.cards_emprestimos.filter(has_text=titulo)

    def abrir_emprestimo(self, titulo: str):
        self.card_emprestimo(titulo).click()
        expect(self.page.get_by_role("button", name="Voltar")).to_be_visible()

    # ---------- utilitários ----------
    def data_fmt(self, dias: int = 0) -> str:
        """Mesma formatação da aplicação (fmt) para hoje + N dias, calculada no navegador."""
        return self.page.evaluate(
            """n => { const d = new Date(Date.now() + n * 86400000);
              return new Date(d.getFullYear(), d.getMonth(), d.getDate())
                .toLocaleDateString('pt-BR', {day:'numeric', month:'short', year:'numeric'}); }""",
            dias,
        )

    def titulos_cards(self, cards: Locator) -> list[str]:
        return [t.strip() for t in cards.locator(".bt").all_inner_texts()]
