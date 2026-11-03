from playwright.sync_api import expect
import pytest

TODOS = ["Casa-Grande & Senzala", "Dom Casmurro", "Vidas Secas",
         "Capitães da Areia", "A Hora da Estrela", "O Quinze"]


@pytest.mark.smoke
def test_lista_inicial_tem_seis_livros(app):
    expect(app.cards_livros).to_have_count(6)
    assert app.titulos_cards(app.cards_livros) == TODOS


@pytest.mark.parametrize("titulo,texto", [
    ("Casa-Grande & Senzala", "Disponível: 3 de 4"),   # 1 empréstimo ativo
    ("Dom Casmurro", "Disponível: 1 de 2"),
    ("Vidas Secas", "Indisponível: 0 de 1"),            # único exemplar emprestado
    ("Capitães da Areia", "Disponível: 3 de 3"),        # empréstimo já devolvido
    ("A Hora da Estrela", "Disponível: 2 de 2"),
    ("O Quinze", "Indisponível: 0 de 1"),               # status Indisponível
])
def test_disponibilidade_exibida_nos_cards(app, titulo, texto):
    expect(app.card_livro(titulo)).to_contain_text(texto)


@pytest.mark.parametrize("aba,esperados", [
    ("Todos", TODOS),
    ("Disponíveis", ["Casa-Grande & Senzala", "Dom Casmurro", "Capitães da Areia", "A Hora da Estrela"]),
    ("Indisponíveis", ["Vidas Secas", "O Quinze"]),
])
def test_abas_filtram_por_disponibilidade(app, aba, esperados):
    app.aba(aba)
    assert app.titulos_cards(app.cards_livros) == esperados


@pytest.mark.parametrize("busca,esperados", [
    ("casmurro", ["Dom Casmurro"]),
    ("MACHADO", ["Dom Casmurro"]),                 # por autor, ignorando maiúsculas
    ("capitaes", ["Capitães da Areia"]),           # ignorando acento
    ("clarice", ["A Hora da Estrela"]),
    ("rocco", []),                                 # editora não entra na busca
])
def test_busca_por_titulo_ou_autor(app, busca, esperados):
    app.buscar(busca)
    assert app.titulos_cards(app.cards_livros) == esperados


def test_busca_sem_resultado_mostra_mensagem(app):
    app.buscar("xyz inexistente")
    expect(app.page.get_by_text("Nenhum livro encontrado.")).to_be_visible()
    expect(app.cards_livros).to_have_count(0)


def test_busca_combina_com_aba(app):
    app.aba("Indisponíveis")
    app.buscar("quinze")
    assert app.titulos_cards(app.cards_livros) == ["O Quinze"]
    app.buscar("dom")   # Dom Casmurro está disponível, não aparece nesta aba
    expect(app.page.get_by_text("Nenhum livro encontrado.")).to_be_visible()


def test_limpar_busca_restaura_lista(app):
    app.buscar("dom")
    expect(app.cards_livros).to_have_count(1)
    app.buscar("")
    expect(app.cards_livros).to_have_count(6)


def test_detalhe_do_livro_mostra_informacoes(app):
    app.abrir_livro("Casa-Grande & Senzala")
    for texto in ["Total de exemplares – 4", "Exemplares disponíveis – 3", "Status – Disponível",
                  "Gênero: Sociologia", "Editora: Global", "Ano de publicação: 1933",
                  "ISBN: 978-0000-0001"]:
        expect(app.painel_info).to_contain_text(texto)
    expect(app.page.get_by_text("Gilberto Freyre")).to_be_visible()


def test_detalhe_lista_emprestimo_em_andamento_com_atraso(app):
    app.abrir_livro("Casa-Grande & Senzala")
    item = app.page.locator("p", has_text="Renally Veríssimo")
    expect(item).to_contain_text("devolver até")
    expect(item).to_contain_text("Atrasado")


def test_detalhe_sem_emprestimos_mostra_nenhum(app):
    app.abrir_livro("A Hora da Estrela")
    expect(app.page.get_by_text("Nenhum.", exact=True)).to_be_visible()


def test_voltar_do_detalhe_retorna_a_lista(app):
    app.abrir_livro("Dom Casmurro")
    app.voltar()
    expect(app.cards_livros).to_have_count(6)
