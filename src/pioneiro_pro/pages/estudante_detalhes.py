import flet as ft

from pioneiro_pro.repositories import EstudanteRepository, VisitaRepository


def estudante_detalhes_view(
    estudante_id: int,
    estudantes: EstudanteRepository,
    visitas: VisitaRepository,
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
            },
        )
        mensagem.value = "Perfil atualizado."
        mensagem.color = ft.Colors.GREEN_700
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
