import flet as ft

from pioneiro_pro.repositories import EstudanteRepository


def estudantes_view(estudantes: EstudanteRepository) -> ft.Control:
    nome = ft.TextField(label="Nome do estudante")
    telefone = ft.TextField(label="Telefone")
    mensagem = ft.Text(size=13)
    lista = ft.Column(spacing=4)

    def carregar() -> None:
        dados = estudantes.listar()
        lista.controls = (
            [
                ft.ListTile(
                    leading=ft.CircleAvatar(
                        content=ft.Text(item["nome"][:1].upper()),
                    ),
                    title=ft.Text(item["nome"]),
                    subtitle=ft.Text(item["telefone"] or "Sem telefone"),
                    trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                )
                for item in dados
            ]
            if dados
            else [
                ft.Container(
                    padding=16,
                    content=ft.Text(
                        "Nenhum estudante cadastrado.",
                        color=ft.Colors.GREY_600,
                    ),
                )
            ]
        )

    def adicionar(_):
        if not (nome.value or "").strip():
            mensagem.value = "Informe o nome do estudante."
            mensagem.color = ft.Colors.RED
            mensagem.update()
            return

        estudantes.criar(nome.value or "", telefone.value or "")
        nome.value = ""
        telefone.value = ""
        mensagem.value = "Estudante adicionado."
        mensagem.color = ft.Colors.GREEN_700
        carregar()
        nome.update()
        telefone.update()
        mensagem.update()
        lista.update()

    carregar()

    return ft.ListView(
        expand=True,
        padding=16,
        spacing=14,
        controls=[
            ft.Text("Estudantes", size=26, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Cadastre e acompanhe seus estudos bíblicos.",
                color=ft.Colors.GREY_600,
            ),
            ft.Container(
                padding=16,
                border_radius=16,
                bgcolor=ft.Colors.WHITE,
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
            ft.Text("Lista", size=18, weight=ft.FontWeight.BOLD),
            lista,
        ],
    )
