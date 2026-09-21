import flet as ft


def agenda_view() -> ft.Control:
    return ft.ListView(
        expand=True,
        padding=16,
        spacing=16,
        controls=[
            ft.Text("Agenda", size=26, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Aqui ficarão estudos, revisitas, lembretes e compromissos.",
                color=ft.Colors.GREY_600,
            ),
            ft.Container(
                padding=20,
                border_radius=16,
                bgcolor=ft.Colors.WHITE,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.CALENDAR_MONTH_OUTLINED, size=48),
                        ft.Text(
                            "Agenda pronta para a próxima etapa",
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            "O banco já possui estrutura para visitas e compromissos.",
                            text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.GREY_600,
                        ),
                    ],
                ),
            ),
        ],
    )
