import flet as ft

from pioneiro_pro.repositories import ConfiguracaoRepository


def configuracoes_view(
    page: ft.Page,
    configuracoes: ConfiguracaoRepository,
) -> ft.Control:
    config = configuracoes.todas()

    nome = ft.TextField(
        label="Seu nome",
        value=config["nome_pioneiro"],
    )
    congregacao = ft.TextField(
        label="Congregação",
        value=config["congregacao"],
    )
    meta_mes = ft.TextField(
        label="Meta mensal (horas)",
        value=config["meta_horas_mes"],
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    meta_ano = ft.TextField(
        label="Meta anual (horas)",
        value=config["meta_horas_ano"],
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    tema_escuro = ft.Switch(
        label="Tema escuro",
        value=config["tema"] == "escuro",
    )
    mensagem = ft.Text(size=13)

    def salvar(_):
        try:
            mensal = max(0, int(float(meta_mes.value or 0)))
            anual = max(0, int(float(meta_ano.value or 0)))
        except ValueError:
            mensagem.value = "As metas precisam ser números."
            mensagem.color = ft.Colors.RED
            mensagem.update()
            return

        configuracoes.definir("nome_pioneiro", (nome.value or "").strip())
        configuracoes.definir("congregacao", (congregacao.value or "").strip())
        configuracoes.definir("meta_horas_mes", mensal)
        configuracoes.definir("meta_horas_ano", anual)
        configuracoes.definir(
            "tema",
            "escuro" if tema_escuro.value else "claro",
        )

        page.theme_mode = (
            ft.ThemeMode.DARK if tema_escuro.value else ft.ThemeMode.LIGHT
        )
        page.update()

        mensagem.value = "Configurações salvas."
        mensagem.color = ft.Colors.GREEN_700
        mensagem.update()

    return ft.ListView(
        expand=True,
        padding=16,
        spacing=16,
        controls=[
            ft.Text("Configurações", size=26, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Personalize o Pioneiro Pro e suas metas.",
                color=ft.Colors.GREY_600,
            ),
            ft.Container(
                padding=16,
                border_radius=18,
                bgcolor=ft.Colors.SURFACE,
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Text("Perfil", size=18, weight=ft.FontWeight.BOLD),
                        nome,
                        congregacao,
                    ],
                ),
            ),
            ft.Container(
                padding=16,
                border_radius=18,
                bgcolor=ft.Colors.SURFACE,
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Text("Metas", size=18, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            controls=[
                                ft.Container(expand=True, content=meta_mes),
                                ft.Container(expand=True, content=meta_ano),
                            ]
                        ),
                    ],
                ),
            ),
            ft.Container(
                padding=16,
                border_radius=18,
                bgcolor=ft.Colors.SURFACE,
                content=ft.Column(
                    controls=[
                        ft.Text("Aparência", size=18, weight=ft.FontWeight.BOLD),
                        tema_escuro,
                    ]
                ),
            ),
            mensagem,
            ft.FilledButton(
                "Salvar configurações",
                icon=ft.Icons.SAVE_OUTLINED,
                on_click=salvar,
            ),
            ft.Divider(),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.BACKUP_OUTLINED),
                title=ft.Text("Backup"),
                subtitle=ft.Text("Backup e restauração entram na próxima etapa."),
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.INFO_OUTLINE),
                title=ft.Text("Pioneiro Pro"),
                subtitle=ft.Text("Versão 0.2.0 • Python + Flet"),
            ),
        ],
    )
