from __future__ import annotations

import csv
import io
from datetime import date

from pioneiro_pro.repositories import AtividadeRepository
from pioneiro_pro.utils import formatar_minutos


TIPOS = {
    "ministerio": "Ministério",
    "estudo_biblico": "Estudo bíblico",
    "revisita": "Revisita",
    "outra": "Outra",
}


class ExportacaoService:
    def __init__(self, atividades: AtividadeRepository) -> None:
        self.atividades = atividades

    def relatorio_csv(self) -> bytes:
        saida = io.StringIO()
        writer = csv.writer(saida)
        writer.writerow(["Data", "Tipo", "Minutos", "Tempo", "Observação"])

        for item in self.atividades.listar():
            writer.writerow(
                [
                    item["data"],
                    TIPOS.get(item["tipo"], item["tipo"].replace("_", " ").title()),
                    item["minutos"],
                    formatar_minutos(item["minutos"]),
                    item["observacao"],
                ]
            )

        return saida.getvalue().encode("utf-8-sig")

    def resumo_txt(self) -> bytes:
        hoje = date.today()
        total_mes = self.atividades.total_minutos_mes(hoje.year, hoje.month)
        total_ano = self.atividades.total_minutos_ano(hoje.year)

        linhas = [
            "Pioneiro Pro - Resumo",
            f"Período: {hoje:%m/%Y}",
            "",
            f"Total no mês: {formatar_minutos(total_mes)}",
            f"Total no ano: {formatar_minutos(total_ano)}",
            "",
            "Atividades recentes:",
        ]

        for item in self.atividades.listar_recentes(20):
            linhas.append(
                f'- {item["data"]} | '
                f'{TIPOS.get(item["tipo"], item["tipo"].replace("_", " ").title())} | '
                f'{formatar_minutos(item["minutos"])}'
            )

        return ("\n".join(linhas) + "\n").encode("utf-8")
