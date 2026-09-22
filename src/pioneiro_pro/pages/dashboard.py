import asyncio
from datetime import date

import flet as ft

from pioneiro_pro.repositories import (
    AtividadeRepository,
    ConfiguracaoRepository,
    EstudanteRepository,
    VisitaRepository,
)
from pioneiro_pro.ui import (
    ACCENT,
    brand_gradient,
    SUCCESS,
    empty_state,
    icon_badge,
    metric_card,
    page_header,
    panel,
    section_header,
    status_pill,
)
from pioneiro_pro.utils import formatar_minutos


MESES = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]


def _activity_card(item: dict) -> ft.Container:
    tipo = item["tipo"].replace("_", " ").title()
    publicacoes = sum(
        int(item.get(chave, 0) or 0)
        for chave in ("brochuras", "folhetos", "outras_publicacoes")
    )

    subtitle = item["data"]
    if item.get("observacao"):
        subtitle += f' • {item["observacao"]}'

    trailing = ft.Column(
        spacing=2,
        horizontal_alignment=ft.CrossAxisAlignment.END,
        controls=[
            ft.Text(
                formatar_minutos(item["minutos"]),
                weight=ft.FontWeight.BOLD,
                color=ACCENT,
            ),
            (
                ft.Text(
                    f"{publicacoes} publ.",
                    size=10,
                    color=ft.Colors.GREY_500,
                )
                if publicacoes
                else ft.Container()
            ),
        ],
    )

    return panel(
        ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                icon_badge(ft.Icons.SCHEDULE_OUTLINED),
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(tipo, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                subtitle,
                                size=11,
                                color=ft.Colors.GREY_500,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                    ),
                ),
                trailing,
            ],
        ),
        padding=14,
        radius=18,
    )


def dashboard_view(
    atividades: AtividadeRepository,
    estudantes: EstudanteRepository,
    visitas: VisitaRepository,
    configuracoes: ConfiguracaoRepository,
    on_navigate,
    page: ft.Page | None = None,
    cronometro=None,
    is_visible=lambda: True,
) -> ft.Control:
    config = configuracoes.todas()
    nome = config["nome_pioneiro"].strip()
    hoje = date.today()

    total = atividades.total_minutos_mes()
    registros = atividades.quantidade_mes()
    alunos = estudantes.quantidade_ativos()
    pendentes = visitas.quantidade_pendentes()
    publicacoes = atividades.publicacoes_mes()

    try:
        meta_minutos = max(0, int(float(config["meta_horas_mes"]))) * 60
    except ValueError:
        meta_minutos = 0

    progresso = min(1.0, total / meta_minutos) if meta_minutos else 0.0
    percentual = round(progresso * 100)
    recentes = atividades.listar_recentes(5)

    saudacao = f"Olá, {nome}" if nome else "Olá"
    periodo = f"{MESES[hoje.month - 1]} de {hoje.year}"

    # Cronômetro na Home: usa a mesma instância do formulário de registro.
    timer_text = ft.Text(
        cronometro.texto() if cronometro else "00:00:00",
        size=40,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE,
        text_align=ft.TextAlign.CENTER,
    )
    timer_status = ft.Text(
        "Em atividade" if cronometro and cronometro.rodando else "Pronto para iniciar",
        size=11,
        color=ft.Colors.BLUE_100,
    )

    async def atualizar_timer_home() -> None:
        while cronometro and cronometro.rodando and is_visible():
            timer_text.value = cronometro.texto()
            timer_status.value = "Em atividade"
            try:
                timer_text.update()
                timer_status.update()
            except Exception:
                return
            await asyncio.sleep(1)

    def iniciar_timer(_):
        if not cronometro:
            return
        cronometro.iniciar()
        timer_status.value = "Em atividade"
        timer_status.update()
        if page:
            page.run_task(atualizar_timer_home)

    def pausar_timer(_):
        if not cronometro:
            return
        cronometro.pausar()
        timer_text.value = cronometro.texto()
        timer_status.value = "Pausado"
        timer_text.update()
        timer_status.update()

    def zerar_timer(_):
        if not cronometro:
            return
        cronometro.zerar()
        timer_text.value = cronometro.texto()
        timer_status.value = "Pronto para iniciar"
        timer_text.update()
        timer_status.update()

    if cronometro and cronometro.rodando and page:
        page.run_task(atualizar_timer_home)

    timer_card = ft.Container(
        padding=20,
        border_radius=26,
        gradient=brand_gradient(),
        content=ft.Column(
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Cronômetro de serviço", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                        status_pill(
                            f"Meta {formatar_minutos(meta_minutos)}" if meta_minutos else "Sem meta",
                            color=ACCENT,
                        ),
                    ],
                ),
                timer_text,
                timer_status,
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=14,
                    controls=[
                        ft.IconButton(icon=ft.Icons.RESTART_ALT, tooltip="Zerar", on_click=zerar_timer),
                        ft.FilledButton(
                            "Pausar" if cronometro and cronometro.rodando else "Iniciar",
                            icon=ft.Icons.PAUSE if cronometro and cronometro.rodando else ft.Icons.PLAY_ARROW,
                            on_click=pausar_timer if cronometro and cronometro.rodando else iniciar_timer,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ADD_TASK,
                            tooltip="Registrar este tempo",
                            on_click=lambda _: on_navigate("registrar"),
                        ),
                    ],
                ),
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Container(expand=True, content=ft.OutlinedButton("Adicionar local", icon=ft.Icons.LOCATION_ON_OUTLINED, on_click=lambda _: on_navigate("agenda"))),
                        ft.Container(expand=True, content=ft.OutlinedButton("Registrar", icon=ft.Icons.EDIT_NOTE, on_click=lambda _: on_navigate("registrar"))),
                    ],
                ),
            ],
        ),
    )

    hero = ft.Container(
        padding=22,
        border_radius=26,
        gradient=brand_gradient(),
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text(
                                    "Meta mensal",
                                    size=13,
                                    color=ft.Colors.BLUE_100,
                                ),
                                ft.Text(
                                    formatar_minutos(total),
                                    size=32,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE,
                                ),
                            ],
                        ),
                        ft.Container(
                            padding=12,
                            border_radius=16,
                            bgcolor=ft.Colors.BLUE_600,
                            content=ft.Text(
                                f"{percentual}%",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ),
                    ],
                ),
                ft.ProgressBar(
                    value=progresso,
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE_500,
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            periodo,
                            size=11,
                            color=ft.Colors.BLUE_100,
                        ),
                        ft.Text(
                            (
                                f"Meta {formatar_minutos(meta_minutos)}"
                                if meta_minutos
                                else "Sem meta definida"
                            ),
                            size=11,
                            color=ft.Colors.BLUE_100,
                        ),
                    ],
                ),
            ],
        ),
    )

    pub_total = sum(publicacoes.values())
    publications_card = panel(
        ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                icon_badge(ft.Icons.AUTO_STORIES_OUTLINED, color=SUCCESS),
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                "Publicações no mês",
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                (
                                    f'{publicacoes["brochuras"]} brochuras • '
                                    f'{publicacoes["folhetos"]} folhetos • '
                                    f'{publicacoes["outras_publicacoes"]} outras'
                                ),
                                size=11,
                                color=ft.Colors.GREY_500,
                            ),
                        ],
                    ),
                ),
                status_pill(
                    str(pub_total),
                    color=SUCCESS,
                    icon=ft.Icons.LIBRARY_BOOKS_OUTLINED,
                ),
            ],
        ),
        padding=15,
    )

    recent_controls = (
        [_activity_card(item) for item in recentes]
        if recentes
        else [
            empty_state(
                ft.Icons.HISTORY_TOGGLE_OFF,
                "Seu histórico começa aqui",
                "Registre uma atividade para acompanhar seu progresso ao longo do mês.",
                action=ft.FilledButton(
                    "Registrar primeira atividade",
                    icon=ft.Icons.ADD,
                    on_click=lambda _: on_navigate("registrar"),
                ),
            )
        ]
    )

    return ft.ListView(
        expand=True,
        padding=18,
        spacing=16,
        controls=[
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=4, vertical=6),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text(saudacao + "! 👋", size=27, weight=ft.FontWeight.BOLD),
                                ft.Text("Seu serviço, suas metas e sua agenda em um só lugar.", size=11, color=ft.Colors.GREY_500),
                            ],
                        ),
                        icon_badge(ft.Icons.NOTIFICATIONS_NONE_ROUNDED, color=ACCENT),
                    ],
                ),
            ),
            timer_card,
            hero,
            ft.Row(
                spacing=10,
                controls=[
                    metric_card("Registros", str(registros), ft.Icons.CHECKLIST_ROUNDED),
                    metric_card("Estudantes", str(alunos), ft.Icons.GROUP_OUTLINED, color=SUCCESS),
                    metric_card("Na agenda", str(pendentes), ft.Icons.EVENT_AVAILABLE_OUTLINED, color=ft.Colors.PURPLE_500),
                ],
            ),
            publications_card,
            section_header(
                "Ações rápidas",
                subtitle="O que você quer fazer agora?",
            ),
            ft.Row(
                spacing=10,
                controls=[
                    ft.Container(
                        expand=True,
                        content=ft.FilledButton(
                            "Registrar",
                            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
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
                ],
            ),
            section_header(
                "Atividades recentes",
                subtitle="Seus últimos registros",
                trailing=ft.TextButton(
                    "Ver histórico",
                    on_click=lambda _: on_navigate("relatorios"),
                ),
            ),
            *recent_controls,
            ft.Container(height=6),
        ],
    )
