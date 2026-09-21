from pioneiro_pro.database import Database
from pioneiro_pro.repositories import AtividadeRepository, EstudanteRepository


def test_criar_e_listar_atividade(tmp_path):
    db = Database(tmp_path / "teste.db")
    db.initialize()
    repo = AtividadeRepository(db)

    repo.criar("2026-09-21", "ministerio", 90, "Teste")

    itens = repo.listar_recentes()
    assert len(itens) == 1
    assert itens[0]["minutos"] == 90


def test_criar_e_listar_estudante(tmp_path):
    db = Database(tmp_path / "teste.db")
    db.initialize()
    repo = EstudanteRepository(db)

    repo.criar("João", "11999999999")

    itens = repo.listar()
    assert len(itens) == 1
    assert itens[0]["nome"] == "João"
