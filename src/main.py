import flet as ft

from pioneiro_pro.app import PioneiroProApp


def main(page: ft.Page) -> None:
    PioneiroProApp(page).mount()


if __name__ == "__main__":
    ft.run(main)
