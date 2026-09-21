import flet as ft

from pioneiro_pro.repositories import AtividadeRepository
from pioneiro_pro.utils import formatar_minutos


def relatorios_view(atividades: AtividadeRepository) -> ft.Control:
    total = atividades.total_minutos_mes()
    quantidade = atividades.quantidade_mes()

    return ft.ListView(
        expand=True,
        padding=16,
        spacing=16,
        controls=[
            ft.Text("Relatórios", size=26, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Acompanhe seu progresso com dados locais.",
                color=ft.Colors.GREY_600,
            ),
            ft.Container(
                padding=20,
                border_radius=16,
                bgcolor=ft.Colors.WHITE,
                content=ft.Column(
                    controls=[
                        ft.Text("Mês atual", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            formatar_minutos(total),
                            size=34,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_700,
                        ),
                        ft.Text(f"{quantidade} atividade(s) registrada(s)"),
                    ],
                ),
            ),
            ft.Text(
                "Gráficos, metas anuais e comparativos serão acrescentados nas próximas etapas.",
                color=ft.Colors.GREY_600,
            ),
        ],
    )
