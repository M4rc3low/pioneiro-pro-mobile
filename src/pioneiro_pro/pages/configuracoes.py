from datetime import date

import flet as ft

from pioneiro_pro.repositories import ConfiguracaoRepository
from pioneiro_pro.services import BackupService, ExportacaoService


def configuracoes_view(
    page: ft.Page,
    configuracoes: ConfiguracaoRepository,
    backup: BackupService,
    exportacao: ExportacaoService,
    on_restored,
) -> ft.Control:
    config = configuracoes.todas()

    nome = ft.TextField(
        label="Seu nome",
        value=config["nome_pioneiro"],
    )
    congregacao = ft.TextField(
        label="Congregação",
        value=config["congregacao"],
    )
    meta_mes = ft.TextField(
        label="Meta mensal (horas)",
        value=config["meta_horas_mes"],
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    meta_ano = ft.TextField(
        label="Meta anual (horas)",
        value=config["meta_horas_ano"],
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    proximidade_ativa = ft.Switch(
        label="Avisos por proximidade",
        value=config.get("proximidade_ativa", "1") == "1",
    )
    raio_padrao = ft.Dropdown(
        label="Raio padrão para novos locais",
        value=config.get("raio_proximidade_padrao", "200"),
        options=[
            ft.DropdownOption(key="100", text="100 m"),
            ft.DropdownOption(key="200", text="200 m"),
            ft.DropdownOption(key="300", text="300 m"),
            ft.DropdownOption(key="500", text="500 m"),
            ft.DropdownOption(key="1000", text="1 km"),
        ],
    )
    tema_escuro = ft.Switch(
        label="Tema escuro",
        value=config["tema"] == "escuro",
    )
    mensagem = ft.Text(size=13)

    def set_mensagem(texto: str, sucesso: bool = True) -> None:
        mensagem.value = texto
        mensagem.color = ft.Colors.GREEN_700 if sucesso else ft.Colors.RED
        mensagem.update()

    def salvar(_):
        try:
            mensal = max(0, int(float(meta_mes.value or 0)))
            anual = max(0, int(float(meta_ano.value or 0)))
        except ValueError:
            set_mensagem("As metas precisam ser números.", False)
            return

        configuracoes.definir("nome_pioneiro", (nome.value or "").strip())
        configuracoes.definir("congregacao", (congregacao.value or "").strip())
        configuracoes.definir("meta_horas_mes", mensal)
        configuracoes.definir("meta_horas_ano", anual)
        configuracoes.definir(
            "proximidade_ativa",
            "1" if proximidade_ativa.value else "0",
        )
        configuracoes.definir(
            "raio_proximidade_padrao",
            raio_padrao.value or "200",
        )
        configuracoes.definir(
            "tema",
            "escuro" if tema_escuro.value else "claro",
        )

        page.theme_mode = (
            ft.ThemeMode.DARK if tema_escuro.value else ft.ThemeMode.LIGHT
        )
        page.update()
        set_mensagem("Configurações salvas.")

    async def exportar_backup(_):
        try:
            nome_arquivo = f"pioneiro-pro-backup-{date.today().isoformat()}.json"
            destino = await ft.FilePicker().save_file(
                dialog_title="Salvar backup",
                file_name=nome_arquivo,
                allowed_extensions=["json"],
                src_bytes=backup.exportar_bytes(),
            )
            if destino is not None or page.web:
                set_mensagem("Backup exportado com sucesso.")
        except Exception as exc:
            set_mensagem(f"Não foi possível exportar o backup: {exc}", False)

    async def restaurar_backup(_):
        try:
            arquivos = await ft.FilePicker().pick_files(
                dialog_title="Selecionar backup",
                allow_multiple=False,
                allowed_extensions=["json"],
                with_data=True,
            )
            if not arquivos:
                return

            conteudo = arquivos[0].bytes
            if conteudo is None:
                set_mensagem("Não foi possível ler o arquivo selecionado.", False)
                return

            backup.restaurar_bytes(conteudo)
            set_mensagem("Backup restaurado. Os dados foram recarregados.")
            on_restored()
        except Exception as exc:
            set_mensagem(f"Backup inválido ou não pôde ser restaurado: {exc}", False)

    async def exportar_csv(_):
        try:
            nome_arquivo = f"pioneiro-pro-relatorio-{date.today().isoformat()}.csv"
            destino = await ft.FilePicker().save_file(
                dialog_title="Salvar relatório",
                file_name=nome_arquivo,
                allowed_extensions=["csv"],
                src_bytes=exportacao.relatorio_csv(),
            )
            if destino is not None or page.web:
                set_mensagem("Relatório CSV exportado.")
        except Exception as exc:
            set_mensagem(f"Não foi possível exportar o relatório: {exc}", False)

    async def exportar_resumo(_):
        try:
            nome_arquivo = f"pioneiro-pro-resumo-{date.today().isoformat()}.txt"
            destino = await ft.FilePicker().save_file(
                dialog_title="Salvar resumo",
                file_name=nome_arquivo,
                allowed_extensions=["txt"],
                src_bytes=exportacao.resumo_txt(),
            )
            if destino is not None or page.web:
                set_mensagem("Resumo exportado.")
        except Exception as exc:
            set_mensagem(f"Não foi possível exportar o resumo: {exc}", False)

    return ft.ListView(
        expand=True,
        padding=16,
        spacing=16,
        controls=[
            ft.Text("Configurações", size=26, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Personalize o Pioneiro Pro e proteja seus dados.",
                color=ft.Colors.GREY_600,
            ),
            ft.Container(
                padding=16,
                border_radius=18,
                bgcolor=ft.Colors.SURFACE,
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Text("Perfil", size=18, weight=ft.FontWeight.BOLD),
                        nome,
                        congregacao,
                    ],
                ),
            ),
            ft.Container(
                padding=16,
                border_radius=18,
                bgcolor=ft.Colors.SURFACE,
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Text("Metas", size=18, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            controls=[
                                ft.Container(expand=True, content=meta_mes),
                                ft.Container(expand=True, content=meta_ano),
                            ]
                        ),
                    ],
                ),
            ),
            ft.Container(
                padding=16,
                border_radius=18,
                bgcolor=ft.Colors.SURFACE,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text("Proximidade", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "O GPS é usado apenas para comparar sua posição com locais que você salvou no próprio aparelho.",
                            size=12,
                            color=ft.Colors.GREY_600,
                        ),
                        proximidade_ativa,
                        raio_padrao,
                    ],
                ),
            ),
            ft.Container(
                padding=16,
                border_radius=18,
                bgcolor=ft.Colors.SURFACE,
                content=ft.Column(
                    controls=[
                        ft.Text("Aparência", size=18, weight=ft.FontWeight.BOLD),
                        tema_escuro,
                    ]
                ),
            ),
            ft.FilledButton(
                "Salvar configurações",
                icon=ft.Icons.SAVE_OUTLINED,
                on_click=salvar,
            ),
            mensagem,
            ft.Divider(),
            ft.Text("Dados e segurança", size=18, weight=ft.FontWeight.BOLD),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.BACKUP_OUTLINED),
                title=ft.Text("Criar backup"),
                subtitle=ft.Text("Salva estudantes, agenda, registros e configurações."),
                on_click=exportar_backup,
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.RESTORE),
                title=ft.Text("Restaurar backup"),
                subtitle=ft.Text("Substitui os dados atuais pelos dados do arquivo."),
                on_click=restaurar_backup,
            ),
            ft.Divider(),
            ft.Text("Exportação", size=18, weight=ft.FontWeight.BOLD),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.TABLE_VIEW_OUTLINED),
                title=ft.Text("Exportar relatório CSV"),
                subtitle=ft.Text("Planilha compatível com Excel e Google Sheets."),
                on_click=exportar_csv,
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.DESCRIPTION_OUTLINED),
                title=ft.Text("Exportar resumo"),
                subtitle=ft.Text("Resumo simples em arquivo de texto."),
                on_click=exportar_resumo,
            ),
            ft.Divider(),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.INFO_OUTLINE),
                title=ft.Text("Pioneiro Pro"),
                subtitle=ft.Text("Versão 0.4.0 • Python + Flet"),
            ),
        ],
    )
