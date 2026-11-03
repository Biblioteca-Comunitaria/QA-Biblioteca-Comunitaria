from playwright.sync_api import expect
import pytest

from pages.biblioteca_page import CPF


@pytest.mark.smoke
def test_emprestimo_com_sucesso(app):
    app.abrir_livro("Capitães da Areia")
    app.emprestar(CPF["Joao"])
    prazo = app.data_fmt(14)
    expect(app.toast).to_have_text(f"Empréstimo feito para João Pedro Lima. Devolução até {prazo}.")
    expect(app.painel_info).to_contain_text("Exemplares disponíveis – 2")
    expect(app.page.locator("p", has_text="João Pedro Lima")).to_contain_text("devolver até")
    expect(app.page.locator("#cpf")).to_have_value("")   # campo limpo após sucesso


def test_emprestimo_aceita_cpf_sem_pontuacao(app):
    app.abrir_livro("Capitães da Areia")
    app.emprestar("33344455566")
    expect(app.toast).to_contain_text("Empréstimo feito para João Pedro Lima")


def test_dica_mostra_nome_do_leitor_ao_digitar_cpf(app):
    app.abrir_livro("Capitães da Areia")
    app.page.locator("#cpf").fill(CPF["Maria"])
    expect(app.page.get_by_text("Leitor: Maria Clara Souza")).to_be_visible()


def test_dica_cpf_nao_cadastrado(app):
    app.abrir_livro("Capitães da Areia")
    app.page.locator("#cpf").fill("999.999.999-99")
    expect(app.page.get_by_text("CPF não cadastrado")).to_be_visible()


@pytest.mark.parametrize("cpf", ["999.999.999-99", ""], ids=["cpf_inexistente", "cpf_vazio"])
def test_emprestimo_leitor_nao_encontrado(app, cpf):
    app.abrir_livro("Capitães da Areia")
    app.emprestar(cpf)
    expect(app.toast).to_have_text("Leitor não encontrado para este CPF.")
    expect(app.painel_info).to_contain_text("Exemplares disponíveis – 3")


def test_emprestimo_cria_registro_na_lista_de_emprestimos(app):
    app.emprestar_livro("A Hora da Estrela", CPF["Maria"])
    app.menu("Empréstimo")
    expect(app.cards_emprestimos).to_have_count(5)
    card = app.card_emprestimo("A Hora da Estrela")
    expect(card).to_contain_text("Maria Clara Souza")
    expect(card).to_contain_text(app.data_fmt(0))
    expect(card).to_contain_text(app.data_fmt(14))
    expect(card).to_contain_text("Status: Ativo")


def test_leitor_com_dois_emprestimos_ativos_nao_pode_pegar_terceiro(app):
    # Abigail já tem 2 empréstimos ativos no seed
    app.abrir_livro("Capitães da Areia")
    app.emprestar(CPF["Abigail"])
    expect(app.toast).to_have_text("Abigail Maria já tem 2 empréstimos ativos.")
    expect(app.painel_info).to_contain_text("Exemplares disponíveis – 3")


def test_limite_de_dois_emprestimos_ao_emprestar_em_sequencia(app):
    app.emprestar_livro("Capitães da Areia", CPF["Joao"])
    app.emprestar_livro("A Hora da Estrela", CPF["Joao"])
    app.abrir_livro("Dom Casmurro")
    app.emprestar(CPF["Joao"])
    expect(app.toast).to_have_text("João Pedro Lima já tem 2 empréstimos ativos.")
    expect(app.painel_info).to_contain_text("Exemplares disponíveis – 1")


def test_leitor_com_um_emprestimo_ainda_pode_pegar_outro(app):
    app.abrir_livro("Capitães da Areia")
    app.emprestar(CPF["Renally"])        # tinha 1 ativo -> passa a 2
    expect(app.toast).to_contain_text("Empréstimo feito para Renally Veríssimo")


def test_livro_sem_exemplares_bloqueia_emprestimo(app):
    app.abrir_livro("Vidas Secas")       # 1 exemplar, já emprestado
    expect(app.btn_salvar).to_be_disabled()
    expect(app.page.get_by_text("Sem exemplares disponíveis.")).to_be_visible()
    expect(app.painel_info).to_contain_text("Exemplares disponíveis – 0")
    expect(app.painel_info).to_contain_text("Status – Indisponível")


def test_livro_marcado_indisponivel_bloqueia_emprestimo(app):
    app.abrir_livro("O Quinze")          # status Indisponível, mesmo com exemplar livre
    expect(app.btn_salvar).to_be_disabled()
    expect(app.painel_info).to_contain_text("Exemplares disponíveis – 0")


def test_emprestar_ultimo_exemplar_bloqueia_novos_emprestimos(app):
    app.abrir_livro("Dom Casmurro")      # 1 de 2 disponível
    app.emprestar(CPF["Maria"])
    expect(app.toast).to_contain_text("Empréstimo feito para Maria Clara Souza")
    expect(app.painel_info).to_contain_text("Exemplares disponíveis – 0")
    expect(app.btn_salvar).to_be_disabled()
    expect(app.page.get_by_text("Sem exemplares disponíveis.")).to_be_visible()
    app.voltar()
    expect(app.card_livro("Dom Casmurro")).to_contain_text("Indisponível: 0 de 2")
    app.aba("Indisponíveis")
    expect(app.card_livro("Dom Casmurro")).to_be_visible()


def test_emprestimo_persiste_apos_reload(app):
    app.emprestar_livro("Capitães da Areia", CPF["Joao"])
    app.page.reload()
    expect(app.card_livro("Capitães da Areia")).to_contain_text("Disponível: 2 de 3")
