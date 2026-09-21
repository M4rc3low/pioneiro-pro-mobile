from datetime import datetime

from pioneiro_pro.database import Database
from pioneiro_pro.repositories import AtividadeRepository, EstudanteRepository, VisitaRepository
from pioneiro_pro.services import AndroidNotificationService, ExportacaoService, ProximidadeService


def criar_db(tmp_path):
    db = Database(tmp_path / "teste.db")
    db.initialize()
    return db


def test_publicacoes_podem_ser_salvas_e_corrigidas(tmp_path):
    db = criar_db(tmp_path)
    repo = AtividadeRepository(db)

    atividade_id = repo.criar(
        "2026-09-21",
        "ministerio",
        60,
        brochuras=2,
        folhetos=3,
        outras_publicacoes=1,
    )

    item = repo.obter(atividade_id)
    assert item["brochuras"] == 2
    assert item["folhetos"] == 3
    assert item["outras_publicacoes"] == 1

    repo.atualizar(
        atividade_id,
        "2026-09-21",
        "ministerio",
        90,
        "Corrigido",
        4,
        5,
        2,
    )

    item = repo.obter(atividade_id)
    assert item["minutos"] == 90
    assert item["brochuras"] == 4
    assert item["folhetos"] == 5
    assert item["outras_publicacoes"] == 2


def test_totais_de_publicacoes_no_mes(tmp_path):
    db = criar_db(tmp_path)
    repo = AtividadeRepository(db)

    repo.criar("2026-09-01", "ministerio", 60, brochuras=2, folhetos=1)
    repo.criar("2026-09-02", "revisita", 30, brochuras=1, folhetos=4, outras_publicacoes=2)
    repo.criar("2026-10-01", "ministerio", 45, brochuras=10)

    totais = repo.publicacoes_mes(2026, 9)
    assert totais == {
        "brochuras": 3,
        "folhetos": 5,
        "outras_publicacoes": 2,
    }


def test_relatorio_mensal_inclui_publicacoes(tmp_path):
    db = criar_db(tmp_path)
    repo = AtividadeRepository(db)
    repo.criar("2026-09-10", "ministerio", 120, brochuras=2, folhetos=3)

    texto = ExportacaoService(repo).relatorio_mensal_texto(2026, 9)

    assert "Tempo: 2h" in texto
    assert "Brochuras: 2" in texto
    assert "Folhetos: 3" in texto


def test_localizacao_do_estudante_e_proximidade(tmp_path):
    db = criar_db(tmp_path)
    estudantes = EstudanteRepository(db)
    visitas = VisitaRepository(db)

    estudante_id = estudantes.criar("Maria")
    estudantes.atualizar_localizacao(
        estudante_id,
        latitude=-23.588000,
        longitude=-46.681000,
        raio_alerta_m=250,
    )

    service = ProximidadeService(estudantes, visitas)
    alertas = service.verificar(
        latitude=-23.588100,
        longitude=-46.681100,
        agora=datetime(2026, 9, 21, 13, 0),
    )

    assert len(alertas) == 1
    assert alertas[0]["nome"] == "Maria"
    assert alertas[0]["distancia_m"] < 250
    assert alertas[0]["latitude"] == -23.588
    assert alertas[0]["longitude"] == -46.681

    url = service.url_google_maps(
        alertas[0]["latitude"],
        alertas[0]["longitude"],
    )
    assert url.startswith("https://www.google.com/maps/dir/?api=1")
    assert "destination=-23.5880000%2C-46.6810000" in url
    assert "travelmode=driving" in url
    assert "dir_action=navigate" in url


def test_proximidade_nao_repete_imediatamente(tmp_path):
    db = criar_db(tmp_path)
    estudantes = EstudanteRepository(db)
    visitas = VisitaRepository(db)

    estudante_id = estudantes.criar("João")
    estudantes.atualizar_localizacao(estudante_id, -23.588, -46.681, 300)

    service = ProximidadeService(estudantes, visitas)
    primeiro = service.verificar(
        -23.5881,
        -46.6811,
        datetime(2026, 9, 21, 13, 0),
    )
    segundo = service.verificar(
        -23.5881,
        -46.6811,
        datetime(2026, 9, 21, 13, 10),
    )

    assert len(primeiro) == 1
    assert segundo == []


def test_revisita_pode_ter_localizacao_propria(tmp_path):
    db = criar_db(tmp_path)
    estudantes = EstudanteRepository(db)
    visitas = VisitaRepository(db)

    visitas.criar(
        data="2026-09-22",
        horario="18:00",
        tipo="revisita",
        observacao="Retorno",
        latitude=-23.588,
        longitude=-46.681,
        raio_alerta_m=200,
    )

    service = ProximidadeService(estudantes, visitas)
    alertas = service.verificar(
        -23.58805,
        -46.68105,
        datetime(2026, 9, 21, 13, 0),
    )

    assert len(alertas) == 1
    assert alertas[0]["tipo"] == "revisita"
    assert alertas[0]["latitude"] == -23.588
    assert alertas[0]["longitude"] == -46.681


def test_alerta_pode_ser_liberado_para_nova_tentativa(tmp_path):
    db = criar_db(tmp_path)
    estudantes = EstudanteRepository(db)
    visitas = VisitaRepository(db)

    estudante_id = estudantes.criar("Paulo")
    estudantes.atualizar_localizacao(estudante_id, -23.588, -46.681, 300)

    service = ProximidadeService(estudantes, visitas)
    agora = datetime(2026, 9, 21, 13, 0)

    primeiro = service.verificar(-23.5881, -46.6811, agora)
    assert len(primeiro) == 1

    service.liberar_alerta(primeiro[0]["chave"])
    segundo = service.verificar(-23.5881, -46.6811, agora)

    assert len(segundo) == 1


def test_ids_de_notificacao_sao_estaveis_por_tipo():
    estudante = AndroidNotificationService.notification_id(
        {"tipo": "estudante", "estudante_id": 42}
    )
    revisita = AndroidNotificationService.notification_id(
        {"tipo": "revisita", "visita_id": 42}
    )

    assert estudante == 10042
    assert revisita == 20042
    assert estudante != revisita


def test_regioes_geofence_refletem_estudantes_e_revisitas(tmp_path):
    db = criar_db(tmp_path)
    estudantes = EstudanteRepository(db)
    visitas = VisitaRepository(db)

    maria_id = estudantes.criar("Maria")
    estudantes.atualizar_localizacao(maria_id, -23.588, -46.681, 80)

    joao_id = estudantes.criar("João")
    estudantes.atualizar_localizacao(joao_id, -23.590, -46.680, 300)
    visitas.criar(
        data="2099-09-22",
        horario="18:00",
        tipo="revisita",
        estudante_id=joao_id,
        latitude=-23.591,
        longitude=-46.679,
        raio_alerta_m=250,
    )

    regioes = ProximidadeService(estudantes, visitas).regioes_geofence()
    por_id = {item["id"]: item for item in regioes}

    assert f"estudante:{maria_id}" in por_id
    assert por_id[f"estudante:{maria_id}"]["raio_m"] == 100

    revisitas = [item for item in regioes if item["tipo"] == "revisita"]
    assert len(revisitas) == 1
    assert revisitas[0]["nome"] == "João"
    assert revisitas[0]["raio_m"] == 250

    # Quando há revisita com localização própria, evitamos uma segunda
    # geofence redundante para o mesmo estudante.
    assert f"estudante:{joao_id}" not in por_id
