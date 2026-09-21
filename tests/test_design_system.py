import flet as ft

from pioneiro_pro.ui import (
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


def test_panel_aplica_superficie_borda_e_sombra():
    card = panel(ft.Text("Conteúdo"))

    assert card.content is not None
    assert card.border is not None
    assert card.shadow is not None
    assert card.border_radius == 22


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
