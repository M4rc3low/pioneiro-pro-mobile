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
        lembrar_minutos_antes: int = 30,
        latitude: float | None = None,
        longitude: float | None = None,
        raio_alerta_m: int = 200,
    ) -> int:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO visitas (
                    estudante_id, data, horario, tipo, observacao,
                    lembrar_minutos_antes, notificado,
                    latitude, longitude, raio_alerta_m, alerta_proximidade
                )
                VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?, 1)
                """,
                (
                    estudante_id,
                    data,
                    horario.strip(),
                    tipo,
                    observacao.strip(),
                    max(0, lembrar_minutos_antes),
                    latitude,
                    longitude,
                    max(50, raio_alerta_m),
                ),
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
                v.lembrar_minutos_antes,
                v.notificado,
                COALESCE(v.latitude, e.latitude) AS latitude,
                COALESCE(v.longitude, e.longitude) AS longitude,
                COALESCE(v.raio_alerta_m, e.raio_alerta_m, 200) AS raio_alerta_m,
                v.alerta_proximidade,
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
                SELECT
                    id, data, horario, tipo, observacao, concluida,
                    lembrar_minutos_antes, notificado,
                    latitude, longitude, raio_alerta_m, alerta_proximidade
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
        lembrar_minutos_antes: int = 30,
        latitude: float | None = None,
        longitude: float | None = None,
        raio_alerta_m: int = 200,
    ) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE visitas
                SET estudante_id = ?,
                    data = ?,
                    horario = ?,
                    tipo = ?,
                    observacao = ?,
                    lembrar_minutos_antes = ?,
                    notificado = 0,
                    latitude = ?,
                    longitude = ?,
                    raio_alerta_m = ?
                WHERE id = ?
                """,
                (
                    estudante_id,
                    data,
                    horario.strip(),
                    tipo,
                    observacao.strip(),
                    max(0, lembrar_minutos_antes),
                    latitude,
                    longitude,
                    max(50, raio_alerta_m),
                    visita_id,
                ),
            )

    def marcar_concluida(self, visita_id: int, concluida: bool) -> None:
        with self.database.connect() as connection:
            connection.execute(
                "UPDATE visitas SET concluida = ? WHERE id = ?",
                (1 if concluida else 0, visita_id),
            )

    def marcar_notificado(self, visita_id: int) -> None:
        with self.database.connect() as connection:
            connection.execute(
                "UPDATE visitas SET notificado = 1 WHERE id = ?",
                (visita_id,),
            )

    def excluir(self, visita_id: int) -> None:
        with self.database.connect() as connection:
            connection.execute("DELETE FROM visitas WHERE id = ?", (visita_id,))

    def listar_para_proximidade(self) -> list[dict]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    v.id,
                    v.tipo,
                    v.data,
                    v.horario,
                    v.observacao,
                    v.estudante_id,
                    e.nome AS estudante_nome,
                    COALESCE(v.latitude, e.latitude) AS latitude,
                    COALESCE(v.longitude, e.longitude) AS longitude,
                    COALESCE(v.raio_alerta_m, e.raio_alerta_m, 200) AS raio_alerta_m
                FROM visitas v
                LEFT JOIN estudantes e ON e.id = v.estudante_id
                WHERE v.concluida = 0
                  AND v.alerta_proximidade = 1
                  AND COALESCE(v.latitude, e.latitude) IS NOT NULL
                  AND COALESCE(v.longitude, e.longitude) IS NOT NULL
                ORDER BY v.data ASC, v.horario ASC
                """
            ).fetchall()
        return [dict(row) for row in rows]

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
