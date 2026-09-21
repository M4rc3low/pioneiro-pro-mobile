import flet as ft


def configuracoes_view() -> ft.Control:
    return ft.ListView(
        expand=True,
        padding=16,
        spacing=16,
        controls=[
            ft.Text("Configurações", size=26, weight=ft.FontWeight.BOLD),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.DARK_MODE_OUTLINED),
                title=ft.Text("Tema"),
                subtitle=ft.Text("Personalização de tema será adicionada aqui."),
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.BACKUP_OUTLINED),
                title=ft.Text("Backup"),
                subtitle=ft.Text("Exportação e restauração serão adicionadas aqui."),
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.INFO_OUTLINE),
                title=ft.Text("Pioneiro Pro"),
                subtitle=ft.Text("Versão 0.1.0 • Python + Flet"),
            ),
        ],
    )
