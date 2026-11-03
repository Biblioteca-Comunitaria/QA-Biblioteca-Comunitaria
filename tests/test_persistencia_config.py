import json

from playwright.sync_api import expect

CHAVE = "biblioteca-luiz-brasil-v2"


def test_dados_iniciais_sao_gravados_no_localstorage(app):
    bruto = app.page.evaluate("k => localStorage.getItem(k)", CHAVE)
    dados = json.loads(bruto)
    assert len(dados["books"]) == 6
    assert len(dados["readers"]) == 6
    assert len(dados["loans"]) == 4


def test_dados_corrompidos_no_localstorage_voltam_ao_seed(app):
    app.page.evaluate("k => localStorage.setItem(k, '{json quebrado')", CHAVE)
    app.page.reload()
    expect(app.cards_livros).to_have_count(6)


def test_estado_sobrevive_a_reload(app):
    app.emprestar_livro("Capitães da Areia", "333.444.555-66")
    app.page.reload()
    expect(app.card_livro("Capitães da Areia")).to_contain_text("Disponível: 2 de 3")


def test_restaurar_dados_iniciais_aceitando_confirmacao(app):
    # altera o estado: cadastra um livro
    app.novo_livro()
    app.preencher_livro()
    app.cadastrar_livro()
    expect(app.cards_livros).to_have_count(7)

    app.ir_para_hash("config")
    expect(app.page.get_by_role("heading", name="Dados")).to_be_visible()
    mensagens = []
    app.page.once("dialog", lambda d: (mensagens.append(d.message), d.accept()))
    app.page.get_by_role("button", name="Restaurar dados iniciais").click()
    expect(app.toast).to_have_text("Dados iniciais restaurados.")
    assert mensagens == ["Restaurar os dados iniciais?"]

    app.ir_para_hash("livros")
    expect(app.cards_livros).to_have_count(6)


def test_restaurar_dados_cancelando_confirmacao_mantem_estado(app):
    app.novo_livro()
    app.preencher_livro()
    app.cadastrar_livro()

    app.ir_para_hash("config")
    app.page.once("dialog", lambda d: d.dismiss())
    app.page.get_by_role("button", name="Restaurar dados iniciais").click()
    expect(app.toast).to_have_count(0)

    app.ir_para_hash("livros")
    expect(app.cards_livros).to_have_count(7)


def test_restaurar_desfaz_emprestimos_e_devolucoes(app):
    app.menu("Empréstimo")
    app.abrir_emprestimo("Vidas Secas")
    app.page.get_by_role("button", name="Marcar como devolvido").click()

    app.ir_para_hash("config")
    app.page.once("dialog", lambda d: d.accept())
    app.page.get_by_role("button", name="Restaurar dados iniciais").click()

    app.ir_para_hash("livros")
    expect(app.card_livro("Vidas Secas")).to_contain_text("Indisponível: 0 de 1")
