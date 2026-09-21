import flet as ft

from pioneiro_pro.repositories import EstudanteRepository


def estudantes_view(estudantes: EstudanteRepository, on_open) -> ft.Control:
    nome = ft.TextField(label="Nome do estudante")
    telefone = ft.TextField(label="Telefone")
    mensagem = ft.Text(size=13)
    busca = ft.TextField(
        label="Buscar",
        hint_text="Nome, telefone, endereço ou observação",
        prefix_icon=ft.Icons.SEARCH,
    )
    filtro_status = ft.Dropdown(
        label="Status",
        value="todos",
        width=150,
        options=[
            ft.DropdownOption(key="todos", text="Todos"),
            ft.DropdownOption(key="ativo", text="Ativos"),
            ft.DropdownOption(key="pausado", text="Pausados"),
            ft.DropdownOption(key="encerrado", text="Encerrados"),
        ],
    )
    lista = ft.Column(spacing=4)

    def carregar() -> None:
        status = None if filtro_status.value == "todos" else filtro_status.value
        dados = estudantes.buscar(busca.value or "", status)
        lista.controls = (
            [
                ft.ListTile(
                    leading=ft.CircleAvatar(
                        content=ft.Text(item["nome"][:1].upper()),
                    ),
                    title=ft.Text(item["nome"]),
                    subtitle=ft.Text(
                        " • ".join(
                            parte
                            for parte in [
                                item["telefone"] or "",
                                (item["status"] or "ativo").title(),
                            ]
                            if parte
                        )
                    ),
                    trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                    on_click=lambda _, estudante_id=item["id"]: on_open(estudante_id),
                )
                for item in dados
            ]
            if dados
            else [
                ft.Container(
                    padding=16,
                    content=ft.Text(
                        "Nenhum estudante encontrado.",
                        color=ft.Colors.GREY_600,
                    ),
                )
            ]
        )
        try:
            lista.update()
        except Exception:
            pass

    def adicionar(_):
        if not (nome.value or "").strip():
            mensagem.value = "Informe o nome do estudante."
            mensagem.color = ft.Colors.RED
            mensagem.update()
            return

        novo_id = estudantes.criar(nome.value or "", telefone.value or "")
        nome.value = ""
        telefone.value = ""
        mensagem.value = "Estudante adicionado."
        mensagem.color = ft.Colors.GREEN_700
        nome.update()
        telefone.update()
        mensagem.update()
        on_open(novo_id)

    busca.on_change = lambda _: carregar()
    filtro_status.on_change = lambda _: carregar()
    carregar()

    return ft.ListView(
        expand=True,
        padding=16,
        spacing=14,
        controls=[
            ft.Text("Estudantes", size=26, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Cadastre, encontre e acompanhe seus estudos bíblicos.",
                color=ft.Colors.GREY_600,
            ),
            ft.Container(
                padding=16,
                border_radius=16,
                bgcolor=ft.Colors.SURFACE,
                content=ft.Column(
                    controls=[
                        nome,
                        telefone,
                        mensagem,
                        ft.FilledButton(
                            "Adicionar estudante",
                            icon=ft.Icons.PERSON_ADD_OUTLINED,
                            on_click=adicionar,
                        ),
                    ]
                ),
            ),
            ft.Row(
                controls=[
                    ft.Container(expand=True, content=busca),
                    filtro_status,
                ]
            ),
            ft.Text("Meus estudantes", size=18, weight=ft.FontWeight.BOLD),
            lista,
        ],
    )
