import asyncio
from datetime import date

import flet as ft

from pioneiro_pro.repositories import (
    AtividadeRepository,
    ConfiguracaoRepository,
    EstudanteRepository,
    VisitaRepository,
)
from pioneiro_pro.ui import ACCENT
from pioneiro_pro.utils import formatar_minutos


MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]
DIAS = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]


def _glass(content, padding=16, radius=22, expand=None, on_click=None):
    return ft.Container(
        expand=expand,
        padding=padding,
        border_radius=radius,
        bgcolor=ft.Colors.with_opacity(0.88, "#08243A"),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.42, "#4D9BD0")),
        shadow=ft.BoxShadow(
            blur_radius=18,
            color=ft.Colors.with_opacity(0.22, ft.Colors.BLACK),
            offset=ft.Offset(0, 7),
        ),
        content=content,
        on_click=on_click,
        ink=on_click is not None,
    )


def _metric(title, value, helper, icon, color, on_click=None):
    return _glass(
        ft.Column(
            spacing=7,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Container(
                            width=42,
                            height=42,
                            border_radius=12,
                            bgcolor=ft.Colors.with_opacity(0.85, color),
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(icon, color=ft.Colors.WHITE, size=21),
                        ),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, color="#91B9D6", size=17),
                    ],
                ),
                ft.Text(
                    title,
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Row(
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    controls=[
                        ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Container(
                            expand=True,
                            content=ft.Text(
                                helper,
                                size=8,
                                color=ft.Colors.WHITE_70,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ),
                    ],
                ),
            ],
        ),
        padding=12,
        radius=18,
        expand=True,
        on_click=on_click,
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
    alunos = estudantes.quantidade_ativos()
    pendentes = visitas.quantidade_pendentes()
    publicacoes = atividades.publicacoes_mes()
    pub_total = sum(publicacoes.values())

    try:
        meta_horas = max(0, int(float(config["meta_horas_mes"])))
    except (ValueError, TypeError):
        meta_horas = 0
    meta_minutos = meta_horas * 60
    progresso = min(1.0, total / meta_minutos) if meta_minutos else 0.0
    percentual = round(progresso * 100)
    restante = max(0, meta_minutos - total)

    timer_text = ft.Text(
        cronometro.texto() if cronometro else "00:00:00",
        size=36,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE,
        text_align=ft.TextAlign.CENTER,
    )
    timer_status = ft.Text(
        "Em atividade" if cronometro and cronometro.rodando else "Pronto para iniciar",
        size=10,
        color=ft.Colors.WHITE_70,
    )

    async def atualizar_timer_home():
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

    timer_card = _glass(
        ft.Column(
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Tempo de hoje", size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=12, vertical=7),
                            border_radius=15,
                            bgcolor=ft.Colors.with_opacity(0.72, "#061C2F"),
                            content=ft.Column(
                                spacing=0,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text("Meta do mês", size=9, color="#8EDCFF"),
                                    ft.Text(f"{meta_horas}h" if meta_horas else "—", size=16, weight=ft.FontWeight.BOLD, color="#16B8FF"),
                                ],
                            ),
                        ),
                    ],
                ),
                timer_text,
                timer_status,
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.IconButton(icon=ft.Icons.RESTART_ALT_ROUNDED, icon_color="#8EDCFF", tooltip="Zerar", on_click=zerar_timer),
                        ft.Container(
                            width=64,
                            height=64,
                            border_radius=32,
                            gradient=ft.LinearGradient(colors=["#22C7F2", "#087CF0"]),
                            alignment=ft.Alignment.CENTER,
                            content=ft.IconButton(
                                icon=ft.Icons.PAUSE_ROUNDED if cronometro and cronometro.rodando else ft.Icons.PLAY_ARROW_ROUNDED,
                                icon_size=29,
                                icon_color=ft.Colors.WHITE,
                                on_click=pausar_timer if cronometro and cronometro.rodando else iniciar_timer,
                            ),
                        ),
                        ft.IconButton(icon=ft.Icons.TIMER_OUTLINED, icon_color="#8EDCFF", tooltip="Registrar", on_click=lambda _: on_navigate("registrar")),
                    ],
                ),
            ],
        ),
        padding=17,
        radius=24,
    )

    greeting = ft.Container(
        padding=ft.Padding.only(left=4, right=4, top=8, bottom=10),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        spacing=5,
                        controls=[
                            ft.Text(f"Olá, {nome}!" if nome else "Olá!", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text(
                                "“Tenham sempre bastante para fazer na obra do Senhor, sabendo que o seu trabalho árduo no Senhor não é em vão.”",
                                size=12,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text("1 Coríntios 15:58", size=11, weight=ft.FontWeight.BOLD, color="#D6ECFF"),
                        ],
                    ),
                ),
                ft.Container(
                    width=78,
                    padding=8,
                    border_radius=17,
                    bgcolor=ft.Colors.with_opacity(0.60, "#09243A"),
                    content=ft.Column(
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(DIAS[hoje.weekday()], size=8, color=ft.Colors.WHITE_70),
                            ft.Text(str(hoje.day), size=25, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text(f"{MESES[hoje.month - 1]} {hoje.year}", size=8, color=ft.Colors.WHITE_70),
                        ],
                    ),
                ),
            ],
        ),
    )

    scenic_hero = ft.Container(
        height=400,
        border_radius=28,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Stack(
            controls=[
                ft.Image(src="https://images.unsplash.com/photo-1759390084722-c246aeadb6a1?auto=format&fit=crop&fm=jpg&q=82&w=1600", width=1000, height=400, fit=ft.BoxFit.COVER),
                ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment.TOP_CENTER,
                        end=ft.Alignment.BOTTOM_CENTER,
                        colors=[
                            ft.Colors.with_opacity(0.08, "#061827"),
                            ft.Colors.with_opacity(0.18, "#061827"),
                            ft.Colors.with_opacity(0.72, "#061827"),
                        ],
                    ),
                ),
                ft.Container(
                    padding=14,
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            greeting,
                            ft.Container(expand=True),
                            timer_card,
                        ],
                    ),
                ),
            ],
        ),
    )

    metrics = ft.Column(
        spacing=10,
        controls=[
            ft.Row(
                spacing=10,
                controls=[
                    _metric("Estudantes", str(alunos), "ativos", ft.Icons.GROUP_ROUNDED, "#087CF0", lambda _: on_navigate("estudantes")),
                    _metric("Na agenda", str(pendentes), "pendentes", ft.Icons.CALENDAR_MONTH_ROUNDED, "#7B16D9", lambda _: on_navigate("agenda")),
                ],
            ),
            ft.Row(
                spacing=10,
                controls=[
                    _metric("Publicações", str(pub_total), f'{publicacoes["brochuras"]} broch. • {publicacoes["folhetos"]} folh.', ft.Icons.AUTO_STORIES_ROUNDED, "#008C3A", lambda _: on_navigate("relatorios")),
                    _metric("Relatórios", formatar_minutos(total), MESES[hoje.month - 1], ft.Icons.BAR_CHART_ROUNDED, "#087CF0", lambda _: on_navigate("relatorios")),
                ],
            ),
        ],
    )

    progress_card = _glass(
        ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Meu progresso este mês", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text(f"{percentual}%", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ],
                ),
                ft.ProgressBar(value=progresso, color="#16B8FF", bgcolor="#214C6D"),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(f"{formatar_minutos(total)} de {meta_horas}h" if meta_horas else formatar_minutos(total), size=10, color=ft.Colors.WHITE_70),
                        ft.Text(f"{formatar_minutos(restante)} restantes" if meta_horas else "Defina sua meta", size=10, color=ft.Colors.WHITE_70),
                    ],
                ),
            ],
        ),
        padding=14,
        radius=19,
    )

    futuras = [v for v in visitas.listar(somente_futuras=True) if not v.get("concluida")]
    proxima = futuras[0] if futuras else None
    if proxima:
        nome_visita = proxima.get("estudante_nome") or proxima.get("tipo", "Visita").replace("_", " ").title()
        visita_card = _glass(
            ft.Column(
                spacing=9,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.GROUP_ROUNDED, color="#73C9FF"),
                            ft.Container(
                                expand=True,
                                content=ft.Column(
                                    spacing=1,
                                    controls=[
                                        ft.Text(nome_visita, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                        ft.Text(proxima.get("observacao") or proxima.get("tipo", "").replace("_", " ").title(), size=10, color=ft.Colors.WHITE_70),
                                    ],
                                ),
                            ),
                            ft.Column(
                                spacing=0,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                controls=[
                                    ft.Text("Hoje" if proxima["data"] == hoje.isoformat() else proxima["data"], size=9, color=ft.Colors.WHITE_70),
                                    ft.Text(proxima.get("horario") or "—", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ],
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.OutlinedButton("Ver na agenda", icon=ft.Icons.LOCATION_ON_OUTLINED, expand=True, on_click=lambda _: on_navigate("agenda")),
                            ft.FilledButton("Iniciar visita", icon=ft.Icons.PLAY_ARROW_ROUNDED, expand=True, on_click=lambda _: on_navigate("agenda")),
                        ],
                    ),
                ],
            ),
            padding=14,
            radius=19,
        )
    else:
        visita_card = _glass(
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.EVENT_AVAILABLE_ROUNDED, color="#73C9FF"),
                    ft.Text("Nenhuma visita pendente.", color=ft.Colors.WHITE_70),
                ],
            ),
            padding=14,
            radius=19,
        )

    return ft.ListView(
        expand=True,
        padding=ft.Padding.only(left=14, right=14, top=6, bottom=18),
        spacing=12,
        controls=[
            scenic_hero,
            metrics,
            progress_card,
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Próximas visitas", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.TextButton("Ver todas", on_click=lambda _: on_navigate("agenda")),
                ],
            ),
            visita_card,
            ft.Container(height=4),
        ],
    )
