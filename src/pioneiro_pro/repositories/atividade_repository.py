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

    def atualizar(
        self,
        atividade_id: int,
        data: str,
        tipo: str,
        minutos: int,
        observacao: str = "",
    ) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE atividades
                SET data = ?, tipo = ?, minutos = ?, observacao = ?
                WHERE id = ?
                """,
                (data, tipo, minutos, observacao.strip(), atividade_id),
            )

    def excluir(self, atividade_id: int) -> None:
        with self.database.connect() as connection:
            connection.execute(
                "DELETE FROM atividades WHERE id = ?",
                (atividade_id,),
            )

    def obter(self, atividade_id: int) -> dict | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, data, tipo, minutos, observacao
                FROM atividades
                WHERE id = ?
                """,
                (atividade_id,),
            ).fetchone()
        return dict(row) if row else None

    def listar(self, limite: int | None = None) -> list[dict]:
        sql = """
            SELECT id, data, tipo, minutos, observacao
            FROM atividades
            ORDER BY data DESC, id DESC
        """
        params: tuple = ()
        if limite is not None:
            sql += " LIMIT ?"
            params = (limite,)
        with self.database.connect() as connection:
            rows = connection.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def listar_recentes(self, limite: int = 10) -> list[dict]:
        return self.listar(limite)

    def buscar(
        self,
        texto: str = "",
        tipo: str | None = None,
        limite: int = 100,
    ) -> list[dict]:
        filtros = []
        params: list[object] = []

        if texto.strip():
            termo = f"%{texto.strip()}%"
            filtros.append(
                "(data LIKE ? OR observacao LIKE ? OR tipo LIKE ?)"
            )
            params.extend([termo, termo, termo])

        if tipo:
            filtros.append("tipo = ?")
            params.append(tipo)

        sql = """
            SELECT id, data, tipo, minutos, observacao
            FROM atividades
        """
        if filtros:
            sql += " WHERE " + " AND ".join(filtros)
        sql += " ORDER BY data DESC, id DESC LIMIT ?"
        params.append(limite)

        with self.database.connect() as connection:
            rows = connection.execute(sql, tuple(params)).fetchall()
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

    def total_minutos_ano(self, ano: int | None = None) -> int:
        ano = ano or date.today().year
        prefixo = f"{ano:04d}"

        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT COALESCE(SUM(minutos), 0) AS total
                FROM atividades
                WHERE substr(data, 1, 4) = ?
                """,
                (prefixo,),
            ).fetchone()
        return int(row["total"])

    def totais_por_mes(self, ano: int | None = None) -> list[dict]:
        ano = ano or date.today().year
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    CAST(substr(data, 6, 2) AS INTEGER) AS mes,
                    COALESCE(SUM(minutos), 0) AS minutos
                FROM atividades
                WHERE substr(data, 1, 4) = ?
                GROUP BY substr(data, 6, 2)
                ORDER BY mes
                """,
                (f"{ano:04d}",),
            ).fetchall()
        valores = {int(row["mes"]): int(row["minutos"]) for row in rows}
        return [{"mes": mes, "minutos": valores.get(mes, 0)} for mes in range(1, 13)]

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
