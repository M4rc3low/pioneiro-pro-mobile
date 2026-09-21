from __future__ import annotations

from datetime import date

from pioneiro_pro.database import Database


class VisitaRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def criar(
        self,
        data: str,
        horario: str,
        tipo: str,
        estudante_id: int | None = None,
        observacao: str = "",
    ) -> int:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO visitas (estudante_id, data, horario, tipo, observacao)
                VALUES (?, ?, ?, ?, ?)
                """,
                (estudante_id, data, horario.strip(), tipo, observacao.strip()),
            )
            return int(cursor.lastrowid)

    def listar(self, somente_futuras: bool = False) -> list[dict]:
        sql = """
            SELECT
                v.id,
                v.estudante_id,
                v.data,
                v.horario,
                v.tipo,
                v.observacao,
                v.concluida,
                e.nome AS estudante_nome
            FROM visitas v
            LEFT JOIN estudantes e ON e.id = v.estudante_id
        """
        params: tuple = ()
        if somente_futuras:
            sql += " WHERE v.data >= ?"
            params = (date.today().isoformat(),)
        sql += " ORDER BY v.data ASC, v.horario ASC, v.id ASC"

        with self.database.connect() as connection:
            rows = connection.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def listar_por_estudante(self, estudante_id: int) -> list[dict]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, data, horario, tipo, observacao, concluida
                FROM visitas
                WHERE estudante_id = ?
                ORDER BY data DESC, horario DESC, id DESC
                """,
                (estudante_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def atualizar(
        self,
        visita_id: int,
        data: str,
        horario: str,
        tipo: str,
        estudante_id: int | None,
        observacao: str,
    ) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE visitas
                SET estudante_id = ?, data = ?, horario = ?, tipo = ?, observacao = ?
                WHERE id = ?
                """,
                (
                    estudante_id,
                    data,
                    horario.strip(),
                    tipo,
                    observacao.strip(),
                    visita_id,
                ),
            )

    def marcar_concluida(self, visita_id: int, concluida: bool) -> None:
        with self.database.connect() as connection:
            connection.execute(
                "UPDATE visitas SET concluida = ? WHERE id = ?",
                (1 if concluida else 0, visita_id),
            )

    def excluir(self, visita_id: int) -> None:
        with self.database.connect() as connection:
            connection.execute("DELETE FROM visitas WHERE id = ?", (visita_id,))

    def quantidade_pendentes(self) -> int:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM visitas
                WHERE concluida = 0 AND data >= ?
                """,
                (date.today().isoformat(),),
            ).fetchone()
        return int(row["total"])
