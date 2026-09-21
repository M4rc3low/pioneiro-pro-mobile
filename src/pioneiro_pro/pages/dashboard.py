import flet as ft

from pioneiro_pro.repositories import AtividadeRepository, EstudanteRepository
from pioneiro_pro.utils import formatar_minutos


def _metric_card(titulo: str, valor: str, icone: ft.IconData) -> ft.Container:
    return ft.Container(
        expand=True,
        padding=16,
        border_radius=16,
        bgcolor=ft.Colors.WHITE,
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
    on_navigate,
) -> ft.Control:
    total = atividades.total_minutos_mes()
    registros = atividades.quantidade_mes()
    alunos = estudantes.quantidade_ativos()
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

    return ft.ListView(
        expand=True,
        padding=16,
        spacing=16,
        controls=[
            ft.Text("Olá 👋", size=16, color=ft.Colors.GREY_600),
            ft.Text("Seu mês em resumo", size=26, weight=ft.FontWeight.BOLD),
            ft.Row(
                spacing=10,
                controls=[
                    _metric_card("Horas", formatar_minutos(total), ft.Icons.TIMER_OUTLINED),
                    _metric_card("Registros", str(registros), ft.Icons.CHECKLIST),
                ],
            ),
            ft.Row(
                controls=[
                    _metric_card("Estudantes ativos", str(alunos), ft.Icons.GROUP_OUTLINED),
                ]
            ),
            ft.FilledButton(
                "Registrar atividade",
                icon=ft.Icons.ADD,
                on_click=lambda _: on_navigate("registrar"),
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Atividades recentes", size=18, weight=ft.FontWeight.BOLD),
                    ft.TextButton(
                        "Relatórios",
                        on_click=lambda _: on_navigate("relatorios"),
                    ),
                ],
            ),
            *lista_recentes,
        ],
    )
