from __future__ import annotations

import flet as ft


ACCENT = ft.Colors.BLUE_600
ACCENT_STRONG = ft.Colors.BLUE_700
SUCCESS = ft.Colors.GREEN_600
WARNING = ft.Colors.ORANGE_600
DANGER = ft.Colors.RED_600
MUTED = ft.Colors.GREY_500


def icon_badge(
    icon: ft.IconData,
    *,
    color: str = ACCENT,
    size: int = 20,
    box_size: int = 42,
) -> ft.Container:
    return ft.Container(
        width=box_size,
        height=box_size,
        border_radius=14,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(icon, color=color, size=size),
    )


def panel(
    content: ft.Control,
    *,
    padding: int = 18,
    radius: int = 22,
    expand: bool | int | None = None,
    bgcolor: str | None = None,
) -> ft.Container:
    return ft.Container(
        expand=expand,
        padding=padding,
        border_radius=radius,
        bgcolor=bgcolor or ft.Colors.SURFACE,
        content=content,
    )


def page_header(
    title: str,
    subtitle: str,
    icon: ft.IconData,
    *,
    trailing: ft.Control | None = None,
) -> ft.Control:
    controls: list[ft.Control] = [
        icon_badge(icon, box_size=48, size=23),
        ft.Container(
            expand=True,
            content=ft.Column(
                spacing=2,
                controls=[
                    ft.Text(title, size=27, weight=ft.FontWeight.BOLD),
                    ft.Text(subtitle, size=13, color=MUTED),
                ],
            ),
        ),
    ]
    if trailing is not None:
        controls.append(trailing)

    return ft.Row(
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=controls,
    )


def section_header(
    title: str,
    *,
    subtitle: str | None = None,
    trailing: ft.Control | None = None,
) -> ft.Control:
    text_controls: list[ft.Control] = [
        ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
    ]
    if subtitle:
        text_controls.append(ft.Text(subtitle, size=12, color=MUTED))

    controls: list[ft.Control] = [
        ft.Container(
            expand=True,
            content=ft.Column(spacing=1, controls=text_controls),
        )
    ]
    if trailing is not None:
        controls.append(trailing)

    return ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=controls,
    )


def metric_card(
    label: str,
    value: str,
    icon: ft.IconData,
    *,
    color: str = ACCENT,
    helper: str | None = None,
) -> ft.Container:
    controls: list[ft.Control] = [
        icon_badge(icon, color=color, box_size=40, size=20),
        ft.Text(label, size=12, color=MUTED),
        ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
    ]
    if helper:
        controls.append(ft.Text(helper, size=11, color=MUTED))

    return panel(
        ft.Column(spacing=7, controls=controls),
        padding=16,
        radius=20,
        expand=True,
    )


def status_pill(
    text: str,
    *,
    color: str = ACCENT,
    icon: ft.IconData | None = None,
) -> ft.Container:
    controls: list[ft.Control] = []
    if icon is not None:
        controls.append(ft.Icon(icon, color=color, size=14))
    controls.append(
        ft.Text(
            text,
            size=11,
            weight=ft.FontWeight.BOLD,
            color=color,
        )
    )

    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=10, vertical=6),
        border_radius=999,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        content=ft.Row(spacing=5, tight=True, controls=controls),
    )


def empty_state(
    icon: ft.IconData,
    title: str,
    subtitle: str,
    *,
    action: ft.Control | None = None,
) -> ft.Container:
    controls: list[ft.Control] = [
        icon_badge(icon, box_size=54, size=26),
        ft.Text(
            title,
            size=16,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        ),
        ft.Text(
            subtitle,
            size=12,
            color=MUTED,
            text_align=ft.TextAlign.CENTER,
        ),
    ]
    if action is not None:
        controls.append(action)

    return panel(
        ft.Column(
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=controls,
        ),
        padding=22,
    )


def action_tile(
    title: str,
    subtitle: str,
    icon: ft.IconData,
    on_click,
    *,
    color: str = ACCENT,
    trailing: ft.Control | None = None,
) -> ft.Container:
    right = trailing or ft.Icon(ft.Icons.CHEVRON_RIGHT, color=MUTED)

    tile = panel(
        ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                icon_badge(icon, color=color),
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(title, weight=ft.FontWeight.BOLD),
                            ft.Text(subtitle, size=12, color=MUTED),
                        ],
                    ),
                ),
                right,
            ],
        ),
        padding=14,
    )
    tile.on_click = on_click
    return tile
