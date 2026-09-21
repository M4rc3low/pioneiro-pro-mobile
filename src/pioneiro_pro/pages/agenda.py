from datetime import date

import flet as ft

from pioneiro_pro.repositories import EstudanteRepository, VisitaRepository
from pioneiro_pro.services import get_current_position_with_permission
from pioneiro_pro.ui import (
    ACCENT,
    DANGER,
    SUCCESS,
    WARNING,
    empty_state,
    icon_badge,
    page_header,
    panel,
    section_header,
    status_pill,
)


TIPO_LABELS = {
    "estudo": ("Estudo bíblico", ft.Icons.MENU_BOOK_OUTLINED, ACCENT),
    "revisita": ("Revisita", ft.Icons.REPLAY_OUTLINED, ft.Colors.PURPLE_500),
    "ligacao": ("Ligação", ft.Icons.CALL_OUTLINED, SUCCESS),
    "outro": ("Outro", ft.Icons.EVENT_NOTE_OUTLINED, WARNING),
}


def agenda_view(
    visitas: VisitaRepository,
    estudantes: EstudanteRepository,
    geolocator,
    on_geofence_changed=lambda: None,
) -> ft.Control:
    editing_id: dict[str, int | None] = {"value": None}
    localizacao: dict[str, float | None] = {"lat": None, "lon": None}

    estudante = ft.Dropdown(
        label="Estudante",
        options=[
            ft.DropdownOption(key=str(item["id"]), text=item["nome"])
            for item in estudantes.listar()
        ],
    )
    data = ft.TextField(label="Data", value=date.today().isoformat())
    horario = ft.TextField(label="Horário", hint_text="Ex.: 19:30")
    tipo = ft.Dropdown(
        label="Tipo",
        value="estudo",
        options=[
            ft.DropdownOption(key="estudo", text="Estudo bíblico"),
            ft.DropdownOption(key="revisita", text="Revisita"),
            ft.DropdownOption(key="ligacao", text="Ligação"),
            ft.DropdownOption(key="outro", text="Outro"),
        ],
    )
    lembrete = ft.Dropdown(
        label="Lembrar antes",
        value="30",
        options=[
            ft.DropdownOption(key="0", text="No horário"),
            ft.DropdownOption(key="10", text="10 minutos antes"),
            ft.DropdownOption(key="30", text="30 minutos antes"),
            ft.DropdownOption(key="60", text="1 hora antes"),
            ft.DropdownOption(key="1440", text="1 dia antes"),
        ],
    )
    raio_proximidade = ft.Dropdown(
        label="Raio do aviso por proximidade",
        value="200",
        options=[
            ft.DropdownOption(key="100", text="100 m"),
            ft.DropdownOption(key="200", text="200 m"),
            ft.DropdownOption(key="300", text="300 m"),
            ft.DropdownOption(key="500", text="500 m"),
            ft.DropdownOption(key="1000", text="1 km"),
        ],
    )
    observacao = ft.TextField(
        label="Observação",
        multiline=True,
        min_lines=2,
        max_lines=4,
    )
    localizacao_status = ft.Text(
        "Usará a localização do estudante, se houver.",
        size=11,
        color=ft.Colors.GREY_500,
    )
    mensagem = ft.Text(size=12)

    lista = ft.Column(spacing=10)
    titulo_form = ft.Text("Novo compromisso", size=18, weight=ft.FontWeight.BOLD)
    botao_salvar = ft.FilledButton("Adicionar à agenda", icon=ft.Icons.ADD)

    def limpar_form() -> None:
        editing_id["value"] = None
        estudante.value = None
        data.value = date.today().isoformat()
        horario.value = ""
        tipo.value = "estudo"
        observacao.value = ""
        lembrete.value = "30"
        raio_proximidade.value = "200"
        localizacao["lat"] = None
        localizacao["lon"] = None
        localizacao_status.value = "Usará a localização do estudante, se houver."
        localizacao_status.color = ft.Colors.GREY_500
        titulo_form.value = "Novo compromisso"
        botao_salvar.text = "Adicionar à agenda"
        mensagem.value = ""

        for control in [
            estudante,
            data,
            horario,
            tipo,
            observacao,
            lembrete,
            raio_proximidade,
            localizacao_status,
            titulo_form,
            botao_salvar,
            mensagem,
        ]:
            control.update()

    def formatar_data(valor: str) -> tuple[str, str]:
        try:
            dt = date.fromisoformat(valor)
            return f"{dt.day:02d}", f"{dt.month:02d}"
        except ValueError:
            return "--", "--"

    def carregar() -> None:
        itens = visitas.listar()
        controls: list[ft.Control] = []

        for item in itens:
            concluida = bool(item["concluida"])
            nome = item["estudante_nome"] or "Sem estudante vinculado"
            tipo_label, tipo_icon, tipo_color = TIPO_LABELS.get(
                item["tipo"],
                (item["tipo"].title(), ft.Icons.EVENT_NOTE_OUTLINED, WARNING),
            )
            dia, mes = formatar_data(item["data"])

            detalhes = [
                item["horario"] or "Sem horário",
                nome,
            ]
            if item["observacao"]:
                detalhes.append(item["observacao"])

            def alternar(_, visita_id=item["id"], atual=concluida):
                visitas.marcar_concluida(visita_id, not atual)
                on_geofence_changed()
                carregar()
                lista.update()

            def editar(_, visita=item):
                editing_id["value"] = visita["id"]
                estudante.value = (
                    str(visita["estudante_id"])
                    if visita["estudante_id"] is not None
                    else None
                )
                data.value = visita["data"]
                horario.value = visita["horario"]
                tipo.value = visita["tipo"]
                observacao.value = visita["observacao"]
                lembrete.value = str(visita.get("lembrar_minutos_antes") or 30)
                raio_proximidade.value = str(visita.get("raio_alerta_m") or 200)
                localizacao["lat"] = visita.get("latitude")
                localizacao["lon"] = visita.get("longitude")
                localizacao_status.value = (
                    "Localização específica salva para este compromisso."
                    if visita.get("latitude") is not None
                    and visita.get("longitude") is not None
                    else "Usará a localização do estudante, se houver."
                )
                titulo_form.value = "Editar compromisso"
                botao_salvar.text = "Salvar alterações"

                for control in [
                    estudante,
                    data,
                    horario,
                    tipo,
                    observacao,
                    lembrete,
                    raio_proximidade,
                    localizacao_status,
                    titulo_form,
                    botao_salvar,
                ]:
                    control.update()

            def excluir(_, visita_id=item["id"]):
                visitas.excluir(visita_id)
                on_geofence_changed()
                carregar()
                lista.update()

            status = (
                status_pill(
                    "Concluído",
                    color=SUCCESS,
                    icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                )
                if concluida
                else status_pill(
                    "Pendente",
                    color=WARNING,
                    icon=ft.Icons.SCHEDULE_OUTLINED,
                )
            )

            controls.append(
                panel(
                    ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=50,
                                height=58,
                                border_radius=16,
                                bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Column(
                                    spacing=0,
                                    tight=True,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text(
                                            dia,
                                            size=19,
                                            weight=ft.FontWeight.BOLD,
                                            color=tipo_color,
                                        ),
                                        ft.Text(
                                            mes,
                                            size=10,
                                            color=ft.Colors.GREY_500,
                                        ),
                                    ],
                                ),
                            ),
                            ft.Container(
                                expand=True,
                                content=ft.Column(
                                    spacing=4,
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    tipo_icon,
                                                    size=17,
                                                    color=tipo_color,
                                                ),
                                                ft.Container(
                                                    expand=True,
                                                    content=ft.Text(
                                                        tipo_label,
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                ),
                                                status,
                                            ]
                                        ),
                                        ft.Text(
                                            " • ".join(detalhes),
                                            size=11,
                                            color=ft.Colors.GREY_500,
                                            max_lines=2,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                    ],
                                ),
                            ),
                            ft.PopupMenuButton(
                                icon=ft.Icons.MORE_VERT,
                                items=[
                                    ft.PopupMenuItem(
                                        content=ft.Text(
                                            "Marcar como pendente"
                                            if concluida
                                            else "Marcar como concluído"
                                        ),
                                        on_click=alternar,
                                    ),
                                    ft.PopupMenuItem(
                                        content=ft.Text("Editar"),
                                        on_click=editar,
                                    ),
                                    ft.PopupMenuItem(
                                        content=ft.Text("Excluir"),
                                        on_click=excluir,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    padding=14,
                    radius=20,
                )
            )

        lista.controls = (
            controls
            if controls
            else [
                empty_state(
                    ft.Icons.EVENT_AVAILABLE_OUTLINED,
                    "Agenda livre",
                    "Adicione um estudo, revisita, ligação ou outro compromisso.",
                )
            ]
        )

    async def salvar_localizacao(_):
        resultado = await get_current_position_with_permission(geolocator)

        if not resultado.ok:
            if resultado.code == "service_disabled":
                mensagem.value = "Ative a localização do aparelho para salvar este ponto."
                mensagem.color = WARNING
                mensagem.update()
                await geolocator.open_location_settings()
                return

            if resultado.code == "permission_permanently_denied":
                mensagem.value = (
                    "A permissão de localização está bloqueada. "
                    "Abra as configurações do app e permita o acesso."
                )
                mensagem.color = WARNING
                mensagem.update()
                await geolocator.open_app_settings()
                return

            mensagem.value = "Permissão de localização não concedida."
            mensagem.color = DANGER
            mensagem.update()
            return

        posicao = resultado.position
        localizacao["lat"] = float(posicao.latitude)
        localizacao["lon"] = float(posicao.longitude)
        localizacao_status.value = "Localização específica salva neste compromisso."
        localizacao_status.color = SUCCESS
        localizacao_status.update()
        mensagem.value = "Localização salva para este compromisso."
        mensagem.color = SUCCESS
        mensagem.update()

    def salvar(_):
        if not (data.value or "").strip():
            mensagem.value = "Informe a data."
            mensagem.color = DANGER
            mensagem.update()
            return

        estudante_id = int(estudante.value) if estudante.value else None

        params = dict(
            estudante_id=estudante_id,
            data=(data.value or "").strip(),
            horario=(horario.value or "").strip(),
            tipo=tipo.value or "estudo",
            observacao=observacao.value or "",
            lembrar_minutos_antes=int(lembrete.value or 30),
            latitude=localizacao["lat"],
            longitude=localizacao["lon"],
            raio_alerta_m=int(raio_proximidade.value or 200),
        )

        if editing_id["value"] is None:
            visitas.criar(**params)
            mensagem.value = "Compromisso adicionado."
        else:
            visitas.atualizar(
                visita_id=int(editing_id["value"]),
                **params,
            )
            mensagem.value = "Compromisso atualizado."

        on_geofence_changed()
        mensagem.color = SUCCESS
        mensagem.update()
        limpar_form()
        carregar()
        lista.update()

    botao_salvar.on_click = salvar
    carregar()

    return ft.ListView(
        expand=True,
        padding=18,
        spacing=16,
        controls=[
            page_header(
                "Agenda",
                "Estudos, revisitas e compromissos em um só lugar.",
                ft.Icons.CALENDAR_MONTH_OUTLINED,
            ),
            panel(
                ft.Column(
                    spacing=12,
                    controls=[
                        section_header(
                            "Novo compromisso",
                            subtitle="Defina horário, lembrete e proximidade.",
                            trailing=icon_badge(ft.Icons.ADD_TASK_OUTLINED),
                        ),
                        titulo_form,
                        estudante,
                        ft.Row(
                            controls=[
                                ft.Container(expand=True, content=data),
                                ft.Container(expand=True, content=horario),
                            ]
                        ),
                        ft.Row(
                            controls=[
                                ft.Container(expand=True, content=tipo),
                                ft.Container(expand=True, content=lembrete),
                            ]
                        ),
                        raio_proximidade,
                        panel(
                            ft.Row(
                                controls=[
                                    icon_badge(
                                        ft.Icons.LOCATION_ON_OUTLINED,
                                        color=ft.Colors.PURPLE_500,
                                        box_size=38,
                                    ),
                                    ft.Container(
                                        expand=True,
                                        content=localizacao_status,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.MY_LOCATION,
                                        tooltip="Salvar localização atual",
                                        on_click=salvar_localizacao,
                                    ),
                                ],
                            ),
                            padding=10,
                            radius=16,
                            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                        ),
                        observacao,
                        mensagem,
                        ft.Row(
                            controls=[
                                ft.Container(expand=True, content=botao_salvar),
                                ft.TextButton(
                                    "Limpar",
                                    icon=ft.Icons.REFRESH,
                                    on_click=lambda _: limpar_form(),
                                ),
                            ]
                        ),
                    ],
                ),
            ),
            section_header(
                "Compromissos",
                subtitle="Toque no menu para editar ou concluir.",
            ),
            lista,
            ft.Container(height=6),
        ],
    )
