from datetime import date

from playwright.sync_api import expect
import pytest

from pages.biblioteca_page import CPF

ANO_ATUAL = date.today().year


@pytest.fixture
def form(app):
    app.novo_livro()
    return app


def _falha(app, msg):
    expect(app.toast).to_have_text(msg)
    expect(app.titulo).to_have_text("Cadastro de novo livro")   # continua no formulário


@pytest.mark.smoke
def test_cadastro_com_sucesso(form):
    form.preencher_livro()
    form.cadastrar_livro()
    expect(form.toast).to_have_text("Livro cadastrado!")
    expect(form.titulo).to_have_text("Livros")
    expect(form.cards_livros).to_have_count(7)
    expect(form.card_livro("Grande Sertão: Veredas")).to_contain_text("Disponível: 2 de 2")


def test_cadastro_com_status_indisponivel(form):
    form.preencher_livro(status="Indisponível", exemplares="3")
    form.cadastrar_livro()
    expect(form.card_livro("Grande Sertão")).to_contain_text("Indisponível: 0 de 3")
    form.aba("Indisponíveis")
    expect(form.card_livro("Grande Sertão")).to_be_visible()


def test_livro_cadastrado_aparece_na_busca_por_autor(form):
    form.preencher_livro()
    form.cadastrar_livro()
    form.buscar("guimaraes rosa")
    assert form.titulos_cards(form.cards_livros) == ["Grande Sertão: Veredas"]


def test_livro_cadastrado_persiste_apos_reload(form):
    form.preencher_livro()
    form.cadastrar_livro()
    form.page.reload()
    expect(form.cards_livros).to_have_count(7)
    expect(form.card_livro("Grande Sertão")).to_be_visible()


def test_livro_cadastrado_pode_ser_emprestado(form):
    form.preencher_livro()
    form.cadastrar_livro()
    form.abrir_livro("Grande Sertão")
    form.emprestar(CPF["Maria"])
    expect(form.toast).to_contain_text("Empréstimo feito para Maria Clara Souza")
    expect(form.painel_info).to_contain_text("Exemplares disponíveis – 1")


def test_cancelar_volta_para_lista_sem_cadastrar(form):
    form.preencher_livro()
    form.page.get_by_role("button", name="Cancelar").click()
    expect(form.titulo).to_have_text("Livros")
    expect(form.cards_livros).to_have_count(6)


def test_espacos_nas_bordas_sao_removidos(form):
    form.preencher_livro(titulo="   Livro com Espaços   ")
    form.cadastrar_livro()
    expect(form.toast).to_have_text("Livro cadastrado!")
    assert "Livro com Espaços" in form.titulos_cards(form.cards_livros)


@pytest.mark.parametrize("campo", ["titulo", "autor", "genero", "editora", "isbn"])
@pytest.mark.parametrize("valor", ["", "   "], ids=["vazio", "so_espacos"])
def test_campos_obrigatorios(form, campo, valor):
    form.preencher_livro(**{campo: valor})
    form.cadastrar_livro()
    _falha(form, "Preencha todos os campos.")
    form.page.get_by_role("button", name="Cancelar").click()
    expect(form.cards_livros).to_have_count(6)


@pytest.mark.parametrize("ano", ["", "999", "0", str(ANO_ATUAL + 2), "1999.5"],
                         ids=["vazio", "999", "zero", "futuro", "decimal"])
def test_ano_invalido(form, ano):
    form.preencher_livro(ano=ano)
    form.cadastrar_livro()
    _falha(form, "Informe um ano de publicação válido.")


@pytest.mark.parametrize("ano", ["1000", str(ANO_ATUAL), str(ANO_ATUAL + 1)])
def test_ano_limite_valido(form, ano):
    form.preencher_livro(ano=ano)
    form.cadastrar_livro()
    expect(form.toast).to_have_text("Livro cadastrado!")


@pytest.mark.parametrize("qtd", ["", "0", "-1", "1.5"], ids=["vazio", "zero", "negativo", "decimal"])
def test_exemplares_invalidos(form, qtd):
    form.preencher_livro(exemplares=qtd)
    form.cadastrar_livro()
    _falha(form, "Exemplares disponíveis deve ser ao menos 1.")


def test_exemplares_minimo_um_e_valido(form):
    form.preencher_livro(exemplares="1")
    form.cadastrar_livro()
    expect(form.card_livro("Grande Sertão")).to_contain_text("Disponível: 1 de 1")


@pytest.mark.parametrize("isbn", ["978-0000-0001", "97800000001", " 978-0000-0001 ", "978 0000 0001"],
                         ids=["igual", "so_digitos", "com_espacos", "outro_separador"])
def test_isbn_duplicado_e_rejeitado_mesmo_com_formatacao_diferente(form, isbn):
    form.preencher_livro(isbn=isbn)
    form.cadastrar_livro()
    _falha(form, "Já existe um livro com esse ISBN.")


def test_isbn_duplicado_de_livro_recem_cadastrado(form):
    form.preencher_livro()
    form.cadastrar_livro()
    form.novo_livro()
    form.preencher_livro(titulo="Outro título")
    form.cadastrar_livro()
    _falha(form, "Já existe um livro com esse ISBN.")


def test_formulario_inicia_com_valores_padrao(form):
    expect(form.page.get_by_label("Exemplares disponíveis")).to_have_value("1")
    expect(form.page.get_by_label("Status")).to_have_value("Disponível")
