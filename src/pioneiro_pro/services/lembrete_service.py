from __future__ import annotations

from datetime import datetime, timedelta

from pioneiro_pro.repositories import VisitaRepository


class LembreteService:
    def __init__(self, visitas: VisitaRepository) -> None:
        self.visitas = visitas

    @staticmethod
    def _quando(item: dict) -> datetime | None:
        data = (item.get("data") or "").strip()
        horario = (item.get("horario") or "").strip() or "00:00"
        try:
            return datetime.fromisoformat(f"{data}T{horario}")
        except ValueError:
            return None

    def compromissos_para_lembrar(
        self,
        agora: datetime | None = None,
    ) -> list[dict]:
        agora = agora or datetime.now()
        encontrados: list[dict] = []

        for item in self.visitas.listar():
            if bool(item["concluida"]) or bool(item.get("notificado")):
                continue

            quando = self._quando(item)
            if quando is None or quando < agora:
                continue

            antecedencia = max(0, int(item.get("lembrar_minutos_antes") or 0))
            inicio = quando - timedelta(minutes=antecedencia)

            if inicio <= agora <= quando:
                encontrados.append(item)

        return encontrados

    def mensagem_pendente(self, agora: datetime | None = None) -> str | None:
        itens = self.compromissos_para_lembrar(agora)
        if not itens:
            return None

        if len(itens) == 1:
            item = itens[0]
            nome = item["estudante_nome"] or item["tipo"].replace("_", " ").title()
            horario = f' às {item["horario"]}' if item["horario"] else ""
            return f"Lembrete: {nome}{horario}."

        return f"Você tem {len(itens)} compromissos próximos."

    def marcar_exibidos(self, itens: list[dict]) -> None:
        for item in itens:
            self.visitas.marcar_notificado(int(item["id"]))
