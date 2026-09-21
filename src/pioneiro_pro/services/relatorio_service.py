from __future__ import annotations

import csv
import io
from datetime import date

from pioneiro_pro.repositories import AtividadeRepository


class RelatorioService:
    def __init__(self, atividades: AtividadeRepository) -> None:
        self.atividades = atividades

    def csv_atividades(self) -> bytes:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Data", "Tipo", "Horas", "Minutos", "Observação"])

        for item in self.atividades.listar():
            total = int(item["minutos"])
            writer.writerow(
                [
                    item["data"],
                    item["tipo"].replace("_", " ").title(),
                    total // 60,
                    total % 60,
                    item["observacao"],
                ]
            )

        return output.getvalue().encode("utf-8-sig")

    def resumo_texto(self) -> str:
        hoje = date.today()
        total_mes = self.atividades.total_minutos_mes()
        total_ano = self.atividades.total_minutos_ano()

        def fmt(minutos: int) -> str:
            horas, resto = divmod(minutos, 60)
            return f"{horas}h {resto:02d}min"

        return (
            "Pioneiro Pro\n"
            f"Resumo de {hoje:%m/%Y}\n\n"
            f"Total do mês: {fmt(total_mes)}\n"
            f"Total do ano: {fmt(total_ano)}\n"
            f"Registros no mês: {self.atividades.quantidade_mes()}\n"
        )
