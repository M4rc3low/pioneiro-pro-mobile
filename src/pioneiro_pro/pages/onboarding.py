import flet as ft

from pioneiro_pro.repositories import ConfiguracaoRepository
from pioneiro_pro.ui import ACCENT, DANGER, SUCCESS, app_logo, brand_gradient, icon_badge, panel


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
    mensagem = ft.Text(size=12)

    def concluir(_):
        try:
            mensal = max(0, int(float(meta_mes.value or 0)))
            anual = max(0, int(float(meta_ano.value or 0)))
        except ValueError:
            mensagem.value = "Informe metas usando apenas números."
            mensagem.color = DANGER
            mensagem.update()
            return

        configuracoes.definir("nome_pioneiro", (nome.value or "").strip())
        configuracoes.definir("congregacao", (congregacao.value or "").strip())
        configuracoes.definir("meta_horas_mes", mensal)
        configuracoes.definir("meta_horas_ano", anual)
        configuracoes.definir("onboarding_concluido", "1")
        on_finish()

    feature_rows = [
        ("Tempo e metas", "Cronômetro, registros e progresso mensal.", ft.Icons.TIMER_OUTLINED),
        ("Estudantes", "Perfis, revisitas e avisos por proximidade.", ft.Icons.GROUP_OUTLINED),
        ("Agenda", "Compromissos e lembretes em um só lugar.", ft.Icons.CALENDAR_MONTH_OUTLINED),
        ("Relatórios", "Histórico, publicações e compartilhamento.", ft.Icons.INSIGHTS_OUTLINED),
    ]

    features = [
        ft.Row(
            controls=[
                icon_badge(icon, color=ACCENT, box_size=38),
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        spacing=1,
                        controls=[
                            ft.Text(title, weight=ft.FontWeight.BOLD),
                            ft.Text(subtitle, size=11, color=ft.Colors.GREY_500),
                        ],
                    ),
                ),
            ]
        )
        for title, subtitle, icon in feature_rows
    ]

    hero = ft.Container(
        padding=24,
        border_radius=28,
        gradient=brand_gradient(),
        content=ft.Column(
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                app_logo(78, 24),
                ft.Text(
                    "Pioneiro Pro",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Text(
                    "Organização pessoal com mais clareza, menos esforço.",
                    color=ft.Colors.BLUE_100,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )

    return ft.ListView(
        expand=True,
        padding=20,
        spacing=16,
        controls=[
            ft.Container(height=6),
            hero,
            panel(
                ft.Column(
                    spacing=12,
                    controls=[
                        ft.Text(
                            "Tudo o que importa em um só lugar",
                            size=19,
                            weight=ft.FontWeight.BOLD,
                        ),
                        *features,
                    ],
                ),
            ),
            panel(
                ft.Column(
                    spacing=12,
                    controls=[
                        ft.Text(
                            "Configure seu perfil",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            "Leva menos de um minuto e você pode alterar tudo depois.",
                            size=12,
                            color=ft.Colors.GREY_500,
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
                            "Começar a usar",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=concluir,
                        ),
                    ],
                ),
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.LOCK_OUTLINE, size=14, color=SUCCESS),
                    ft.Text(
                        "Seus dados ficam armazenados localmente no aparelho.",
                        size=11,
                        color=ft.Colors.GREY_500,
                    ),
                ],
            ),
            ft.Container(height=12),
        ],
    )
