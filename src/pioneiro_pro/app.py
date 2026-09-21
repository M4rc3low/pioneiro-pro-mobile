from __future__ import annotations

import flet as ft

from pioneiro_pro.database import Database
from pioneiro_pro.pages import (
    agenda_view,
    configuracoes_view,
    dashboard_view,
    estudantes_view,
    registrar_view,
    relatorios_view,
)
from pioneiro_pro.repositories import AtividadeRepository, EstudanteRepository


class PioneiroProApp:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.database = Database()
        self.database.initialize()

        self.atividades = AtividadeRepository(self.database)
        self.estudantes = EstudanteRepository(self.database)

        self.current_key = "dashboard"
        self.content = ft.Container(expand=True)

        self.nav = ft.NavigationBar(
            selected_index=0,
            on_change=self._on_nav_change,
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
        self.page.title = "Pioneiro Pro"
        self.page.padding = 0
        self.page.bgcolor = ft.Colors.GREY_100
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
        self.page.navigation_bar = self.nav

        self.page.appbar = ft.AppBar(
            title=ft.Text("Pioneiro Pro", weight=ft.FontWeight.BOLD),
            center_title=False,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    tooltip="Configurações",
                    on_click=lambda _: self.navigate("configuracoes"),
                )
            ],
        )

        self.page.add(
            ft.SafeArea(
                expand=True,
                content=self.content,
            )
        )
        self.navigate("dashboard")

    def _on_nav_change(self, event: ft.Event[ft.NavigationBar]) -> None:
        index = event.control.selected_index or 0
        keys = ["dashboard", "registrar", "estudantes", "agenda", "relatorios"]
        self.navigate(keys[index], update_nav=False)

    def navigate(self, key: str, update_nav: bool = True) -> None:
        self.current_key = key

        if key == "dashboard":
            control = dashboard_view(
                self.atividades,
                self.estudantes,
                self.navigate,
            )
        elif key == "registrar":
            control = registrar_view(
                self.atividades,
                on_saved=lambda: self.navigate("dashboard"),
            )
        elif key == "estudantes":
            control = estudantes_view(self.estudantes)
        elif key == "agenda":
            control = agenda_view()
        elif key == "relatorios":
            control = relatorios_view(self.atividades)
        elif key == "configuracoes":
            control = configuracoes_view()
        else:
            control = dashboard_view(
                self.atividades,
                self.estudantes,
                self.navigate,
            )
            key = "dashboard"

        self.content.content = control

        if update_nav:
            nav_indexes = {
                "dashboard": 0,
                "registrar": 1,
                "estudantes": 2,
                "agenda": 3,
                "relatorios": 4,
            }
            if key in nav_indexes:
                self.nav.selected_index = nav_indexes[key]

        self.page.update()
