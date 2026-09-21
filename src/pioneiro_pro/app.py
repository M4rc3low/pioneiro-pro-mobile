from __future__ import annotations

import flet as ft
import flet_geolocator as ftg

from pioneiro_pro.database import Database
from pioneiro_pro.pages import (
    agenda_view,
    configuracoes_view,
    dashboard_view,
    estudante_detalhes_view,
    estudantes_view,
    onboarding_view,
    registrar_view,
    relatorios_view,
)
from pioneiro_pro.repositories import (
    AtividadeRepository,
    ConfiguracaoRepository,
    EstudanteRepository,
    VisitaRepository,
)
from pioneiro_pro.services import (
    BackupService,
    CronometroService,
    ExportacaoService,
    LembreteService,
    ProximidadeService,
)
from pioneiro_pro.ui import app_logo


class PioneiroProApp:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.database = Database()
        self.database.initialize()

        self.atividades = AtividadeRepository(self.database)
        self.estudantes = EstudanteRepository(self.database)
        self.visitas = VisitaRepository(self.database)
        self.configuracoes = ConfiguracaoRepository(self.database)

        self.cronometro = CronometroService()
        self.backup = BackupService(self.database)
        self.exportacao = ExportacaoService(self.atividades)
        self.lembretes = LembreteService(self.visitas)
        self.proximidade = ProximidadeService(self.estudantes, self.visitas)
        self.url_launcher = ft.UrlLauncher()
        self.geolocator = None

        self.current_key = "dashboard"
        self.content = ft.Container(expand=True)
        self._lembrete_mostrado_hoje = False

        self.nav = ft.NavigationBar(
            selected_index=0,
            on_change=self._on_nav_change,
            bgcolor=ft.Colors.SURFACE,
            indicator_color=ft.Colors.with_opacity(0.16, ft.Colors.BLUE_600),
            elevation=0,
            label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.HOME_OUTLINED,
                    selected_icon=ft.Icons.HOME,
                    label="Início",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    selected_icon=ft.Icons.ADD_CIRCLE,
                    label="Registrar",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.GROUP_OUTLINED,
                    selected_icon=ft.Icons.GROUP,
                    label="Estudantes",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
                    selected_icon=ft.Icons.CALENDAR_MONTH,
                    label="Agenda",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.BAR_CHART_OUTLINED,
                    selected_icon=ft.Icons.BAR_CHART,
                    label="Relatórios",
                ),
            ],
        )

    def mount(self) -> None:
        config = self.configuracoes.todas()

        self.page.title = "Pioneiro Pro"
        self.page.padding = 0
        self.page.bgcolor = ft.Colors.SURFACE_CONTAINER_LOW
        self.page.theme_mode = (
            ft.ThemeMode.DARK if config["tema"] == "escuro" else ft.ThemeMode.LIGHT
        )
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE_600,
            scaffold_bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        )
        self.page.on_app_lifecycle_state_change = self._on_lifecycle
        self._configurar_geolocalizacao()

        self.page.add(
            ft.SafeArea(
                expand=True,
                content=self.content,
            )
        )

        if config.get("onboarding_concluido") == "1":
            self._ativar_shell()
            self.navigate("dashboard")
            self._mostrar_lembrete_do_dia()
        else:
            self.page.appbar = None
            self.page.navigation_bar = None
            self.current_key = "onboarding"
            self.content.content = onboarding_view(
                self.configuracoes,
                on_finish=self._finalizar_onboarding,
            )
            self.page.update()

    def _configurar_geolocalizacao(self) -> None:
        if self.page.platform == ft.PagePlatform.ANDROID:
            config = ftg.GeolocatorAndroidConfiguration(
                accuracy=ftg.GeolocatorPositionAccuracy.HIGH,
                distance_filter=50,
                interval_duration=ft.Duration(seconds=30),
                foreground_notification_config=ftg.ForegroundNotificationConfiguration(
                    notification_title="Pioneiro Pro",
                    notification_text="Monitorando estudantes e revisitas próximas",
                    notification_channel_name="Localização do Pioneiro Pro",
                    notification_set_ongoing=True,
                ),
            )
        elif self.page.platform == ft.PagePlatform.IOS:
            config = ftg.GeolocatorIosConfiguration(
                accuracy=ftg.GeolocatorPositionAccuracy.HIGH,
                distance_filter=50,
                allow_background_location_updates=True,
                pause_location_updates_automatically=True,
                show_background_location_indicator=True,
            )
        else:
            config = ftg.GeolocatorConfiguration(
                accuracy=ftg.GeolocatorPositionAccuracy.HIGH,
                distance_filter=50,
            )

        self.geolocator = ftg.Geolocator(
            configuration=config,
            on_position_change=self._on_position_change,
            on_error=self._on_location_error,
        )
        self.page.services.append(self.geolocator)

    def _on_location_error(self, event) -> None:
        # A permissão é solicitada quando o usuário salva a localização
        # de um estudante. Até lá, erros de localização são silenciosos.
        return

    def _on_position_change(self, event) -> None:
        config = self.configuracoes.todas()
        if config.get("proximidade_ativa", "1") != "1":
            return

        encontrados = self.proximidade.verificar(
            float(event.position.latitude),
            float(event.position.longitude),
        )
        if not encontrados:
            return

        item = encontrados[0]
        distancia = item["distancia_m"]
        texto = f'{item["nome"]} está a aproximadamente {distancia} m.'

        latitude = float(item["latitude"])
        longitude = float(item["longitude"])
        rota_url = self.proximidade.url_google_maps(latitude, longitude)

        async def abrir_rota(_):
            await self.url_launcher.launch_url(
                rota_url,
                mode=ft.LaunchMode.EXTERNAL_APPLICATION,
            )

        self.page.show_dialog(
            ft.SnackBar(
                content=ft.Text(texto),
                action="Como chegar",
                on_action=abrir_rota,
                show_close_icon=True,
            )
        )

    def _ativar_shell(self) -> None:
        self.page.navigation_bar = self.nav
        self.page.appbar = ft.AppBar(
            bgcolor=ft.Colors.SURFACE,
            elevation=0,
            shadow_color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
            title=ft.Row(
                spacing=10,
                controls=[
                    app_logo(38, 12),
                    ft.Column(
                        spacing=0,
                        controls=[
                            ft.Text(
                                "Pioneiro Pro",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Organização pessoal",
                                size=10,
                                color=ft.Colors.GREY_500,
                            ),
                        ],
                    ),
                ],
            ),
            center_title=False,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    tooltip="Configurações",
                    on_click=lambda _: self.navigate("configuracoes"),
                )
            ],
        )

    def _finalizar_onboarding(self) -> None:
        self._ativar_shell()
        self.navigate("dashboard")
        self._mostrar_lembrete_do_dia()

    def _on_lifecycle(self, event: ft.AppLifecycleStateChangeEvent) -> None:
        if event.state in {
            ft.AppLifecycleState.RESUME,
            ft.AppLifecycleState.SHOW,
            ft.AppLifecycleState.RESTART,
        }:
            self._mostrar_lembrete_do_dia(force=True)

    def _mostrar_lembrete_do_dia(self, force: bool = False) -> None:
        if self._lembrete_mostrado_hoje and not force:
            return

        itens = self.lembretes.compromissos_para_lembrar()
        mensagem = self.lembretes.mensagem_pendente()
        if not mensagem:
            return

        self._lembrete_mostrado_hoje = True
        self.lembretes.marcar_exibidos(itens)
        self.page.show_dialog(
            ft.SnackBar(
                content=ft.Text(mensagem),
                action="Ver agenda",
                on_action=lambda _: self.navigate("agenda"),
                show_close_icon=True,
            )
        )

    def _on_nav_change(self, event: ft.Event[ft.NavigationBar]) -> None:
        index = event.control.selected_index or 0
        keys = ["dashboard", "registrar", "estudantes", "agenda", "relatorios"]
        self.navigate(keys[index], update_nav=False)

    def _dados_restaurados(self) -> None:
        config = self.configuracoes.todas()
        self.page.theme_mode = (
            ft.ThemeMode.DARK if config["tema"] == "escuro" else ft.ThemeMode.LIGHT
        )
        self.navigate("dashboard")

    def navigate(self, key: str, update_nav: bool = True, **kwargs) -> None:
        self.current_key = key

        if key == "dashboard":
            control = dashboard_view(
                self.atividades,
                self.estudantes,
                self.visitas,
                self.configuracoes,
                self.navigate,
            )
        elif key == "registrar":
            control = registrar_view(
                page=self.page,
                atividades=self.atividades,
                cronometro=self.cronometro,
                is_visible=lambda: self.current_key == "registrar",
                on_saved=lambda: self.navigate("dashboard"),
            )
        elif key == "estudantes":
            control = estudantes_view(
                self.estudantes,
                on_open=lambda estudante_id: self.navigate(
                    "estudante_detalhes",
                    estudante_id=estudante_id,
                ),
            )
        elif key == "estudante_detalhes":
            estudante_id = int(kwargs.get("estudante_id", 0))
            control = estudante_detalhes_view(
                estudante_id=estudante_id,
                estudantes=self.estudantes,
                visitas=self.visitas,
                geolocator=self.geolocator,
                on_back=lambda: self.navigate("estudantes"),
                on_deleted=lambda: self.navigate("estudantes"),
            )
        elif key == "agenda":
            control = agenda_view(
                self.visitas,
                self.estudantes,
                self.geolocator,
            )
        elif key == "relatorios":
            control = relatorios_view(
                self.atividades,
                self.configuracoes,
                self.exportacao,
            )
        elif key == "configuracoes":
            control = configuracoes_view(
                self.page,
                self.configuracoes,
                self.backup,
                self.exportacao,
                self._dados_restaurados,
            )
        else:
            key = "dashboard"
            self.current_key = key
            control = dashboard_view(
                self.atividades,
                self.estudantes,
                self.visitas,
                self.configuracoes,
                self.navigate,
            )

        self.content.content = control

        if update_nav:
            nav_indexes = {
                "dashboard": 0,
                "registrar": 1,
                "estudantes": 2,
                "estudante_detalhes": 2,
                "agenda": 3,
                "relatorios": 4,
            }
            if key in nav_indexes:
                self.nav.selected_index = nav_indexes[key]

        self.page.update()
