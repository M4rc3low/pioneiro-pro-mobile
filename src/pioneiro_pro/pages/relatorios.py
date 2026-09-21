from __future__ import annotations

from datetime import date

import flet as ft

from pioneiro_pro.repositories import AtividadeRepository, ConfiguracaoRepository
from pioneiro_pro.services import ExportacaoService
from pioneiro_pro.ui import (
    ACCENT,
    brand_gradient,
    DANGER,
    SUCCESS,
    WARNING,
    empty_state,
    icon_badge,
    metric_card,
    page_header,
    panel,
    section_header,
    status_pill,
)
from pioneiro_pro.utils import formatar_minutos


MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def _progresso(atual: int, meta: int) -> float:
    if meta <= 0:
        return 0.0
    return min(1.0, max(0.0, atual / meta))


def relatorios_view(
    atividades: AtividadeRepository,
    configuracoes: ConfiguracaoRepository,
    exportacao: ExportacaoService,
) -> ft.Control:
    hoje = date.today()
    config = configuracoes.todas()

    try:
        meta_mes_min = int(float(config["meta_horas_mes"])) * 60
    except ValueError:
        meta_mes_min = 0
    try:
        meta_ano_min = int(float(config["meta_horas_ano"])) * 60
    except ValueError:
        meta_ano_min = 0

    total_mes = atividades.total_minutos_mes()
    total_ano = atividades.total_minutos_ano()
    quantidade = atividades.quantidade_mes()
    publicacoes_mes = atividades.publicacoes_mes()
    relatorio_mensal = exportacao.relatorio_mensal_texto()

    editor_id: dict[str, int | None] = {"value": None}
    excluir_id: dict[str, int | None] = {"value": None}

    editor = ft.Container(visible=False)
    confirmacao = ft.Container(visible=False)
    lista_atividades = ft.Column(spacing=10)

    busca = ft.TextField(
        label="Buscar no histórico",
        hint_text="Data, observação ou tipo",
        prefix_icon=ft.Icons.SEARCH,
    )
    filtro_tipo = ft.Dropdown(
        label="Tipo",
        value="todos",
        width=145,
        options=[
            ft.DropdownOption(key="todos", text="Todos"),
            ft.DropdownOption(key="ministerio", text="Ministério"),
            ft.DropdownOption(key="estudo_biblico", text="Estudo bíblico"),
            ft.DropdownOption(key="revisita", text="Revisita"),
            ft.DropdownOption(key="outra", text="Outra"),
        ],
    )

    edit_data = ft.TextField(label="Data")
    edit_tipo = ft.Dropdown(
        label="Tipo",
        options=[
            ft.DropdownOption(key="ministerio", text="Ministério"),
            ft.DropdownOption(key="estudo_biblico", text="Estudo bíblico"),
            ft.DropdownOption(key="revisita", text="Revisita"),
            ft.DropdownOption(key="outra", text="Outra"),
        ],
    )
    edit_horas = ft.TextField(label="Horas", keyboard_type=ft.KeyboardType.NUMBER)
    edit_minutos = ft.TextField(label="Minutos", keyboard_type=ft.KeyboardType.NUMBER)
    edit_brochuras = ft.TextField(label="Brochuras", keyboard_type=ft.KeyboardType.NUMBER)
    edit_folhetos = ft.TextField(label="Folhetos", keyboard_type=ft.KeyboardType.NUMBER)
    edit_outras = ft.TextField(label="Outras publicações", keyboard_type=ft.KeyboardType.NUMBER)
    edit_obs = ft.TextField(
        label="Observação",
        multiline=True,
        min_lines=2,
        max_lines=4,
    )
    edit_msg = ft.Text(size=12)

    def fechar_editor(_=None):
        editor_id["value"] = None
        editor.visible = False
        editor.update()

    def abrir_editor(_, item: dict):
        editor_id["value"] = item["id"]
        edit_data.value = item["data"]
        edit_tipo.value = item["tipo"]
        edit_horas.value = str(item["minutos"] // 60)
        edit_minutos.value = str(item["minutos"] % 60)
        edit_brochuras.value = str(item.get("brochuras", 0))
        edit_folhetos.value = str(item.get("folhetos", 0))
        edit_outras.value = str(item.get("outras_publicacoes", 0))
        edit_obs.value = item["observacao"]
        edit_msg.value = ""
        editor.visible = True

        for control in [
            edit_data,
            edit_tipo,
            edit_horas,
            edit_minutos,
            edit_brochuras,
            edit_folhetos,
            edit_outras,
            edit_obs,
            edit_msg,
            editor,
        ]:
            control.update()

    def salvar_edicao(_):
        try:
            total = int(edit_horas.value or 0) * 60 + int(edit_minutos.value or 0)
            qtd_brochuras = max(0, int(edit_brochuras.value or 0))
            qtd_folhetos = max(0, int(edit_folhetos.value or 0))
            qtd_outras = max(0, int(edit_outras.value or 0))
        except ValueError:
            edit_msg.value = "Tempo e publicações precisam ser números."
            edit_msg.color = DANGER
            edit_msg.update()
            return

        if editor_id["value"] is None or total <= 0:
            edit_msg.value = "Informe um tempo válido."
            edit_msg.color = DANGER
            edit_msg.update()
            return

        atividades.atualizar(
            int(editor_id["value"]),
            edit_data.value or hoje.isoformat(),
            edit_tipo.value or "ministerio",
            total,
            edit_obs.value or "",
            qtd_brochuras,
            qtd_folhetos,
            qtd_outras,
        )
        fechar_editor()
        carregar_atividades()

    def pedir_exclusao(_, atividade_id: int):
        excluir_id["value"] = atividade_id
        confirmacao.visible = True
        confirmacao.update()

    def cancelar_exclusao(_=None):
        excluir_id["value"] = None
        confirmacao.visible = False
        confirmacao.update()

    def confirmar_exclusao(_):
        if excluir_id["value"] is not None:
            atividades.excluir(int(excluir_id["value"]))
        cancelar_exclusao()
        carregar_atividades()

    def activity_card(item: dict) -> ft.Container:
        publicacoes = sum(
            int(item.get(chave, 0) or 0)
            for chave in ("brochuras", "folhetos", "outras_publicacoes")
        )
        detalhes = f'{item["data"]} • {formatar_minutos(item["minutos"])}'
        if item.get("observacao"):
            detalhes += f' • {item["observacao"]}'

        return panel(
            ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    icon_badge(ft.Icons.HISTORY_TOGGLE_OFF),
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text(
                                    item["tipo"].replace("_", " ").title(),
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    detalhes,
                                    size=11,
                                    color=ft.Colors.GREY_500,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                (
                                    status_pill(
                                        f"{publicacoes} publicação(ões)",
                                        color=ft.Colors.PURPLE_500,
                                        icon=ft.Icons.AUTO_STORIES_OUTLINED,
                                    )
                                    if publicacoes
                                    else ft.Container()
                                ),
                            ],
                        ),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        tooltip="Editar",
                        on_click=lambda e, registro=item: abrir_editor(e, registro),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        tooltip="Excluir",
                        on_click=lambda e, atividade_id=item["id"]: pedir_exclusao(
                            e,
                            atividade_id,
                        ),
                    ),
                ],
            ),
            padding=13,
            radius=19,
        )

    def carregar_atividades() -> None:
        tipo = None if filtro_tipo.value == "todos" else filtro_tipo.value
        itens = atividades.buscar(busca.value or "", tipo, limite=100)
        lista_atividades.controls = (
            [activity_card(item) for item in itens]
            if itens
            else [
                empty_state(
                    ft.Icons.SEARCH_OFF_OUTLINED,
                    "Nenhum registro encontrado",
                    "Altere a busca ou o filtro para visualizar outros registros.",
                )
            ]
        )

        try:
            lista_atividades.update()
        except Exception:
            pass

    editor.content = ft.Column(
        spacing=12,
        controls=[
            section_header(
                "Editar atividade",
                subtitle="Corrija tempo, publicações ou observações.",
                trailing=ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    on_click=fechar_editor,
                ),
            ),
            edit_data,
            edit_tipo,
            ft.Row(
                controls=[
                    ft.Container(expand=True, content=edit_horas),
                    ft.Container(expand=True, content=edit_minutos),
                ]
            ),
            ft.Text("Publicações entregues", weight=ft.FontWeight.BOLD),
            ft.Row(
                controls=[
                    ft.Container(expand=True, content=edit_brochuras),
                    ft.Container(expand=True, content=edit_folhetos),
                ]
            ),
            edit_outras,
            edit_obs,
            edit_msg,
            ft.FilledButton(
                "Salvar alterações",
                icon=ft.Icons.SAVE_OUTLINED,
                on_click=salvar_edicao,
            ),
        ],
    )
    editor.padding = 18
    editor.border_radius = 22
    editor.bgcolor = ft.Colors.SURFACE

    confirmacao.content = ft.Row(
        controls=[
            ft.Container(
                expand=True,
                content=ft.Text(
                    "Excluir este registro?",
                    color=DANGER,
                    weight=ft.FontWeight.BOLD,
                ),
            ),
            ft.TextButton("Cancelar", on_click=cancelar_exclusao),
            ft.FilledButton("Excluir", on_click=confirmar_exclusao),
        ]
    )
    confirmacao.padding = 12
    confirmacao.border_radius = 16
    confirmacao.bgcolor = ft.Colors.SURFACE

    barras = []
    for item in atividades.totais_por_mes(hoje.year):
        barras.append(
            ft.Row(
                controls=[
                    ft.Text(MESES[item["mes"] - 1], width=32, size=11),
                    ft.Container(
                        expand=True,
                        content=ft.ProgressBar(
                            value=_progresso(item["minutos"], meta_mes_min),
                        ),
                    ),
                    ft.Text(
                        formatar_minutos(item["minutos"]),
                        width=68,
                        size=11,
                        text_align=ft.TextAlign.RIGHT,
                    ),
                ]
            )
        )

    busca.on_change = lambda _: carregar_atividades()
    filtro_tipo.on_change = lambda _: carregar_atividades()
    carregar_atividades()

    progresso_mes = _progresso(total_mes, meta_mes_min)
    progresso_ano = _progresso(total_ano, meta_ano_min)

    hero = ft.Container(
        padding=22,
        border_radius=26,
        gradient=brand_gradient(),
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text(
                                    "Este mês",
                                    color=ft.Colors.BLUE_100,
                                    size=12,
                                ),
                                ft.Text(
                                    formatar_minutos(total_mes),
                                    size=31,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE,
                                ),
                            ],
                        ),
                        status_pill(
                            f"{round(progresso_mes * 100)}%",
                            color=SUCCESS,
                            icon=ft.Icons.TRENDING_UP,
                        ),
                    ],
                ),
                ft.ProgressBar(
                    value=progresso_mes,
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE_500,
                ),
                ft.Text(
                    (
                        f"Meta mensal: {formatar_minutos(meta_mes_min)}"
                        if meta_mes_min
                        else "Sem meta mensal definida"
                    ),
                    size=11,
                    color=ft.Colors.BLUE_100,
                ),
            ],
        ),
    )

    share_card = panel(
        ft.Column(
            spacing=10,
            controls=[
                section_header(
                    "Relatório mensal",
                    subtitle="Pronto para WhatsApp, e-mail ou outro app.",
                    trailing=icon_badge(
                        ft.Icons.SHARE_OUTLINED,
                        color=SUCCESS,
                    ),
                ),
                ft.Text(relatorio_mensal, size=12),
                ft.Button(
                    "Compartilhar relatório",
                    icon=ft.Icons.SHARE,
                    action=ft.ShareText(
                        relatorio_mensal,
                        subject="Relatório mensal - Pioneiro Pro",
                        title="Compartilhar relatório mensal",
                    ),
                ),
            ],
        )
    )

    return ft.ListView(
        expand=True,
        padding=18,
        spacing=16,
        controls=[
            page_header(
                "Relatórios",
                "Acompanhe progresso, publicações e histórico.",
                ft.Icons.INSIGHTS_OUTLINED,
            ),
            hero,
            ft.Row(
                spacing=10,
                controls=[
                    metric_card(
                        "Registros",
                        str(quantidade),
                        ft.Icons.CHECKLIST_OUTLINED,
                    ),
                    metric_card(
                        "Ano",
                        formatar_minutos(total_ano),
                        ft.Icons.CALENDAR_TODAY_OUTLINED,
                        color=ft.Colors.PURPLE_500,
                        helper=f"{round(progresso_ano * 100)}% da meta",
                    ),
                ],
            ),
            ft.Row(
                spacing=10,
                controls=[
                    metric_card(
                        "Brochuras",
                        str(publicacoes_mes["brochuras"]),
                        ft.Icons.MENU_BOOK_OUTLINED,
                        color=SUCCESS,
                    ),
                    metric_card(
                        "Folhetos",
                        str(publicacoes_mes["folhetos"]),
                        ft.Icons.DESCRIPTION_OUTLINED,
                        color=WARNING,
                    ),
                ],
            ),
            share_card,
            section_header(
                f"Progresso mensal • {hoje.year}",
                subtitle="Comparação visual mês a mês.",
            ),
            panel(ft.Column(spacing=9, controls=barras), padding=15),
            editor,
            confirmacao,
            section_header(
                "Histórico de atividades",
                subtitle="Busque, edite ou exclua qualquer registro salvo.",
            ),
            ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(expand=True, content=busca),
                    filtro_tipo,
                ]
            ),
            lista_atividades,
            ft.Container(height=6),
        ],
    )
