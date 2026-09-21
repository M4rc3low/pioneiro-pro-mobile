from __future__ import annotations

from pioneiro_pro.database import Database


class EstudanteRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def criar(self, nome: str, telefone: str = "", observacao: str = "") -> int:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO estudantes (nome, telefone, observacao)
                VALUES (?, ?, ?)
                """,
                (nome.strip(), telefone.strip(), observacao.strip()),
            )
            return int(cursor.lastrowid)

    def listar(self) -> list[dict]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, nome, telefone, status, observacao
                FROM estudantes
                ORDER BY nome COLLATE NOCASE
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def quantidade_ativos(self) -> int:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS total FROM estudantes WHERE status = 'ativo'"
            ).fetchone()
        return int(row["total"])
