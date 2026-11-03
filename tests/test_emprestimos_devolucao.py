from playwright.sync_api import expect
import pytest

from pages.biblioteca_page import CPF


@pytest.fixture
def emp(app):
    app.menu("Empréstimo")
    expect(app.titulo).to_have_text("Empréstimo")
    return app


# ---------- listagem ----------
@pytest.mark.smoke
def test_lista_inicial_ordenada_do_mais_recente_para_o_mais_antigo(emp):
    assert emp.titulos_cards(emp.cards_emprestimos) == [
        "Vidas Secas", "Dom Casmurro", "Casa-Grande & Senzala", "Capitães da Areia"]


@pytest.mark.parametrize("aba,esperados", [
    ("Todos", 4),
    ("Ativos", 1),
    ("Atrasados", 2),
    ("Devolvidos", 1),
])
def test_abas_de_status(emp, aba, esperados):
    emp.aba(aba)
    expect(emp.cards_emprestimos).to_have_count(esperados)


def test_aba_atrasados_lista_os_corretos(emp):
    emp.aba("Atrasados")
    assert set(emp.titulos_cards(emp.cards_emprestimos)) == {"Casa-Grande & Senzala", "Dom Casmurro"}
    for card in emp.cards_emprestimos.all():
        expect(card).to_contain_text("◆ Atrasado")


def test_card_devolvido_mostra_data_de_devolucao(emp):
    card = emp.card_emprestimo("Capitães da Areia")
    expect(card).to_contain_text("Devolvido em:")
    expect(card).to_contain_text("Status: Devolvido")
    expect(card).to_contain_text(emp.data_fmt(-50))


def test_card_ativo_mostra_devolucao_prevista(emp):
    card = emp.card_emprestimo("Vidas Secas")
    expect(card).to_contain_text("Devolução prevista:")
    expect(card).to_contain_text(emp.data_fmt(11))
    expect(card).to_contain_text("Abigail Maria")
    expect(card).to_contain_text("Status: Ativo")


@pytest.mark.parametrize("busca,esperados", [
    ("abigail", {"Vidas Secas", "Dom Casmurro"}),        # por leitor
    ("RENALLY", {"Casa-Grande & Senzala"}),
    ("veríssimo", {"Casa-Grande & Senzala"}),
    ("verissimo", {"Casa-Grande & Senzala"}),            # sem acento
    ("vidas", {"Vidas Secas"}),                          # por livro
    ("graciliano", {"Vidas Secas"}),                     # por autor
])
def test_busca_por_livro_ou_leitor(emp, busca, esperados):
    emp.buscar(busca)
    assert set(emp.titulos_cards(emp.cards_emprestimos)) == esperados


def test_busca_sem_resultado(emp):
    emp.buscar("zzz")
    expect(emp.page.get_by_text("Nenhum empréstimo nesta lista.")).to_be_visible()


def test_aba_sem_resultado_com_busca(emp):
    emp.aba("Devolvidos")
    emp.buscar("abigail")
    expect(emp.page.get_by_text("Nenhum empréstimo nesta lista.")).to_be_visible()


# ---------- detalhe ----------
def test_detalhe_do_emprestimo_atrasado(emp):
    emp.abrir_emprestimo("Casa-Grande & Senzala")
    pagina = emp.page
    expect(pagina.get_by_text("Renally Veríssimo")).to_be_visible()
    expect(pagina.get_by_text("111.222.333-44")).to_be_visible()
    expect(pagina.get_by_text("(81) 90000-0001")).to_be_visible()
    expect(pagina.get_by_text("◆ Atrasado")).to_be_visible()
    expect(pagina.get_by_role("button", name="Marcar como devolvido")).to_be_visible()


def test_detalhe_de_emprestimo_devolvido_nao_tem_botao_de_devolucao(emp):
    emp.abrir_emprestimo("Capitães da Areia")
    expect(emp.page.get_by_text("Devolvido em:")).to_be_visible()
    expect(emp.page.get_by_role("button", name="Marcar como devolvido")).to_have_count(0)


def test_voltar_do_detalhe_retorna_a_lista(emp):
    emp.abrir_emprestimo("Vidas Secas")
    emp.voltar()
    expect(emp.cards_emprestimos).to_have_count(4)


# ---------- devolução ----------
@pytest.mark.smoke
def test_devolucao_atualiza_status_e_exibe_mensagem(emp):
    emp.abrir_emprestimo("Vidas Secas")
    emp.page.get_by_role("button", name="Marcar como devolvido").click()
    expect(emp.toast).to_have_text(f"Devolução registrada em {emp.data_fmt(0)}.")
    expect(emp.cards_emprestimos).to_have_count(4)      # voltou para a lista
    card = emp.card_emprestimo("Vidas Secas")
    expect(card).to_contain_text("Status: Devolvido")
    expect(card).to_contain_text("Devolvido em:")
    expect(card).to_contain_text(emp.data_fmt(0))


def test_devolucao_move_emprestimo_entre_abas(emp):
    emp.abrir_emprestimo("Vidas Secas")
    emp.page.get_by_role("button", name="Marcar como devolvido").click()
    emp.aba("Ativos")
    expect(emp.cards_emprestimos).to_have_count(0)
    emp.aba("Devolvidos")
    expect(emp.cards_emprestimos).to_have_count(2)


def test_devolucao_de_emprestimo_atrasado(emp):
    emp.abrir_emprestimo("Dom Casmurro")
    emp.page.get_by_role("button", name="Marcar como devolvido").click()
    emp.aba("Atrasados")
    assert emp.titulos_cards(emp.cards_emprestimos) == ["Casa-Grande & Senzala"]


def test_devolucao_libera_exemplar_no_livro(emp):
    emp.abrir_emprestimo("Vidas Secas")
    emp.page.get_by_role("button", name="Marcar como devolvido").click()
    emp.menu("Livros")
    expect(emp.card_livro("Vidas Secas")).to_contain_text("Disponível: 1 de 1")
    emp.aba("Disponíveis")
    expect(emp.card_livro("Vidas Secas")).to_be_visible()


def test_devolucao_libera_leitor_do_limite_de_dois_emprestimos(app):
    # Abigail está no limite: não consegue emprestar
    app.abrir_livro("Capitães da Areia")
    app.emprestar(CPF["Abigail"])
    expect(app.toast).to_contain_text("já tem 2 empréstimos ativos")
    app.voltar()
    # devolve um dos empréstimos dela
    app.menu("Empréstimo")
    app.abrir_emprestimo("Vidas Secas")
    app.page.get_by_role("button", name="Marcar como devolvido").click()
    # agora consegue
    app.menu("Livros")
    app.abrir_livro("Capitães da Areia")
    app.emprestar(CPF["Abigail"])
    expect(app.toast).to_contain_text("Empréstimo feito para Abigail Maria")


def test_devolucao_persiste_apos_reload(emp):
    emp.abrir_emprestimo("Vidas Secas")
    emp.page.get_by_role("button", name="Marcar como devolvido").click()
    emp.page.reload()
    emp.aba("Devolvidos")
    expect(emp.card_emprestimo("Vidas Secas")).to_be_visible()


def test_ciclo_completo_emprestar_e_devolver(app):
    app.emprestar_livro("A Hora da Estrela", CPF["Maria"])
    expect(app.card_livro("A Hora da Estrela")).to_contain_text("Disponível: 1 de 2")
    app.menu("Empréstimo")
    app.abrir_emprestimo("A Hora da Estrela")
    app.page.get_by_role("button", name="Marcar como devolvido").click()
    app.menu("Livros")
    expect(app.card_livro("A Hora da Estrela")).to_contain_text("Disponível: 2 de 2")
