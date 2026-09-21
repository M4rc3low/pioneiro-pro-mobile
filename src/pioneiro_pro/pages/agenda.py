from datetime import date

import flet as ft

from pioneiro_pro.repositories import EstudanteRepository, VisitaRepository


def agenda_view(
    visitas: VisitaRepository,
    estudantes: EstudanteRepository,
) -> ft.Control:
    editing_id: dict[str, int | None] = {"value": None}

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
    observacao = ft.TextField(
        label="Observação",
        multiline=True,
        min_lines=2,
        max_lines=4,
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
    mensagem = ft.Text(size=13)
    lista = ft.Column(spacing=8)
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
        titulo_form.value = "Novo compromisso"
        botao_salvar.text = "Adicionar à agenda"
        for control in [estudante, data, horario, tipo, observacao, lembrete, titulo_form, botao_salvar]:
            control.update()

    def carregar() -> None:
        itens = visitas.listar()
        controls: list[ft.Control] = []

        for item in itens:
            concluida = bool(item["concluida"])
            nome = item["estudante_nome"] or "Sem estudante vinculado"
            descricao = f'{item["data"]} {item["horario"]}'.strip()
            if item["observacao"]:
                descricao += f' • {item["observacao"]}'

            def alternar(_, visita_id=item["id"], atual=concluida):
                visitas.marcar_concluida(visita_id, not atual)
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
                titulo_form.value = "Editar compromisso"
                botao_salvar.text = "Salvar alterações"
                for control in [
                    estudante,
                    data,
                    horario,
                    tipo,
                    observacao,
                    lembrete,
                    titulo_form,
                    botao_salvar,
                ]:
                    control.update()

            def excluir(_, visita_id=item["id"]):
                visitas.excluir(visita_id)
                carregar()
                lista.update()

            controls.append(
                ft.Container(
                    padding=10,
                    border_radius=14,
                    bgcolor=ft.Colors.WHITE,
                    content=ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Checkbox(
                                value=concluida,
                                on_change=alternar,
                            ),
                            ft.Container(
                                expand=True,
                                content=ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(
                                            f'{item["tipo"].replace("_", " ").title()} • {nome}',
                                            weight=ft.FontWeight.BOLD,
                                            color=(
                                                ft.Colors.GREY_500
                                                if concluida
                                                else ft.Colors.BLACK
                                            ),
                                        ),
                                        ft.Text(
                                            descricao,
                                            size=12,
                                            color=ft.Colors.GREY_600,
                                        ),
                                    ],
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                tooltip="Editar",
                                on_click=editar,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Excluir",
                                on_click=excluir,
                            ),
                        ],
                    ),
                )
            )

        lista.controls = controls or [
            ft.Container(
                padding=16,
                content=ft.Text(
                    "Nenhum compromisso na agenda.",
                    color=ft.Colors.GREY_600,
                ),
            )
        ]

    def salvar(_):
        if not (data.value or "").strip():
            mensagem.value = "Informe a data."
            mensagem.color = ft.Colors.RED
            mensagem.update()
            return

        estudante_id = int(estudante.value) if estudante.value else None

        if editing_id["value"] is None:
            visitas.criar(
                estudante_id=estudante_id,
                data=(data.value or "").strip(),
                horario=(horario.value or "").strip(),
                tipo=tipo.value or "estudo",
                observacao=observacao.value or "",
                lembrar_minutos_antes=int(lembrete.value or 30),
            )
            mensagem.value = "Compromisso adicionado."
        else:
            visitas.atualizar(
                visita_id=int(editing_id["value"]),
                estudante_id=estudante_id,
                data=(data.value or "").strip(),
                horario=(horario.value or "").strip(),
                tipo=tipo.value or "estudo",
                observacao=observacao.value or "",
                lembrar_minutos_antes=int(lembrete.value or 30),
            )
            mensagem.value = "Compromisso atualizado."

        mensagem.color = ft.Colors.GREEN_700
        mensagem.update()
        limpar_form()
        carregar()
        lista.update()

    botao_salvar.on_click = salvar
    carregar()

    return ft.ListView(
        expand=True,
        padding=16,
        spacing=16,
        controls=[
            ft.Text("Agenda", size=26, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Organize estudos, revisitas, ligações e outros compromissos.",
                color=ft.Colors.GREY_600,
            ),
            ft.Container(
                padding=16,
                border_radius=18,
                bgcolor=ft.Colors.WHITE,
                content=ft.Column(
                    spacing=12,
                    controls=[
                        titulo_form,
                        estudante,
                        ft.Row(
                            controls=[
                                ft.Container(expand=True, content=data),
                                ft.Container(expand=True, content=horario),
                            ]
                        ),
                        tipo,
                        lembrete,
                        observacao,
                        mensagem,
                        ft.Row(
                            controls=[
                                ft.Container(expand=True, content=botao_salvar),
                                ft.TextButton(
                                    "Limpar",
                                    on_click=lambda _: limpar_form(),
                                ),
                            ]
                        ),
                    ],
                ),
            ),
            ft.Text("Compromissos", size=18, weight=ft.FontWeight.BOLD),
            lista,
        ],
    )
