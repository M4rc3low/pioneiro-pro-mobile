import asyncio
from datetime import date

import flet as ft

from pioneiro_pro.repositories import AtividadeRepository
from pioneiro_pro.services import CronometroService


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
    observacao = ft.TextField(
        label="Observação",
        multiline=True,
        min_lines=2,
        max_lines=4,
    )
    mensagem = ft.Text(size=13)
    cronometro_texto = ft.Text(
        cronometro.texto(),
        size=38,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )
    status = ft.Text(
        "Em andamento" if cronometro.rodando else "Pronto para iniciar",
        size=12,
        color=ft.Colors.GREEN_700 if cronometro.rodando else ft.Colors.GREY_600,
    )

    async def atualizar_cronometro() -> None:
        while cronometro.rodando and is_visible():
            cronometro_texto.value = cronometro.texto()
            status.value = "Em andamento"
            status.color = ft.Colors.GREEN_700
            try:
                cronometro_texto.update()
                status.update()
            except Exception:
                return
            await asyncio.sleep(1)

    def iniciar(_):
        cronometro.iniciar()
        status.value = "Em andamento"
        status.color = ft.Colors.GREEN_700
        status.update()
        page.run_task(atualizar_cronometro)

    def pausar(_):
        cronometro.pausar()
        cronometro_texto.value = cronometro.texto()
        status.value = "Pausado"
        status.color = ft.Colors.ORANGE_700
        cronometro_texto.update()
        status.update()

    def zerar(_):
        cronometro.zerar()
        cronometro_texto.value = cronometro.texto()
        status.value = "Pronto para iniciar"
        status.color = ft.Colors.GREY_600
        cronometro_texto.update()
        status.update()

    def usar_tempo(_):
        total = cronometro.minutos_para_registro()
        horas.value = str(total // 60)
        minutos.value = str(total % 60)
        horas.update()
        minutos.update()
        mensagem.value = "Tempo do cronômetro transferido para o registro."
        mensagem.color = ft.Colors.BLUE_700
        mensagem.update()

    def salvar(_):
        try:
            h = max(0, int(horas.value or 0))
            m = max(0, int(minutos.value or 0))
            total = h * 60 + m
        except ValueError:
            mensagem.value = "Informe horas e minutos usando apenas números."
            mensagem.color = ft.Colors.RED
            mensagem.update()
            return

        if total <= 0:
            mensagem.value = "Informe um tempo maior que zero."
            mensagem.color = ft.Colors.RED
            mensagem.update()
            return

        atividades.criar(
            data=data.value or date.today().isoformat(),
            tipo=tipo.value or "ministerio",
            minutos=total,
            observacao=observacao.value or "",
        )
        cronometro.zerar()
        on_saved()

    if cronometro.rodando:
        page.run_task(atualizar_cronometro)

    return ft.ListView(
        expand=True,
        padding=16,
        spacing=16,
        controls=[
            ft.Text("Registrar atividade", size=26, weight=ft.FontWeight.BOLD),
            ft.Container(
                padding=18,
                border_radius=18,
                bgcolor=ft.Colors.WHITE,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(
                                    ft.Icons.TIMER_OUTLINED,
                                    color=ft.Colors.BLUE_700,
                                ),
                                ft.Text(
                                    "Cronômetro",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                        ),
                        cronometro_texto,
                        status,
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
                        ft.TextButton(
                            "Usar este tempo no registro",
                            icon=ft.Icons.DOWNLOAD_DONE,
                            on_click=usar_tempo,
                        ),
                    ],
                ),
            ),
            ft.Text(
                "Registro manual",
                size=18,
                weight=ft.FontWeight.BOLD,
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
            observacao,
            mensagem,
            ft.FilledButton(
                "Salvar atividade",
                icon=ft.Icons.SAVE_OUTLINED,
                on_click=salvar,
            ),
        ],
    )
