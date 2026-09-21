import json

from pioneiro_pro.database import Database
from pioneiro_pro.repositories import (
    AtividadeRepository,
    EstudanteRepository,
    VisitaRepository,
)
from pioneiro_pro.services import BackupService, ExportacaoService, LembreteService


def criar_db(tmp_path):
    db = Database(tmp_path / "teste.db")
    db.initialize()
    return db


def test_backup_e_restauracao(tmp_path):
    db = criar_db(tmp_path)
    atividades = AtividadeRepository(db)
    estudantes = EstudanteRepository(db)
    visitas = VisitaRepository(db)
    backup = BackupService(db)

    estudante_id = estudantes.criar("Ana", "11999999999")
    atividades.criar("2026-09-21", "ministerio", 120, "Teste")
    visitas.criar("2026-09-21", "19:00", "estudo", estudante_id, "Lição 2")

    conteudo = backup.exportar_bytes()
    payload = json.loads(conteudo.decode("utf-8"))
    assert payload["formato"] == "pioneiro-pro-backup"

    atividades.excluir(atividades.listar()[0]["id"])
    estudantes.excluir(estudante_id)

    backup.restaurar_bytes(conteudo)

    assert len(atividades.listar()) == 1
    assert len(estudantes.listar()) == 1
    assert len(visitas.listar()) == 1


def test_exportacao_csv(tmp_path):
    db = criar_db(tmp_path)
    atividades = AtividadeRepository(db)
    atividades.criar("2026-09-21", "revisita", 75, "Casa azul")

    csv_bytes = ExportacaoService(atividades).relatorio_csv()
    texto = csv_bytes.decode("utf-8-sig")

    assert "Revisita" in texto
    assert "Casa azul" in texto
    assert "75" in texto


def test_busca_estudantes_e_atividades(tmp_path):
    db = criar_db(tmp_path)
    estudantes = EstudanteRepository(db)
    atividades = AtividadeRepository(db)

    estudantes.criar("Carlos", observacao="trabalha à noite")
    estudantes.criar("Maria")
    atividades.criar("2026-09-21", "ministerio", 60, "Parque")
    atividades.criar("2026-09-22", "revisita", 30, "Prédio")

    assert len(estudantes.buscar("noite")) == 1
    assert estudantes.buscar("noite")[0]["nome"] == "Carlos"
    assert len(atividades.buscar("Parque")) == 1
    assert len(atividades.buscar(tipo="revisita")) == 1


def test_lembrete_do_dia(tmp_path, monkeypatch):
    db = criar_db(tmp_path)
    visitas = VisitaRepository(db)
    estudantes = EstudanteRepository(db)

    estudante_id = estudantes.criar("Paulo")
    visitas.criar("2026-09-21", "18:30", "estudo", estudante_id)

    class DataFixa:
        @classmethod
        def today(cls):
            from datetime import date

            return date(2026, 9, 21)

    monkeypatch.setattr("pioneiro_pro.services.lembrete_service.date", DataFixa)

    service = LembreteService(visitas)
    assert len(service.compromissos_hoje()) == 1
    assert "Paulo" in (service.mensagem_hoje() or "")
