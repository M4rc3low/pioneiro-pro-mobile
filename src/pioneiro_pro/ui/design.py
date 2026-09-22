from __future__ import annotations

import flet as ft


ACCENT = ft.Colors.BLUE_600
ACCENT_STRONG = ft.Colors.BLUE_700
ACCENT_SOFT = ft.Colors.BLUE_100
SUCCESS = ft.Colors.GREEN_600
WARNING = ft.Colors.ORANGE_600
DANGER = ft.Colors.RED_600
MUTED = ft.Colors.ON_SURFACE_VARIANT


def brand_gradient() -> ft.LinearGradient:
    return ft.LinearGradient(
        begin=ft.Alignment.TOP_LEFT,
        end=ft.Alignment.BOTTOM_RIGHT,
        colors=[
            ft.Colors.BLUE_800,
            ft.Colors.BLUE_600,
            ft.Colors.CYAN_500,
        ],
        stops=[0.0, 0.62, 1.0],
    )


def soft_shadow() -> ft.BoxShadow:
    return ft.BoxShadow(
        blur_radius=18,
        spread_radius=0,
        color=ft.Colors.with_opacity(0.10, ft.Colors.BLACK),
        offset=ft.Offset(0, 6),
    )


def app_logo(size: int = 44, radius: int = 14) -> ft.Container:
    return ft.Container(
        width=size,
        height=size,
        border_radius=radius,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Image(
            src="icon.png",
            width=size,
            height=size,
            fit=ft.BoxFit.COVER,
        ),
    )


def icon_badge(
    icon: ft.IconData,
    *,
    color: str = ACCENT,
    size: int = 20,
    box_size: int = 40,
) -> ft.Container:
    return ft.Container(
        width=box_size,
        height=box_size,
        border_radius=13,
        bgcolor=ft.Colors.with_opacity(0.10, color),
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(icon, color=color, size=size),
    )


def panel(
    content: ft.Control,
    *,
    padding: int = 16,
    radius: int = 20,
    expand: bool | int | None = None,
    bgcolor: str | None = None,
    elevated: bool = False,
) -> ft.Container:
    return ft.Container(
        expand=expand,
        padding=padding,
        border_radius=radius,
        bgcolor=bgcolor or ft.Colors.SURFACE,
        border=ft.Border.all(
            width=1,
            color=ft.Colors.with_opacity(0.07, ft.Colors.OUTLINE),
        ),
        shadow=soft_shadow() if elevated else None,
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
        icon_badge(icon, box_size=44, size=22),
        ft.Container(
            expand=True,
            content=ft.Column(
                spacing=3,
                controls=[
                    ft.Text(
                        title,
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_SURFACE,
                    ),
                    ft.Text(
                        subtitle,
                        size=12,
                        color=MUTED,
                    ),
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
        ft.Text(
            title,
            size=18,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.ON_SURFACE,
        ),
    ]
    if subtitle:
        text_controls.append(ft.Text(subtitle, size=12, color=MUTED))

    controls: list[ft.Control] = [
        ft.Container(
            expand=True,
            content=ft.Column(spacing=2, controls=text_controls),
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
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                icon_badge(icon, color=color, box_size=42, size=21),
                ft.Container(
                    width=6,
                    height=6,
                    border_radius=99,
                    bgcolor=color,
                ),
            ],
        ),
        ft.Text(label, size=12, color=MUTED),
        ft.Text(
            value,
            size=23,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.ON_SURFACE,
        ),
    ]
    if helper:
        controls.append(ft.Text(helper, size=11, color=MUTED))

    return panel(
        ft.Column(spacing=8, controls=controls),
        padding=14,
        radius=22,
        expand=True,
        bgcolor=ft.Colors.SURFACE_CONTAINER,
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
        bgcolor=ft.Colors.with_opacity(0.12, color),
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
        icon_badge(icon, box_size=56, size=27),
        ft.Text(
            title,
            size=17,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
            color=ft.Colors.ON_SURFACE,
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
            spacing=9,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=controls,
        ),
        padding=24,
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
                        spacing=3,
                        controls=[
                            ft.Text(
                                title,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.ON_SURFACE,
                            ),
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
    tile.ink = True
    tile.ink_color = ft.Colors.with_opacity(0.06, color)
    return tile
