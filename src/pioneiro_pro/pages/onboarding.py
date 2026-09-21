import flet as ft

from pioneiro_pro.repositories import ConfiguracaoRepository


def onboarding_view(
    configuracoes: ConfiguracaoRepository,
    on_finish,
) -> ft.Control:
    nome = ft.TextField(label="Seu nome")
    congregacao = ft.TextField(label="Congregação")
    meta_mes = ft.TextField(
        label="Meta mensal de horas",
        value="50",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    meta_ano = ft.TextField(
        label="Meta anual de horas",
        value="600",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    mensagem = ft.Text(size=13)

    def concluir(_):
        try:
            mensal = max(0, int(float(meta_mes.value or 0)))
            anual = max(0, int(float(meta_ano.value or 0)))
        except ValueError:
            mensagem.value = "Informe metas usando apenas números."
            mensagem.color = ft.Colors.RED
            mensagem.update()
            return

        configuracoes.definir("nome_pioneiro", (nome.value or "").strip())
        configuracoes.definir("congregacao", (congregacao.value or "").strip())
        configuracoes.definir("meta_horas_mes", mensal)
        configuracoes.definir("meta_horas_ano", anual)
        configuracoes.definir("onboarding_concluido", "1")
        on_finish()

    return ft.ListView(
        expand=True,
        padding=24,
        spacing=18,
        controls=[
            ft.Container(height=16),
            ft.Icon(
                ft.Icons.EXPLORE_OUTLINED,
                size=72,
                color=ft.Colors.BLUE_700,
            ),
            ft.Text(
                "Bem-vindo ao Pioneiro Pro",
                size=30,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Text(
                "Organize seu tempo, estudantes, revisitas, agenda e metas em um só lugar.",
                color=ft.Colors.GREY_600,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(
                padding=18,
                border_radius=20,
                bgcolor=ft.Colors.SURFACE,
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Text(
                            "Configuração inicial",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                        nome,
                        congregacao,
                        ft.Row(
                            controls=[
                                ft.Container(expand=True, content=meta_mes),
                                ft.Container(expand=True, content=meta_ano),
                            ]
                        ),
                        mensagem,
                        ft.FilledButton(
                            "Começar",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=concluir,
                        ),
                    ],
                ),
            ),
            ft.Text(
                "Essas informações podem ser alteradas depois em Configurações.",
                size=12,
                color=ft.Colors.GREY_500,
                text_align=ft.TextAlign.CENTER,
            ),
        ],
    )
