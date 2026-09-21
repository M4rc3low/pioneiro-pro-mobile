from pioneiro_pro.database import Database
from pioneiro_pro.repositories import (
    AtividadeRepository,
    ConfiguracaoRepository,
    EstudanteRepository,
    VisitaRepository,
)


def criar_db(tmp_path):
    db = Database(tmp_path / "teste.db")
    db.initialize()
    return db


def test_criar_editar_e_excluir_atividade(tmp_path):
    db = criar_db(tmp_path)
    repo = AtividadeRepository(db)

    atividade_id = repo.criar("2026-09-21", "ministerio", 90, "Teste")
    repo.atualizar(atividade_id, "2026-09-22", "revisita", 75, "Atualizado")

    item = repo.obter(atividade_id)
    assert item is not None
    assert item["data"] == "2026-09-22"
    assert item["tipo"] == "revisita"
    assert item["minutos"] == 75
    assert item["observacao"] == "Atualizado"

    repo.excluir(atividade_id)
    assert repo.obter(atividade_id) is None


def test_totais_por_mes_e_ano(tmp_path):
    db = criar_db(tmp_path)
    repo = AtividadeRepository(db)

    repo.criar("2026-01-10", "ministerio", 60)
    repo.criar("2026-01-11", "ministerio", 30)
    repo.criar("2026-02-10", "ministerio", 120)

    assert repo.total_minutos_mes(2026, 1) == 90
    assert repo.total_minutos_ano(2026) == 210

    totais = repo.totais_por_mes(2026)
    assert totais[0]["minutos"] == 90
    assert totais[1]["minutos"] == 120


def test_criar_atualizar_e_listar_estudante(tmp_path):
    db = criar_db(tmp_path)
    repo = EstudanteRepository(db)

    estudante_id = repo.criar("João", "11999999999")
    repo.atualizar(
        estudante_id,
        {
            "endereco": "Rua Teste",
            "modalidade": "presencial",
            "publicacao_atual": "Seja Feliz Para Sempre!",
            "licao_atual": "Lição 3",
        },
    )

    item = repo.obter(estudante_id)
    assert item is not None
    assert item["nome"] == "João"
    assert item["endereco"] == "Rua Teste"
    assert item["modalidade"] == "presencial"
    assert item["licao_atual"] == "Lição 3"


def test_agenda_criar_concluir_editar_e_excluir(tmp_path):
    db = criar_db(tmp_path)
    estudantes = EstudanteRepository(db)
    visitas = VisitaRepository(db)

    estudante_id = estudantes.criar("Maria")
    visita_id = visitas.criar(
        estudante_id=estudante_id,
        data="2099-09-21",
        horario="19:30",
        tipo="estudo",
        observacao="Lição 5",
    )

    itens = visitas.listar()
    assert len(itens) == 1
    assert itens[0]["estudante_nome"] == "Maria"

    visitas.atualizar(
        visita_id,
        "2099-09-22",
        "20:00",
        "revisita",
        estudante_id,
        "Nova visita",
    )
    visitas.marcar_concluida(visita_id, True)

    item = visitas.listar()[0]
    assert item["tipo"] == "revisita"
    assert item["concluida"] == 1

    visitas.excluir(visita_id)
    assert visitas.listar() == []


def test_configuracoes_persistentes(tmp_path):
    db = criar_db(tmp_path)
    repo = ConfiguracaoRepository(db)

    assert repo.obter("meta_horas_mes") == "50"

    repo.definir("meta_horas_mes", 45)
    repo.definir("tema", "escuro")

    assert repo.obter("meta_horas_mes") == "45"
    assert repo.todas()["tema"] == "escuro"
