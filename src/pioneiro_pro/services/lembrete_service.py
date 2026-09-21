from __future__ import annotations

from datetime import date

from pioneiro_pro.repositories import VisitaRepository


class LembreteService:
    def __init__(self, visitas: VisitaRepository) -> None:
        self.visitas = visitas

    def compromissos_hoje(self) -> list[dict]:
        hoje = date.today().isoformat()
        return [
            item
            for item in self.visitas.listar()
            if item["data"] == hoje and not bool(item["concluida"])
        ]

    def mensagem_hoje(self) -> str | None:
        itens = self.compromissos_hoje()
        if not itens:
            return None

        if len(itens) == 1:
            item = itens[0]
            nome = item["estudante_nome"] or "compromisso"
            horario = f' às {item["horario"]}' if item["horario"] else ""
            return f"Você tem {nome}{horario} hoje."

        return f"Você tem {len(itens)} compromissos pendentes hoje."
