from __future__ import annotations

from datetime import date

from pioneiro_pro.database import Database


class AtividadeRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def criar(self, data: str, tipo: str, minutos: int, observacao: str = "") -> int:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO atividades (data, tipo, minutos, observacao)
                VALUES (?, ?, ?, ?)
                """,
                (data, tipo, minutos, observacao.strip()),
            )
            return int(cursor.lastrowid)

    def listar_recentes(self, limite: int = 10) -> list[dict]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, data, tipo, minutos, observacao
                FROM atividades
                ORDER BY data DESC, id DESC
                LIMIT ?
                """,
                (limite,),
            ).fetchall()
        return [dict(row) for row in rows]

    def total_minutos_mes(self, ano: int | None = None, mes: int | None = None) -> int:
        hoje = date.today()
        ano = ano or hoje.year
        mes = mes or hoje.month
        prefixo = f"{ano:04d}-{mes:02d}"

        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT COALESCE(SUM(minutos), 0) AS total
                FROM atividades
                WHERE substr(data, 1, 7) = ?
                """,
                (prefixo,),
            ).fetchone()
        return int(row["total"])

    def quantidade_mes(self, ano: int | None = None, mes: int | None = None) -> int:
        hoje = date.today()
        ano = ano or hoje.year
        mes = mes or hoje.month
        prefixo = f"{ano:04d}-{mes:02d}"

        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM atividades
                WHERE substr(data, 1, 7) = ?
                """,
                (prefixo,),
            ).fetchone()
        return int(row["total"])
