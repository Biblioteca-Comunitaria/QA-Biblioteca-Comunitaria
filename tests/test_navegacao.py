from playwright.sync_api import expect
import pytest


@pytest.mark.smoke
def test_rota_padrao_e_livros(app):
    expect(app.titulo).to_have_text("Livros")
    expect(app.page.get_by_text("Olá, administrador!")).to_be_visible()
    expect(app.page.get_by_text("Luiz Brasil").first).to_be_visible()


def test_menu_alterna_entre_livros_e_emprestimos(app):
    app.menu("Empréstimo")
    expect(app.titulo).to_have_text("Empréstimo")
    expect(app.page).to_have_url(f"{app.base_url}/#emprestimos")
    app.menu("Livros")
    expect(app.titulo).to_have_text("Livros")


def test_hash_invalido_cai_em_livros(app):
    app.ir_para_hash("rota-inexistente")
    expect(app.titulo).to_have_text("Livros")


def test_busca_placeholder_muda_por_tela(app):
    busca = app.page.locator("input.search")
    expect(busca).to_have_attribute("placeholder", "Buscar por título ou autor...")
    app.menu("Empréstimo")
    expect(busca).to_have_attribute("placeholder", "Buscar por livro ou leitor...")


def test_trocar_de_tela_limpa_busca_e_aba(app):
    app.buscar("dom")
    app.aba("Disponíveis")
    app.menu("Empréstimo")
    app.menu("Livros")
    expect(app.page.locator("input.search")).to_have_value("")
    expect(app.cards_livros).to_have_count(6)


def test_busca_e_novo_livro_somem_no_detalhe(app):
    app.abrir_livro("Dom Casmurro")
    expect(app.page.locator("input.search")).to_have_count(0)
    expect(app.page.get_by_role("button", name="+ Novo livro")).to_have_count(0)
