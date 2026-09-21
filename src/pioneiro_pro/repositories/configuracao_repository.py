from __future__ import annotations

from pioneiro_pro.database import Database


class ConfiguracaoRepository:
    DEFAULTS = {
        "nome_pioneiro": "",
        "congregacao": "",
        "meta_horas_mes": "50",
        "meta_horas_ano": "600",
        "tema": "claro",
    }

    def __init__(self, database: Database) -> None:
        self.database = database

    def obter(self, chave: str, padrao: str | None = None) -> str:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT valor FROM configuracoes WHERE chave = ?",
                (chave,),
            ).fetchone()
        if row:
            return str(row["valor"])
        if padrao is not None:
            return padrao
        return self.DEFAULTS.get(chave, "")

    def definir(self, chave: str, valor: str | int | float) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO configuracoes (chave, valor)
                VALUES (?, ?)
                ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor
                """,
                (chave, str(valor)),
            )

    def todas(self) -> dict[str, str]:
        valores = dict(self.DEFAULTS)
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT chave, valor FROM configuracoes"
            ).fetchall()
        valores.update({str(row["chave"]): str(row["valor"]) for row in rows})
        return valores
