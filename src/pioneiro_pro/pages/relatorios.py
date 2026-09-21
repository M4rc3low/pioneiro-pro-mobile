from __future__ import annotations

from datetime import date

import flet as ft

from pioneiro_pro.repositories import AtividadeRepository, ConfiguracaoRepository
from pioneiro_pro.services import ExportacaoService
from pioneiro_pro.utils import formatar_minutos


MESES = [
    "Jan",
    "Fev",
    "Mar",
    "Abr",
    "Mai",
    "Jun",
    "Jul",
    "Ago",
    "Set",
    "Out",
    "Nov",
    "Dez",
]


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
    meta_mes_min = int(float(config["meta_horas_mes"])) * 60
    meta_ano_min = int(float(config["meta_horas_ano"])) * 60

    total_mes = atividades.total_minutos_mes()
    total_ano = atividades.total_minutos_ano()
    quantidade = atividades.quantidade_mes()
    publicacoes_mes = atividades.publicacoes_mes()
    relatorio_mensal = exportacao.relatorio_mensal_texto()

    editor_id: dict[str, int | None] = {"value": None}
    excluir_id: dict[str, int | None] = {"value": None}

    editor = ft.Container(visible=False)
    confirmacao = ft.Container(visible=False)
    lista_atividades = ft.Column(spacing=8)
    busca = ft.TextField(
        label="Buscar no histórico",
        hint_text="Data, observação ou tipo",
        prefix_icon=ft.Icons.SEARCH,
    )
    filtro_tipo = ft.Dropdown(
        label="Tipo",
        value="todos",
        width=150,
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
    edit_obs = ft.TextField(label="Observação", multiline=True, min_lines=2, max_lines=4)
    edit_msg = ft.Text(size=13)

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
            edit_msg.value = "Horas e minutos precisam ser números."
            edit_msg.color = ft.Colors.RED
            edit_msg.update()
            return

        if editor_id["value"] is None or total <= 0:
            edit_msg.value = "Informe um tempo válido."
            edit_msg.color = ft.Colors.RED
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

    def carregar_atividades() -> None:
        tipo = None if filtro_tipo.value == "todos" else filtro_tipo.value
        itens = atividades.buscar(busca.value or "", tipo, limite=100)
        controls: list[ft.Control] = []

        for item in itens:
            controls.append(
                ft.Container(
                    padding=10,
                    border_radius=14,
                    bgcolor=ft.Colors.WHITE,
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.SCHEDULE, color=ft.Colors.BLUE_700),
                            ft.Container(
                                expand=True,
                                content=ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(
                                            item["tipo"].replace("_", " ").title(),
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            f'{item["data"]} • {formatar_minutos(item["minutos"])}',
                                            size=12,
                                            color=ft.Colors.GREY_600,
                                        ),
                                        ft.Text(
                                            " • ".join(
                                                parte for parte in [
                                                    f'Brochuras: {item.get("brochuras", 0)}' if item.get("brochuras", 0) else "",
                                                    f'Folhetos: {item.get("folhetos", 0)}' if item.get("folhetos", 0) else "",
                                                    f'Outras: {item.get("outras_publicacoes", 0)}' if item.get("outras_publicacoes", 0) else "",
                                                ] if parte
                                            ),
                                            size=12,
                                            color=ft.Colors.BLUE_700,
                                            visible=bool(
                                                item.get("brochuras", 0)
                                                or item.get("folhetos", 0)
                                                or item.get("outras_publicacoes", 0)
                                            ),
                                        ),
                                        (
                                            ft.Text(
                                                item["observacao"],
                                                size=12,
                                                color=ft.Colors.GREY_600,
                                            )
                                            if item["observacao"]
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
                                    e, atividade_id
                                ),
                            ),
                        ],
                    ),
                )
            )

        lista_atividades.controls = controls or [
            ft.Text("Nenhuma atividade registrada.", color=ft.Colors.GREY_600)
        ]
        try:
            lista_atividades.update()
        except Exception:
            pass

    editor.content = ft.Column(
        spacing=10,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Editar atividade", size=18, weight=ft.FontWeight.BOLD),
                    ft.IconButton(icon=ft.Icons.CLOSE, on_click=fechar_editor),
                ],
            ),
            edit_data,
            edit_tipo,
            ft.Row(
                controls=[
                    ft.Container(expand=True, content=edit_horas),
                    ft.Container(expand=True, content=edit_minutos),
                ]
            ),
            edit_obs,
            edit_msg,
            ft.FilledButton(
                "Salvar alterações",
                icon=ft.Icons.SAVE_OUTLINED,
                on_click=salvar_edicao,
            ),
        ],
    )
    editor.padding = 16
    editor.border_radius = 18
    editor.bgcolor = ft.Colors.WHITE

    confirmacao.content = ft.Row(
        controls=[
            ft.Text("Excluir este registro?", color=ft.Colors.RED_700),
            ft.TextButton("Cancelar", on_click=cancelar_exclusao),
            ft.FilledButton("Excluir", on_click=confirmar_exclusao),
        ]
    )
    confirmacao.padding = 12
    confirmacao.border_radius = 12
    confirmacao.bgcolor = ft.Colors.RED_50

    barras = []
    for item in atividades.totais_por_mes(hoje.year):
        barras.append(
            ft.Row(
                controls=[
                    ft.Text(MESES[item["mes"] - 1], width=32, size=12),
                    ft.Container(
                        expand=True,
                        content=ft.ProgressBar(
                            value=_progresso(item["minutos"], meta_mes_min),
                        ),
                    ),
                    ft.Text(formatar_minutos(item["minutos"]), width=70, size=12),
                ]
            )
        )

    busca.on_change = lambda _: carregar_atividades()
    filtro_tipo.on_change = lambda _: carregar_atividades()
    carregar_atividades()

    return ft.ListView(
        expand=True,
        padding=16,
        spacing=16,
        controls=[
            ft.Text("Relatórios", size=26, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Acompanhe seu progresso e mantenha seus registros organizados.",
                color=ft.Colors.GREY_600,
            ),
            ft.Container(
                padding=16,
                border_radius=18,
                bgcolor=ft.Colors.SURFACE,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text("Relatório mensal", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(relatorio_mensal, size=13),
                        ft.Button(
                            "Compartilhar",
                            icon=ft.Icons.SHARE,
                            action=ft.ShareText(
                                relatorio_mensal,
                                subject="Relatório mensal - Pioneiro Pro",
                                title="Compartilhar relatório mensal",
                            ),
                        ),
                    ],
                ),
            ),
            ft.Container(
                padding=18,
                border_radius=18,
                bgcolor=ft.Colors.WHITE,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text("Meta do mês", weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"{formatar_minutos(total_mes)} de {formatar_minutos(meta_mes_min)}",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_700,
                        ),
                        ft.ProgressBar(value=_progresso(total_mes, meta_mes_min)),
                        ft.Text(f"{quantidade} atividade(s) neste mês", size=12),
                        ft.Text(
                            f"Brochuras: {publicacoes_mes['brochuras']} • "
                            f"Folhetos: {publicacoes_mes['folhetos']} • "
                            f"Outras: {publicacoes_mes['outras_publicacoes']}",
                            size=12,
                        ),
                    ],
                ),
            ),
            ft.Container(
                padding=18,
                border_radius=18,
                bgcolor=ft.Colors.WHITE,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text("Meta do ano", weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"{formatar_minutos(total_ano)} de {formatar_minutos(meta_ano_min)}",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_700,
                        ),
                        ft.ProgressBar(value=_progresso(total_ano, meta_ano_min)),
                    ],
                ),
            ),
            ft.Text(f"Progresso mensal • {hoje.year}", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                padding=14,
                border_radius=18,
                bgcolor=ft.Colors.WHITE,
                content=ft.Column(spacing=8, controls=barras),
            ),
            editor,
            confirmacao,
            ft.Text("Histórico de atividades", size=18, weight=ft.FontWeight.BOLD),
            ft.Row(
                controls=[
                    ft.Container(expand=True, content=busca),
                    filtro_tipo,
                ]
            ),
            lista_atividades,
        ],
    )
