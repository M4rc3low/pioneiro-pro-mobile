import asyncio
from datetime import date

import flet as ft

from pioneiro_pro.repositories import AtividadeRepository
from pioneiro_pro.services import CronometroService
from pioneiro_pro.ui import (
    ACCENT,
    brand_gradient,
    DANGER,
    SUCCESS,
    WARNING,
    icon_badge,
    page_header,
    panel,
    section_header,
    status_pill,
)


def registrar_view(
    page: ft.Page,
    atividades: AtividadeRepository,
    cronometro: CronometroService,
    is_visible,
    on_saved,
) -> ft.Control:
    data = ft.TextField(label="Data", value=date.today().isoformat())
    tipo = ft.Dropdown(
        label="Tipo de atividade",
        value="ministerio",
        options=[
            ft.DropdownOption(key="ministerio", text="Ministério"),
            ft.DropdownOption(key="estudo_biblico", text="Estudo bíblico"),
            ft.DropdownOption(key="revisita", text="Revisita"),
            ft.DropdownOption(key="outra", text="Outra"),
        ],
    )
    horas = ft.TextField(
        label="Horas",
        value="0",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    minutos = ft.TextField(
        label="Minutos",
        value="0",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    brochuras = ft.TextField(
        label="Brochuras",
        value="0",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    folhetos = ft.TextField(
        label="Folhetos",
        value="0",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    outras_publicacoes = ft.TextField(
        label="Outras publicações",
        value="0",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    observacao = ft.TextField(
        label="Observação",
        multiline=True,
        min_lines=2,
        max_lines=4,
    )
    mensagem = ft.Text(size=12)

    cronometro_texto = ft.Text(
        cronometro.texto(),
        size=42,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
        color=ft.Colors.WHITE,
    )
    status_texto = ft.Text(
        "Em andamento" if cronometro.rodando else "Pronto para iniciar",
        size=11,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE,
    )

    async def atualizar_cronometro() -> None:
        while cronometro.rodando and is_visible():
            cronometro_texto.value = cronometro.texto()
            status_texto.value = "Em andamento"
            try:
                cronometro_texto.update()
                status_texto.update()
            except Exception:
                return
            await asyncio.sleep(1)

    def iniciar(_):
        cronometro.iniciar()
        status_texto.value = "Em andamento"
        status_texto.update()
        page.run_task(atualizar_cronometro)

    def pausar(_):
        cronometro.pausar()
        cronometro_texto.value = cronometro.texto()
        status_texto.value = "Pausado"
        cronometro_texto.update()
        status_texto.update()

    def zerar(_):
        cronometro.zerar()
        cronometro_texto.value = cronometro.texto()
        status_texto.value = "Pronto para iniciar"
        cronometro_texto.update()
        status_texto.update()

    def usar_tempo(_):
        total = cronometro.minutos_para_registro()
        horas.value = str(total // 60)
        minutos.value = str(total % 60)
        horas.update()
        minutos.update()
        mensagem.value = "Tempo do cronômetro transferido para o registro."
        mensagem.color = ACCENT
        mensagem.update()

    def salvar(_):
        try:
            h = max(0, int(horas.value or 0))
            m = max(0, int(minutos.value or 0))
            total = h * 60 + m
            qtd_brochuras = max(0, int(brochuras.value or 0))
            qtd_folhetos = max(0, int(folhetos.value or 0))
            qtd_outras = max(0, int(outras_publicacoes.value or 0))
        except ValueError:
            mensagem.value = "Use apenas números nos campos de tempo e publicações."
            mensagem.color = DANGER
            mensagem.update()
            return

        if total <= 0:
            mensagem.value = "Informe um tempo maior que zero."
            mensagem.color = DANGER
            mensagem.update()
            return

        atividades.criar(
            data=data.value or date.today().isoformat(),
            tipo=tipo.value or "ministerio",
            minutos=total,
            observacao=observacao.value or "",
            brochuras=qtd_brochuras,
            folhetos=qtd_folhetos,
            outras_publicacoes=qtd_outras,
        )
        cronometro.zerar()
        on_saved()

    if cronometro.rodando:
        page.run_task(atualizar_cronometro)

    timer_card = ft.Container(
        padding=22,
        border_radius=20,
        gradient=brand_gradient(),
        content=ft.Column(
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Icon(
                                    ft.Icons.TIMER_OUTLINED,
                                    color=ft.Colors.WHITE,
                                    size=21,
                                ),
                                ft.Text(
                                    "Cronômetro",
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                        ),
                        status_pill(
                            "Ativo" if cronometro.rodando else "Manual",
                            color=SUCCESS if cronometro.rodando else WARNING,
                        ),
                    ],
                ),
                cronometro_texto,
                status_texto,
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.FilledButton(
                            "Iniciar",
                            icon=ft.Icons.PLAY_ARROW,
                            on_click=iniciar,
                        ),
                        ft.OutlinedButton(
                            "Pausar",
                            icon=ft.Icons.PAUSE,
                            on_click=pausar,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.RESTART_ALT,
                            tooltip="Zerar",
                            on_click=zerar,
                        ),
                    ],
                ),
                ft.OutlinedButton(
                    "Usar este tempo no registro",
                    icon=ft.Icons.DOWNLOAD_DONE,
                    on_click=usar_tempo,
                ),
            ],
        ),
    )

    return ft.ListView(
        expand=True,
        padding=14,
        spacing=12,
        controls=[
            page_header(
                "Registrar atividade",
                "Use o cronômetro ou informe o tempo manualmente.",
                ft.Icons.ADD_CIRCLE_OUTLINE,
            ),
            timer_card,
            panel(
                ft.Column(
                    spacing=12,
                    controls=[
                        section_header(
                            "Detalhes da atividade",
                            subtitle="Data, tipo e tempo registrado.",
                            trailing=icon_badge(ft.Icons.EDIT_CALENDAR_OUTLINED),
                        ),
                        data,
                        tipo,
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Container(expand=True, content=horas),
                                ft.Container(expand=True, content=minutos),
                            ],
                        ),
                    ],
                ),
            ),
            panel(
                ft.Column(
                    spacing=12,
                    controls=[
                        section_header(
                            "Publicações entregues",
                            subtitle="Opcional — você pode ajustar depois.",
                            trailing=icon_badge(
                                ft.Icons.AUTO_STORIES_OUTLINED,
                                color=ft.Colors.PURPLE_500,
                            ),
                        ),
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Container(expand=True, content=brochuras),
                                ft.Container(expand=True, content=folhetos),
                            ],
                        ),
                        outras_publicacoes,
                    ],
                ),
            ),
            panel(
                ft.Column(
                    spacing=10,
                    controls=[
                        section_header(
                            "Observações",
                            subtitle="Anote algo útil sobre essa atividade.",
                        ),
                        observacao,
                    ],
                ),
            ),
            mensagem,
            ft.FilledButton(
                "Salvar atividade",
                icon=ft.Icons.SAVE_OUTLINED,
                on_click=salvar,
            ),
            ft.Container(height=6),
        ],
    )
