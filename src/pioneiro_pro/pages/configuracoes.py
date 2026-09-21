from datetime import date

import flet as ft

from pioneiro_pro import __version__

from pioneiro_pro.repositories import ConfiguracaoRepository
from pioneiro_pro.services import (
    BackupService,
    ExportacaoService,
    LocalSecurityService,
    background_location_granted,
    get_current_position_with_permission,
)
from pioneiro_pro.ui import (
    ACCENT,
    DANGER,
    SUCCESS,
    action_tile,
    icon_badge,
    page_header,
    panel,
    section_header,
)


def configuracoes_view(
    page: ft.Page,
    configuracoes: ConfiguracaoRepository,
    backup: BackupService,
    exportacao: ExportacaoService,
    geolocator,
    seguranca_local: LocalSecurityService,
    on_restored,
) -> ft.Control:
    config = configuracoes.todas()

    nome = ft.TextField(label="Seu nome", value=config["nome_pioneiro"])
    congregacao = ft.TextField(label="Congregação", value=config["congregacao"])
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
        value=config.get("proximidade_ativa", "0") == "1",
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
    bloqueio_local = ft.Switch(
        label="Bloquear ao abrir com biometria/PIN",
        value=config.get("bloqueio_local", "0") == "1",
    )
    mensagem = ft.Text(size=12)

    def set_mensagem(texto: str, sucesso: bool = True) -> None:
        mensagem.value = texto
        mensagem.color = SUCCESS if sucesso else DANGER
        mensagem.update()

    async def abrir_configuracoes_localizacao(_=None):
        page.pop_dialog()
        await geolocator.open_app_settings()

    def manter_apenas_em_primeiro_plano(_=None):
        page.pop_dialog()
        set_mensagem(
            "Proximidade ativada. Para avisos fora da tela, permita localização "
            "o tempo todo nas configurações do aparelho."
        )

    def mostrar_orientacao_background() -> None:
        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Permitir localização em segundo plano"),
                content=ft.Text(
                    "Para tentar avisar quando o Pioneiro Pro não estiver na tela, "
                    "abra as configurações do aplicativo e escolha a opção de localização "
                    "que permite acesso o tempo todo. O sistema operacional pode limitar "
                    "esse funcionamento quando o app é encerrado completamente."
                ),
                actions=[
                    ft.TextButton(
                        "Agora não",
                        on_click=manter_apenas_em_primeiro_plano,
                    ),
                    ft.FilledButton(
                        "Abrir configurações",
                        on_click=abrir_configuracoes_localizacao,
                    ),
                ],
            )
        )

    async def confirmar_ativacao_proximidade(_=None):
        page.pop_dialog()
        resultado = await get_current_position_with_permission(geolocator)

        if not resultado.ok:
            proximidade_ativa.value = False
            proximidade_ativa.update()

            if resultado.code == "service_disabled":
                set_mensagem(
                    "Ative a localização do aparelho para usar avisos por proximidade.",
                    False,
                )
                await geolocator.open_location_settings()
                return

            if resultado.code == "permission_permanently_denied":
                set_mensagem(
                    "A permissão de localização está bloqueada nas configurações do app.",
                    False,
                )
                await geolocator.open_app_settings()
                return

            set_mensagem("Permissão de localização não concedida.", False)
            return

        proximidade_ativa.value = True
        proximidade_ativa.update()
        configuracoes.definir("proximidade_ativa", "1")

        if background_location_granted(resultado.permission):
            set_mensagem("Avisos por proximidade ativados.")
        else:
            mostrar_orientacao_background()

    def cancelar_ativacao_proximidade(_=None):
        page.pop_dialog()
        proximidade_ativa.value = False
        proximidade_ativa.update()

    async def alterar_proximidade(event):
        if not event.control.value:
            configuracoes.definir("proximidade_ativa", "0")
            set_mensagem("Avisos por proximidade desativados.")
            return

        event.control.value = False
        event.control.update()
        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Ativar avisos por proximidade?"),
                content=ft.Text(
                    "O Pioneiro Pro usa a localização do aparelho para comparar sua "
                    "posição com estudantes e revisitas que você salvou. Para avisos "
                    "fora da tela, a localização pode ser usada em segundo plano. "
                    "Esses dados permanecem no aparelho e não são enviados "
                    "automaticamente para um servidor."
                ),
                actions=[
                    ft.TextButton(
                        "Agora não",
                        on_click=cancelar_ativacao_proximidade,
                    ),
                    ft.FilledButton(
                        "Continuar",
                        on_click=confirmar_ativacao_proximidade,
                    ),
                ],
            )
        )

    proximidade_ativa.on_change = alterar_proximidade

    async def alterar_bloqueio_local(event):
        if not event.control.value:
            configuracoes.definir("bloqueio_local", "0")
            set_mensagem("Bloqueio local desativado.")
            return

        suportado = await seguranca_local.is_supported()
        if not suportado:
            event.control.value = False
            event.control.update()
            set_mensagem(
                "Este aparelho não oferece autenticação local compatível.",
                False,
            )
            return

        autenticado = await seguranca_local.authenticate(
            "Confirme sua identidade para ativar o bloqueio do Pioneiro Pro."
        )
        if not autenticado:
            event.control.value = False
            event.control.update()
            set_mensagem("Não foi possível ativar o bloqueio local.", False)
            return

        configuracoes.definir("bloqueio_local", "1")
        set_mensagem("Bloqueio por biometria/PIN ativado.")

    bloqueio_local.on_change = alterar_bloqueio_local

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
        configuracoes.definir(
            "bloqueio_local",
            "1" if bloqueio_local.value else "0",
        )

        page.theme_mode = (
            ft.ThemeMode.DARK if tema_escuro.value else ft.ThemeMode.LIGHT
        )
        page.update()
        set_mensagem("Configurações salvas.")

    async def exportar_backup_json(_):
        try:
            nome_arquivo = f"pioneiro-pro-backup-{date.today().isoformat()}.json"
            destino = await ft.FilePicker().save_file(
                dialog_title="Salvar backup JSON sem senha",
                file_name=nome_arquivo,
                allowed_extensions=["json"],
                src_bytes=backup.exportar_bytes(),
            )
            if destino is not None or page.web:
                set_mensagem(
                    "Backup JSON exportado. Guarde-o em local seguro, pois não possui senha."
                )
        except Exception as exc:
            set_mensagem(f"Não foi possível exportar o backup: {exc}", False)

    def exportar_backup_protegido(_):
        senha = ft.TextField(
            label="Senha do backup",
            password=True,
            can_reveal_password=True,
            autofocus=True,
        )
        confirmar = ft.TextField(
            label="Confirmar senha",
            password=True,
            can_reveal_password=True,
        )
        erro = ft.Text(size=11, color=DANGER)

        async def confirmar_exportacao(_event):
            valor = senha.value or ""
            if len(valor) < 8:
                erro.value = "Use pelo menos 8 caracteres."
                erro.update()
                return
            if valor != (confirmar.value or ""):
                erro.value = "As senhas não coincidem."
                erro.update()
                return

            try:
                conteudo = backup.exportar_protegido_bytes(valor)
                page.pop_dialog()
                nome_arquivo = (
                    f"pioneiro-pro-backup-{date.today().isoformat()}.ppbackup"
                )
                destino = await ft.FilePicker().save_file(
                    dialog_title="Salvar backup protegido",
                    file_name=nome_arquivo,
                    allowed_extensions=["ppbackup"],
                    src_bytes=conteudo,
                )
                if destino is not None or page.web:
                    set_mensagem(
                        "Backup protegido criado. Guarde a senha: ela não pode ser recuperada."
                    )
            except Exception as exc:
                page.pop_dialog()
                set_mensagem(
                    f"Não foi possível criar o backup protegido: {exc}",
                    False,
                )

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Criar backup protegido"),
                content=ft.Column(
                    tight=True,
                    spacing=10,
                    controls=[
                        ft.Text(
                            "O arquivo será criptografado. Use uma senha que você consiga "
                            "lembrar; o Pioneiro Pro não armazena nem recupera essa senha.",
                            size=12,
                        ),
                        senha,
                        confirmar,
                        erro,
                    ],
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                    ft.FilledButton(
                        "Criar backup",
                        icon=ft.Icons.LOCK_OUTLINE,
                        on_click=confirmar_exportacao,
                    ),
                ],
            )
        )

    async def restaurar_backup(_):
        try:
            arquivos = await ft.FilePicker().pick_files(
                dialog_title="Selecionar backup",
                allow_multiple=False,
                allowed_extensions=["ppbackup", "json"],
                with_data=True,
            )
            if not arquivos:
                return

            conteudo = arquivos[0].bytes
            if conteudo is None:
                set_mensagem("Não foi possível ler o arquivo selecionado.", False)
                return

            if not backup.eh_backup_protegido(conteudo):
                backup.restaurar_bytes(conteudo)
                set_mensagem("Backup restaurado. Os dados foram recarregados.")
                on_restored()
                return

            senha = ft.TextField(
                label="Senha do backup",
                password=True,
                can_reveal_password=True,
                autofocus=True,
            )
            erro = ft.Text(size=11, color=DANGER)

            async def confirmar_restauracao(_event):
                try:
                    backup.restaurar_protegido_bytes(
                        conteudo,
                        senha.value or "",
                    )
                    page.pop_dialog()
                    set_mensagem("Backup protegido restaurado com sucesso.")
                    on_restored()
                except ValueError as exc:
                    erro.value = str(exc)
                    erro.update()
                except Exception as exc:
                    page.pop_dialog()
                    set_mensagem(
                        f"Não foi possível restaurar o backup: {exc}",
                        False,
                    )

            page.show_dialog(
                ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Backup protegido"),
                    content=ft.Column(
                        tight=True,
                        spacing=10,
                        controls=[
                            ft.Text(
                                "Informe a senha usada quando este backup foi criado.",
                                size=12,
                            ),
                            senha,
                            erro,
                        ],
                    ),
                    actions=[
                        ft.TextButton(
                            "Cancelar",
                            on_click=lambda _: page.pop_dialog(),
                        ),
                        ft.FilledButton(
                            "Restaurar",
                            icon=ft.Icons.RESTORE,
                            on_click=confirmar_restauracao,
                        ),
                    ],
                )
            )
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

    profile_summary = config.get("congregacao") or "Perfil local do Pioneiro Pro"

    return ft.ListView(
        expand=True,
        padding=18,
        spacing=16,
        controls=[
            page_header(
                "Configurações",
                "Personalize o app, seus dados e a experiência de uso.",
                ft.Icons.TUNE_OUTLINED,
            ),
            panel(
                ft.Row(
                    controls=[
                        ft.Container(
                            width=56,
                            height=56,
                            border_radius=18,
                            bgcolor=ft.Colors.BLUE_700,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(
                                ft.Icons.PERSON_OUTLINED,
                                size=26,
                                color=ft.Colors.WHITE,
                            ),
                        ),
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                spacing=3,
                                controls=[
                                    ft.Text(
                                        config.get("nome_pioneiro") or "Seu perfil",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        profile_summary,
                                        size=12,
                                        color=ft.Colors.GREY_500,
                                    ),
                                ],
                            ),
                        ),
                    ]
                )
            ),
            panel(
                ft.Column(
                    spacing=12,
                    controls=[
                        section_header(
                            "Perfil e metas",
                            subtitle="Informações usadas no dashboard e relatórios.",
                            trailing=icon_badge(ft.Icons.FLAG_OUTLINED),
                        ),
                        nome,
                        congregacao,
                        ft.Row(
                            controls=[
                                ft.Container(expand=True, content=meta_mes),
                                ft.Container(expand=True, content=meta_ano),
                            ]
                        ),
                    ],
                )
            ),
            panel(
                ft.Column(
                    spacing=12,
                    controls=[
                        section_header(
                            "Localização e proximidade",
                            subtitle="Controle os avisos de estudantes e revisitas próximas.",
                            trailing=icon_badge(
                                ft.Icons.LOCATION_ON_OUTLINED,
                                color=ft.Colors.PURPLE_500,
                            ),
                        ),
                        proximidade_ativa,
                        raio_padrao,
                        ft.Text(
                            "Ao ativar, o app pode usar sua localização em segundo plano "
                            "para comparar sua posição com locais que você cadastrou. "
                            "As coordenadas permanecem no aparelho.",
                            size=11,
                            color=ft.Colors.GREY_500,
                        ),
                    ],
                )
            ),
            panel(
                ft.Column(
                    spacing=8,
                    controls=[
                        section_header(
                            "Aparência",
                            subtitle="Escolha o tema que fica melhor no seu aparelho.",
                            trailing=icon_badge(
                                ft.Icons.DARK_MODE_OUTLINED,
                                color=ft.Colors.ORANGE_600,
                            ),
                        ),
                        tema_escuro,
                    ],
                )
            ),
            mensagem,
            ft.FilledButton(
                "Salvar configurações",
                icon=ft.Icons.SAVE_OUTLINED,
                on_click=salvar,
            ),
            section_header(
                "Dados e segurança",
                subtitle="Proteja e mova seus dados quando precisar.",
            ),
            panel(
                ft.Column(
                    spacing=8,
                    controls=[
                        section_header(
                            "Proteção do aplicativo",
                            subtitle="Use a segurança já configurada no seu aparelho.",
                            trailing=icon_badge(
                                ft.Icons.LOCK_OUTLINE,
                                color=ft.Colors.TEAL_500,
                            ),
                        ),
                        bloqueio_local,
                        ft.Text(
                            "Quando ativado, o Pioneiro Pro exige biometria, PIN, "
                            "senha ou padrão do próprio aparelho para abrir.",
                            size=11,
                            color=ft.Colors.GREY_500,
                        ),
                    ],
                )
            ),
            action_tile(
                "Criar backup protegido",
                "Criptografa estudantes, agenda e registros com uma senha escolhida por você.",
                ft.Icons.LOCK_OUTLINE,
                exportar_backup_protegido,
                color=SUCCESS,
            ),
            action_tile(
                "Restaurar backup",
                "Aceita backup protegido (.ppbackup) e o JSON antigo.",
                ft.Icons.RESTORE,
                restaurar_backup,
                color=ft.Colors.PURPLE_500,
            ),
            action_tile(
                "Exportar backup JSON sem senha",
                "Compatibilidade com versões antigas. O conteúdo fica legível no arquivo.",
                ft.Icons.WARNING_AMBER_OUTLINED,
                exportar_backup_json,
                color=ft.Colors.ORANGE_600,
            ),
            section_header(
                "Exportação",
                subtitle="Leve seus dados para outros aplicativos.",
            ),
            action_tile(
                "Exportar relatório CSV",
                "Compatível com Excel, Google Sheets e similares.",
                ft.Icons.TABLE_VIEW_OUTLINED,
                exportar_csv,
            ),
            action_tile(
                "Exportar resumo TXT",
                "Arquivo simples com seu resumo e registros recentes.",
                ft.Icons.DESCRIPTION_OUTLINED,
                exportar_resumo,
                color=ft.Colors.ORANGE_600,
            ),
            panel(
                ft.Row(
                    controls=[
                        icon_badge(ft.Icons.INFO_OUTLINE, box_size=38),
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        "Pioneiro Pro",
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"Versão {__version__} • Python + Flet",
                                        size=11,
                                        color=ft.Colors.GREY_500,
                                    ),
                                ],
                            ),
                        ),
                        ft.Text(
                            "Local-first",
                            size=11,
                            color=ACCENT,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ]
                ),
                padding=14,
            ),
            ft.Container(height=6),
        ],
    )
