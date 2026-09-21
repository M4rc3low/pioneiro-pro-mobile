import flet as ft

from pioneiro_pro.database import Database
from pioneiro_pro.pages import (
    agenda_view,
    configuracoes_view,
    dashboard_view,
    estudante_detalhes_view,
    estudantes_view,
    onboarding_view,
    registrar_view,
    relatorios_view,
)
from pioneiro_pro.repositories import (
    AtividadeRepository,
    ConfiguracaoRepository,
    EstudanteRepository,
    VisitaRepository,
)
from pioneiro_pro.services import BackupService, CronometroService, ExportacaoService


class DummyPage:
    web = False
    theme_mode = ft.ThemeMode.LIGHT

    def update(self):
        return None

    def run_task(self, *_args, **_kwargs):
        return None


class DummyGeolocator:
    async def request_permission(self):
        return None

    async def get_current_position(self):
        return None


def criar_contexto(tmp_path):
    db = Database(tmp_path / "ui.db")
    db.initialize()
    atividades = AtividadeRepository(db)
    estudantes = EstudanteRepository(db)
    visitas = VisitaRepository(db)
    configuracoes = ConfiguracaoRepository(db)
    return db, atividades, estudantes, visitas, configuracoes


def test_construcao_das_telas_principais(tmp_path):
    db, atividades, estudantes, visitas, configuracoes = criar_contexto(tmp_path)
    estudante_id = estudantes.criar("Teste", "11999999999")

    page = DummyPage()
    geolocator = DummyGeolocator()
    cronometro = CronometroService()
    exportacao = ExportacaoService(atividades)
    backup = BackupService(db)

    views = [
        dashboard_view(
            atividades,
            estudantes,
            visitas,
            configuracoes,
            lambda *_args, **_kwargs: None,
        ),
        registrar_view(
            page,
            atividades,
            cronometro,
            lambda: True,
            lambda: None,
        ),
        estudantes_view(
            estudantes,
            lambda *_args, **_kwargs: None,
        ),
        estudante_detalhes_view(
            estudante_id,
            estudantes,
            visitas,
            geolocator,
            lambda: None,
            lambda: None,
        ),
        agenda_view(
            visitas,
            estudantes,
            geolocator,
        ),
        relatorios_view(
            atividades,
            configuracoes,
            exportacao,
        ),
        configuracoes_view(
            page,
            configuracoes,
            backup,
            exportacao,
            lambda: None,
        ),
        onboarding_view(
            configuracoes,
            lambda: None,
        ),
    ]

    assert len(views) == 8
    assert all(view is not None for view in views)


def test_dashboard_com_dados_reais_constroi_sem_erro(tmp_path):
    _, atividades, estudantes, visitas, configuracoes = criar_contexto(tmp_path)
    atividades.criar(
        "2026-09-21",
        "ministerio",
        95,
        "Teste visual",
        brochuras=2,
        folhetos=3,
    )
    estudante_id = estudantes.criar("Maria", "11999999999")
    visitas.criar(
        data="2099-09-22",
        horario="18:30",
        tipo="estudo",
        estudante_id=estudante_id,
    )

    view = dashboard_view(
        atividades,
        estudantes,
        visitas,
        configuracoes,
        lambda *_args, **_kwargs: None,
    )

    assert view is not None
