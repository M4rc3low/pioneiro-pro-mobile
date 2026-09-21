import flet as ft

from pioneiro_pro.repositories import (
    AtividadeRepository,
    ConfiguracaoRepository,
    EstudanteRepository,
    VisitaRepository,
)
from pioneiro_pro.utils import formatar_minutos


def _metric_card(titulo: str, valor: str, icone: ft.IconData) -> ft.Container:
    return ft.Container(
        expand=True,
        padding=16,
        border_radius=16,
        bgcolor=ft.Colors.SURFACE,
        content=ft.Column(
            spacing=6,
            controls=[
                ft.Icon(icone, color=ft.Colors.BLUE_700),
                ft.Text(titulo, size=12, color=ft.Colors.GREY_600),
                ft.Text(valor, size=22, weight=ft.FontWeight.BOLD),
            ],
        ),
    )


def dashboard_view(
    atividades: AtividadeRepository,
    estudantes: EstudanteRepository,
    visitas: VisitaRepository,
    configuracoes: ConfiguracaoRepository,
    on_navigate,
) -> ft.Control:
    config = configuracoes.todas()
    nome = config["nome_pioneiro"].strip()
    total = atividades.total_minutos_mes()
    registros = atividades.quantidade_mes()
    alunos = estudantes.quantidade_ativos()
    pendentes = visitas.quantidade_pendentes()

    try:
        meta_minutos = max(0, int(float(config["meta_horas_mes"]))) * 60
    except ValueError:
        meta_minutos = 0

    progresso = min(1.0, total / meta_minutos) if meta_minutos else 0.0
    recentes = atividades.listar_recentes(5)

    lista_recentes = (
        [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.SCHEDULE),
                title=ft.Text(item["tipo"].replace("_", " ").title()),
                subtitle=ft.Text(item["data"]),
                trailing=ft.Text(
                    formatar_minutos(item["minutos"]),
                    weight=ft.FontWeight.BOLD,
                ),
            )
            for item in recentes
        ]
        if recentes
        else [
            ft.Container(
                padding=16,
                content=ft.Text(
                    "Nenhuma atividade registrada ainda.",
                    color=ft.Colors.GREY_600,
                ),
            )
        ]
    )

    saudacao = f"Olá, {nome} 👋" if nome else "Olá 👋"

    return ft.ListView(
        expand=True,
        padding=16,
        spacing=16,
        controls=[
            ft.Text(saudacao, size=16, color=ft.Colors.GREY_600),
            ft.Text("Seu mês em resumo", size=26, weight=ft.FontWeight.BOLD),
            ft.Container(
                padding=18,
                border_radius=18,
                bgcolor=ft.Colors.SURFACE,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Meta mensal", weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    (
                                        f"{formatar_minutos(total)} / "
                                        f"{formatar_minutos(meta_minutos)}"
                                        if meta_minutos
                                        else formatar_minutos(total)
                                    ),
                                    color=ft.Colors.BLUE_700,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                        ),
                        ft.ProgressBar(value=progresso),
                    ],
                ),
            ),
            ft.Row(
                spacing=10,
                controls=[
                    _metric_card("Horas", formatar_minutos(total), ft.Icons.TIMER_OUTLINED),
                    _metric_card("Registros", str(registros), ft.Icons.CHECKLIST),
                ],
            ),
            ft.Row(
                spacing=10,
                controls=[
                    _metric_card("Estudantes", str(alunos), ft.Icons.GROUP_OUTLINED),
                    _metric_card("Na agenda", str(pendentes), ft.Icons.EVENT_OUTLINED),
                ],
            ),
            ft.Row(
                controls=[
                    ft.Container(
                        expand=True,
                        content=ft.FilledButton(
                            "Registrar",
                            icon=ft.Icons.ADD,
                            on_click=lambda _: on_navigate("registrar"),
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.OutlinedButton(
                            "Agenda",
                            icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
                            on_click=lambda _: on_navigate("agenda"),
                        ),
                    ),
                ]
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Atividades recentes", size=18, weight=ft.FontWeight.BOLD),
                    ft.TextButton(
                        "Ver histórico",
                        on_click=lambda _: on_navigate("relatorios"),
                    ),
                ],
            ),
            *lista_recentes,
        ],
    )
