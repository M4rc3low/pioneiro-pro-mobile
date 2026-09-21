import flet as ft

from pioneiro_pro.repositories import EstudanteRepository, VisitaRepository


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
        return ft.Column(
            expand=True,
            controls=[
                ft.Text("Estudante não encontrado.", size=20),
                ft.TextButton("Voltar", on_click=lambda _: on_back()),
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
    localizacao_status = ft.Text(
        (
            f'Localização salva: {float(estudante["latitude"]):.5f}, '
            f'{float(estudante["longitude"]):.5f}'
            if estudante.get("latitude") is not None
            and estudante.get("longitude") is not None
            else "Localização ainda não salva."
        ),
        size=12,
        color=ft.Colors.GREY_600,
    )
    mensagem = ft.Text(size=13)
    confirmar_exclusao = ft.Row(visible=False)

    def salvar(_):
        if not (nome.value or "").strip():
            mensagem.value = "O nome não pode ficar vazio."
            mensagem.color = ft.Colors.RED
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
        mensagem.color = ft.Colors.GREEN_700
        mensagem.update()

    async def salvar_localizacao(_):
        try:
            await geolocator.request_permission()
            posicao = await geolocator.get_current_position()
            estudantes.atualizar_localizacao(
                estudante_id,
                float(posicao.latitude),
                float(posicao.longitude),
                int(raio_alerta.value or 200),
            )
            alerta_proximidade.value = True
            localizacao_status.value = (
                f"Localização salva: {float(posicao.latitude):.5f}, "
                f"{float(posicao.longitude):.5f}"
            )
            localizacao_status.color = ft.Colors.GREEN_700
            alerta_proximidade.update()
            localizacao_status.update()
            mensagem.value = "Localização salva. O Pioneiro Pro poderá avisar quando você estiver por perto."
            mensagem.color = ft.Colors.GREEN_700
            mensagem.update()
        except Exception as exc:
            mensagem.value = f"Não foi possível obter a localização: {exc}"
            mensagem.color = ft.Colors.RED
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
    historico_controls = []
    for item in historico[:10]:
        concluida = bool(item["concluida"])
        historico_controls.append(
            ft.ListTile(
                leading=ft.Icon(
                    ft.Icons.CHECK_CIRCLE if concluida else ft.Icons.EVENT_OUTLINED,
                    color=ft.Colors.GREEN_700 if concluida else ft.Colors.BLUE_700,
                ),
                title=ft.Text(item["tipo"].replace("_", " ").title()),
                subtitle=ft.Text(
                    f'{item["data"]} {item["horario"]}'.strip()
                    + (f' • {item["observacao"]}' if item["observacao"] else "")
                ),
            )
        )

    if not historico_controls:
        historico_controls.append(
            ft.Text(
                "Ainda não há visitas ou revisitas registradas.",
                color=ft.Colors.GREY_600,
            )
        )

    confirmar_exclusao.controls = [
        ft.Text("Excluir definitivamente?", color=ft.Colors.RED_700),
        ft.TextButton("Cancelar", on_click=cancelar_exclusao),
        ft.FilledButton("Excluir", on_click=excluir),
    ]

    return ft.ListView(
        expand=True,
        padding=16,
        spacing=14,
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
            ft.Container(
                padding=16,
                border_radius=18,
                bgcolor=ft.Colors.WHITE,
                content=ft.Column(
                    spacing=12,
                    controls=[
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
                        ft.Divider(),
                        ft.Text(
                            "Localização e proximidade",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            "Salve a localização quando estiver no local da visita. "
                            "Ela fica apenas no banco local do aplicativo.",
                            size=12,
                            color=ft.Colors.GREY_600,
                        ),
                        raio_alerta,
                        alerta_proximidade,
                        localizacao_status,
                        ft.OutlinedButton(
                            "Salvar minha localização atual",
                            icon=ft.Icons.MY_LOCATION,
                            on_click=salvar_localizacao,
                        ),
                        observacao,
                        mensagem,
                        ft.FilledButton(
                            "Salvar alterações",
                            icon=ft.Icons.SAVE_OUTLINED,
                            on_click=salvar,
                        ),
                    ],
                ),
            ),
            ft.Text("Histórico de visitas", size=18, weight=ft.FontWeight.BOLD),
            *historico_controls,
            ft.Divider(),
            ft.TextButton(
                "Excluir estudante",
                icon=ft.Icons.DELETE_OUTLINE,
                on_click=pedir_exclusao,
            ),
            confirmar_exclusao,
        ],
    )
