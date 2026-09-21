import flet as ft

from pioneiro_pro.repositories import EstudanteRepository
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


STATUS = {
    "ativo": ("Ativo", SUCCESS),
    "pausado": ("Pausado", WARNING),
    "encerrado": ("Encerrado", DANGER),
}


def estudantes_view(estudantes: EstudanteRepository, on_open) -> ft.Control:
    nome = ft.TextField(label="Nome do estudante")
    telefone = ft.TextField(label="Telefone")
    mensagem = ft.Text(size=12)

    busca = ft.TextField(
        label="Buscar estudante",
        hint_text="Nome, telefone, endereço ou observação",
        prefix_icon=ft.Icons.SEARCH,
    )
    filtro_status = ft.Dropdown(
        label="Status",
        value="todos",
        width=145,
        options=[
            ft.DropdownOption(key="todos", text="Todos"),
            ft.DropdownOption(key="ativo", text="Ativos"),
            ft.DropdownOption(key="pausado", text="Pausados"),
            ft.DropdownOption(key="encerrado", text="Encerrados"),
        ],
    )
    lista = ft.Column(spacing=10)
    contador = ft.Text("", size=12, color=ft.Colors.GREY_500)

    def estudante_card(item: dict) -> ft.Container:
        status_key = item["status"] or "ativo"
        status_text, status_color = STATUS.get(status_key, ("Ativo", SUCCESS))
        inicial = item["nome"][:1].upper() if item["nome"] else "?"

        infos = [
            parte
            for parte in [
                item.get("telefone") or "",
                item.get("endereco") or "",
            ]
            if parte
        ]
        subtitulo = " • ".join(infos) if infos else "Sem contato adicional"

        return panel(
            ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=48,
                        height=48,
                        border_radius=16,
                        bgcolor=ft.Colors.BLUE_700,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Text(
                            inicial,
                            size=19,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            spacing=4,
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Container(
                                            expand=True,
                                            content=ft.Text(
                                                item["nome"],
                                                size=16,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        ),
                                        status_pill(
                                            status_text,
                                            color=status_color,
                                        ),
                                    ]
                                ),
                                ft.Text(
                                    subtitulo,
                                    size=11,
                                    color=ft.Colors.GREY_500,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                        ),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CHEVRON_RIGHT,
                        tooltip="Abrir perfil",
                        on_click=lambda _, estudante_id=item["id"]: on_open(estudante_id),
                    ),
                ],
            ),
            padding=14,
            radius=20,
        )

    def carregar() -> None:
        status = None if filtro_status.value == "todos" else filtro_status.value
        dados = estudantes.buscar(busca.value or "", status)
        contador.value = f"{len(dados)} encontrado(s)"

        lista.controls = (
            [estudante_card(item) for item in dados]
            if dados
            else [
                empty_state(
                    ft.Icons.PERSON_SEARCH_OUTLINED,
                    "Nenhum estudante encontrado",
                    "Ajuste a busca, o filtro ou adicione um novo estudante.",
                )
            ]
        )

        try:
            contador.update()
            lista.update()
        except Exception:
            pass

    def adicionar(_):
        if not (nome.value or "").strip():
            mensagem.value = "Informe o nome do estudante."
            mensagem.color = DANGER
            mensagem.update()
            return

        novo_id = estudantes.criar(nome.value or "", telefone.value or "")
        nome.value = ""
        telefone.value = ""
        mensagem.value = "Estudante adicionado."
        mensagem.color = SUCCESS
        nome.update()
        telefone.update()
        mensagem.update()
        on_open(novo_id)

    busca.on_change = lambda _: carregar()
    filtro_status.on_change = lambda _: carregar()
    carregar()

    return ft.ListView(
        expand=True,
        padding=18,
        spacing=16,
        controls=[
            page_header(
                "Estudantes",
                "Organize contatos, progresso, revisitas e localização.",
                ft.Icons.GROUP_OUTLINED,
            ),
            panel(
                ft.Column(
                    spacing=12,
                    controls=[
                        section_header(
                            "Novo estudante",
                            subtitle="Cadastre o básico e complete o perfil depois.",
                            trailing=icon_badge(
                                ft.Icons.PERSON_ADD_OUTLINED,
                                color=ACCENT,
                            ),
                        ),
                        nome,
                        telefone,
                        mensagem,
                        ft.FilledButton(
                            "Adicionar estudante",
                            icon=ft.Icons.ADD,
                            on_click=adicionar,
                        ),
                    ],
                ),
            ),
            section_header(
                "Meus estudantes",
                subtitle="Encontre rapidamente quem você procura.",
                trailing=contador,
            ),
            ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(expand=True, content=busca),
                    filtro_status,
                ],
            ),
            lista,
            ft.Container(height=6),
        ],
    )
