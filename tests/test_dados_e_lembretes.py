from datetime import datetime

from pioneiro_pro.database import Database
from pioneiro_pro.repositories import AtividadeRepository, EstudanteRepository, VisitaRepository
from pioneiro_pro.services import BackupService, ExportacaoService, LembreteService


def criar_db(tmp_path, nome="teste.db"):
    db = Database(tmp_path / nome)
    db.initialize()
    return db


def test_backup_e_restauracao(tmp_path):
    origem = criar_db(tmp_path, "origem.db")
    atividades = AtividadeRepository(origem)
    estudantes = EstudanteRepository(origem)
    visitas = VisitaRepository(origem)

    atividades.criar("2026-09-21", "ministerio", 90, "Teste")
    estudante_id = estudantes.criar("Ana", "11999999999")
    visitas.criar(
        "2026-09-22",
        "19:30",
        "estudo",
        estudante_id,
        "Lição 4",
        60,
    )

    backup = BackupService(origem).exportar_bytes()

    destino = criar_db(tmp_path, "destino.db")
    BackupService(destino).restaurar_bytes(backup)

    assert len(AtividadeRepository(destino).listar()) == 1
    assert len(EstudanteRepository(destino).listar()) == 1
    itens = VisitaRepository(destino).listar()
    assert len(itens) == 1
    assert itens[0]["lembrar_minutos_antes"] == 60


def test_exportacao_csv_e_resumo(tmp_path):
    db = criar_db(tmp_path)
    atividades = AtividadeRepository(db)
    atividades.criar("2026-09-21", "ministerio", 75, "Registro")

    exportacao = ExportacaoService(atividades)

    csv_bytes = exportacao.relatorio_csv()
    resumo = exportacao.resumo_txt()

    assert "Ministério".encode("utf-8") in csv_bytes
    assert b"Pioneiro Pro" in resumo


def test_lembrete_respeita_antecedencia(tmp_path):
    db = criar_db(tmp_path)
    visitas = VisitaRepository(db)
    visitas.criar(
        data="2026-09-21",
        horario="15:00",
        tipo="revisita",
        observacao="Retorno",
        lembrar_minutos_antes=30,
    )

    service = LembreteService(visitas)

    antes = service.compromissos_para_lembrar(datetime(2026, 9, 21, 14, 20))
    dentro = service.compromissos_para_lembrar(datetime(2026, 9, 21, 14, 40))

    assert antes == []
    assert len(dentro) == 1

    service.marcar_exibidos(dentro)
    assert service.compromissos_para_lembrar(datetime(2026, 9, 21, 14, 45)) == []
