import flet as ft

from pioneiro_pro.ui import (
    app_logo,
    brand_gradient,
    empty_state,
    metric_card,
    panel,
    status_pill,
)


def test_gradiente_da_marca_possui_tres_cores():
    gradient = brand_gradient()

    assert isinstance(gradient, ft.LinearGradient)
    assert len(gradient.colors) == 3


def test_panel_moderno_usa_superficie_e_borda_sem_sombra_por_padrao():
    card = panel(ft.Text("Conteúdo"))

    assert card.content is not None
    assert card.border is not None
    assert card.shadow is None
    assert card.border_radius == 20


def test_panel_elevado_continua_disponivel_quando_necessario():
    card = panel(ft.Text("Conteúdo"), elevated=True)

    assert card.shadow is not None


def test_logo_oficial_constroi_com_asset_do_app():
    logo = app_logo()

    assert logo.content is not None
    assert isinstance(logo.content, ft.Image)
    assert logo.content.src == "icon.png"


def test_componentes_visuais_constroem_sem_erro():
    metric = metric_card(
        "Tempo",
        "10h",
        ft.Icons.TIMER_OUTLINED,
    )
    pill = status_pill(
        "Ativo",
        icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
    )
    empty = empty_state(
        ft.Icons.INBOX_OUTLINED,
        "Nada aqui",
        "Descrição do estado vazio.",
    )

    assert metric is not None
    assert pill is not None
    assert empty is not None
