from datetime import date

import flet as ft

from pioneiro_pro.repositories import AtividadeRepository


def registrar_view(
    atividades: AtividadeRepository,
    on_saved,
) -> ft.Control:
    data = ft.TextField(label="Data", value=date.today().isoformat())
    tipo = ft.Dropdown(
        label="Tipo de atividade",
        value="ministerio",
        options=[
            ft.DropdownOption(key="ministerio", text="Ministério"),
            ft.DropdownOption(key="estudo_biblico", text="Estudo bíblico"),
            ft.DropdownOption(key="revisita", text="Revisita"),
            ft.DropdownOption(key="outra", text="Outra"),
        ],
    )
    horas = ft.TextField(label="Horas", value="0", keyboard_type=ft.KeyboardType.NUMBER)
    minutos = ft.TextField(label="Minutos", value="0", keyboard_type=ft.KeyboardType.NUMBER)
    observacao = ft.TextField(
        label="Observação",
        multiline=True,
        min_lines=2,
        max_lines=4,
    )
    mensagem = ft.Text(size=13)

    def salvar(_):
        try:
            h = max(0, int(horas.value or 0))
            m = max(0, int(minutos.value or 0))
            total = h * 60 + m
        except ValueError:
            mensagem.value = "Informe horas e minutos usando apenas números."
            mensagem.color = ft.Colors.RED
            mensagem.update()
            return

        if total <= 0:
            mensagem.value = "Informe um tempo maior que zero."
            mensagem.color = ft.Colors.RED
            mensagem.update()
            return

        atividades.criar(
            data=data.value or date.today().isoformat(),
            tipo=tipo.value or "ministerio",
            minutos=total,
            observacao=observacao.value or "",
        )
        mensagem.value = "Atividade salva com sucesso."
        mensagem.color = ft.Colors.GREEN_700
        mensagem.update()
        on_saved()

    return ft.ListView(
        expand=True,
        padding=16,
        spacing=16,
        controls=[
            ft.Text("Registrar atividade", size=26, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Registre o tempo e os detalhes da atividade.",
                color=ft.Colors.GREY_600,
            ),
            data,
            tipo,
            ft.Row(
                spacing=10,
                controls=[
                    ft.Container(expand=True, content=horas),
                    ft.Container(expand=True, content=minutos),
                ],
            ),
            observacao,
            mensagem,
            ft.FilledButton(
                "Salvar atividade",
                icon=ft.Icons.SAVE_OUTLINED,
                on_click=salvar,
            ),
        ],
    )
