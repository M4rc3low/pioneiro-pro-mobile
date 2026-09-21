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
    panel,
    section_header,
    status_pill,
)


STATUS = {
    "ativo": ("Ativo", SUCCESS),
    "pausado": ("Pausado", WARNING),
    "encerrado": ("Encerrado", DANGER),
}


def estudante_detalhes_view(
    estudante_id: int,
    estudantes: EstudanteRepository,
    visitas: VisitaRepository,
    geolocator,
    on_back,
    on_deleted,
) -> ft.Control:
    estudante = estudantes.obter(estudante_id)
    if not estudante:
        return ft.ListView(
            expand=True,
            padding=18,
            controls=[
                empty_state(
                    ft.Icons.PERSON_OFF_OUTLINED,
                    "Estudante não encontrado",
                    "Esse perfil não está mais disponível.",
                    action=ft.TextButton(
                        "Voltar",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda _: on_back(),
                    ),
                )
            ],
        )

    nome = ft.TextField(label="Nome", value=estudante["nome"])
    telefone = ft.TextField(label="Telefone", value=estudante["telefone"])
    endereco = ft.TextField(label="Endereço", value=estudante["endereco"])
    status = ft.Dropdown(
        label="Status",
        value=estudante["status"] or "ativo",
        options=[
            ft.DropdownOption(key="ativo", text="Ativo"),
            ft.DropdownOption(key="pausado", text="Pausado"),
            ft.DropdownOption(key="encerrado", text="Encerrado"),
        ],
    )
    modalidade = ft.Dropdown(
        label="Modalidade",
        value=estudante["modalidade"] or None,
        options=[
            ft.DropdownOption(key="presencial", text="Presencial"),
            ft.DropdownOption(key="online", text="Online"),
            ft.DropdownOption(key="hibrido", text="Híbrido"),
        ],
    )
    horario = ft.Dropdown(
        label="Horário preferido",
        value=estudante["horario_preferido"] or None,
        options=[
            ft.DropdownOption(key="manha", text="Manhã"),
            ft.DropdownOption(key="tarde", text="Tarde"),
            ft.DropdownOption(key="noite", text="Noite"),
        ],
    )
    publicacao = ft.TextField(
        label="Publicação em estudo",
        value=estudante["publicacao_atual"],
    )
    licao = ft.TextField(label="Lição atual", value=estudante["licao_atual"])
    data_inicio = ft.TextField(
        label="Data de início (AAAA-MM-DD)",
        value=estudante["data_inicio"],
    )
    observacao = ft.TextField(
        label="Histórico e observações",
        value=estudante["observacao"],
        multiline=True,
        min_lines=3,
        max_lines=6,
    )
    raio_alerta = ft.Dropdown(
        label="Avisar quando eu estiver a",
        value=str(estudante.get("raio_alerta_m") or 200),
        options=[
            ft.DropdownOption(key="100", text="100 m"),
            ft.DropdownOption(key="200", text="200 m"),
            ft.DropdownOption(key="300", text="300 m"),
            ft.DropdownOption(key="500", text="500 m"),
            ft.DropdownOption(key="1000", text="1 km"),
        ],
    )
    alerta_proximidade = ft.Switch(
        label="Avisar quando eu estiver por perto",
        value=bool(estudante.get("alerta_proximidade", 1)),
    )

    localizacao_salva = (
        estudante.get("latitude") is not None
        and estudante.get("longitude") is not None
    )
    localizacao_status = ft.Text(
        (
            "Localização cadastrada e pronta para avisos."
            if localizacao_salva
            else "Nenhuma localização foi salva ainda."
        ),
        size=11,
        color=SUCCESS if localizacao_salva else ft.Colors.GREY_500,
    )
    mensagem = ft.Text(size=12)
    confirmar_exclusao = ft.Row(visible=False)

    def salvar(_):
        if not (nome.value or "").strip():
            mensagem.value = "O nome não pode ficar vazio."
            mensagem.color = DANGER
            mensagem.update()
            return

        estudantes.atualizar(
            estudante_id,
            {
                "nome": (nome.value or "").strip(),
                "telefone": (telefone.value or "").strip(),
                "endereco": (endereco.value or "").strip(),
                "status": status.value or "ativo",
                "modalidade": modalidade.value or "",
                "horario_preferido": horario.value or "",
                "publicacao_atual": (publicacao.value or "").strip(),
                "licao_atual": (licao.value or "").strip(),
                "data_inicio": (data_inicio.value or "").strip(),
                "observacao": (observacao.value or "").strip(),
                "raio_alerta_m": int(raio_alerta.value or 200),
                "alerta_proximidade": 1 if alerta_proximidade.value else 0,
            },
        )
        mensagem.value = "Perfil atualizado."
        mensagem.color = SUCCESS
        mensagem.update()

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
        estudantes.atualizar_localizacao(
            estudante_id,
            float(posicao.latitude),
            float(posicao.longitude),
            int(raio_alerta.value or 200),
        )
        alerta_proximidade.value = True
        localizacao_status.value = "Localização cadastrada e pronta para avisos."
        localizacao_status.color = SUCCESS
        alerta_proximidade.update()
        localizacao_status.update()
        mensagem.value = "Localização salva com sucesso."
        mensagem.color = SUCCESS
        mensagem.update()

    def pedir_exclusao(_):
        confirmar_exclusao.visible = True
        confirmar_exclusao.update()

    def cancelar_exclusao(_):
        confirmar_exclusao.visible = False
        confirmar_exclusao.update()

    def excluir(_):
        estudantes.excluir(estudante_id)
        on_deleted()

    historico = visitas.listar_por_estudante(estudante_id)
    historico_controls: list[ft.Control] = []

    for item in historico[:10]:
        concluida = bool(item["concluida"])
        historico_controls.append(
            panel(
                ft.Row(
                    controls=[
                        icon_badge(
                            (
                                ft.Icons.CHECK_CIRCLE_OUTLINE
                                if concluida
                                else ft.Icons.EVENT_OUTLINED
                            ),
                            color=SUCCESS if concluida else ACCENT,
                            box_size=38,
                        ),
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
                                        (
                                            f'{item["data"]} {item["horario"]}'.strip()
                                            + (
                                                f' • {item["observacao"]}'
                                                if item["observacao"]
                                                else ""
                                            )
                                        ),
                                        size=11,
                                        color=ft.Colors.GREY_500,
                                    ),
                                ],
                            ),
                        ),
                        status_pill(
                            "Concluído" if concluida else "Pendente",
                            color=SUCCESS if concluida else WARNING,
                        ),
                    ],
                ),
                padding=12,
                radius=18,
            )
        )

    if not historico_controls:
        historico_controls.append(
            empty_state(
                ft.Icons.HISTORY_OUTLINED,
                "Sem histórico ainda",
                "Visitas e revisitas associadas aparecerão aqui.",
            )
        )

    confirmar_exclusao.controls = [
        ft.Container(
            expand=True,
            content=ft.Text(
                "Excluir este estudante definitivamente?",
                color=DANGER,
                weight=ft.FontWeight.BOLD,
            ),
        ),
        ft.TextButton("Cancelar", on_click=cancelar_exclusao),
        ft.FilledButton("Excluir", on_click=excluir),
    ]

    status_text, status_color = STATUS.get(
        estudante["status"] or "ativo",
        ("Ativo", SUCCESS),
    )
    inicial = estudante["nome"][:1].upper() if estudante["nome"] else "?"

    hero = panel(
        ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=64,
                    height=64,
                    border_radius=22,
                    bgcolor=ft.Colors.BLUE_700,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(
                        inicial,
                        size=26,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                ),
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(
                                estudante["nome"],
                                size=22,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                estudante["telefone"] or "Sem telefone cadastrado",
                                size=12,
                                color=ft.Colors.GREY_500,
                            ),
                            status_pill(status_text, color=status_color),
                        ],
                    ),
                ),
            ],
        ),
        padding=18,
    )

    return ft.ListView(
        expand=True,
        padding=18,
        spacing=16,
        controls=[
            ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        tooltip="Voltar",
                        on_click=lambda _: on_back(),
                    ),
                    ft.Text(
                        "Perfil do estudante",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                    ),
                ]
            ),
            hero,
            panel(
                ft.Column(
                    spacing=12,
                    controls=[
                        section_header(
                            "Informações principais",
                            subtitle="Contato, modalidade e andamento.",
                            trailing=icon_badge(ft.Icons.BADGE_OUTLINED),
                        ),
                        nome,
                        telefone,
                        endereco,
                        ft.Row(
                            controls=[
                                ft.Container(expand=True, content=status),
                                ft.Container(expand=True, content=modalidade),
                            ]
                        ),
                        horario,
                        publicacao,
                        licao,
                        data_inicio,
                    ],
                )
            ),
            panel(
                ft.Column(
                    spacing=12,
                    controls=[
                        section_header(
                            "Localização e proximidade",
                            subtitle="Avisos quando você estiver por perto.",
                            trailing=icon_badge(
                                ft.Icons.LOCATION_ON_OUTLINED,
                                color=ft.Colors.PURPLE_500,
                            ),
                        ),
                        raio_alerta,
                        alerta_proximidade,
                        panel(
                            ft.Row(
                                controls=[
                                    icon_badge(
                                        (
                                            ft.Icons.CHECK_CIRCLE_OUTLINE
                                            if localizacao_salva
                                            else ft.Icons.LOCATION_OFF_OUTLINED
                                        ),
                                        color=SUCCESS if localizacao_salva else WARNING,
                                        box_size=38,
                                    ),
                                    ft.Container(
                                        expand=True,
                                        content=localizacao_status,
                                    ),
                                ],
                            ),
                            padding=10,
                            radius=16,
                            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                        ),
                        ft.OutlinedButton(
                            "Salvar localização atual",
                            icon=ft.Icons.MY_LOCATION,
                            on_click=salvar_localizacao,
                        ),
                    ],
                )
            ),
            panel(
                ft.Column(
                    spacing=10,
                    controls=[
                        section_header(
                            "Anotações",
                            subtitle="Observações úteis sobre o acompanhamento.",
                        ),
                        observacao,
                    ],
                )
            ),
            mensagem,
            ft.FilledButton(
                "Salvar alterações",
                icon=ft.Icons.SAVE_OUTLINED,
                on_click=salvar,
            ),
            section_header(
                "Histórico de visitas",
                subtitle="Últimos compromissos associados.",
            ),
            *historico_controls,
            ft.Divider(),
            ft.TextButton(
                "Excluir estudante",
                icon=ft.Icons.DELETE_OUTLINE,
                on_click=pedir_exclusao,
            ),
            confirmar_exclusao,
            ft.Container(height=6),
        ],
    )
