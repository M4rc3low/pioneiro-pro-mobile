from __future__ import annotations

from pioneiro_pro.database import Database


class EstudanteRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def criar(
        self,
        nome: str,
        telefone: str = "",
        observacao: str = "",
        endereco: str = "",
        modalidade: str = "",
        horario_preferido: str = "",
        publicacao_atual: str = "",
        licao_atual: str = "",
        data_inicio: str = "",
    ) -> int:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO estudantes (
                    nome,
                    telefone,
                    observacao,
                    endereco,
                    modalidade,
                    horario_preferido,
                    publicacao_atual,
                    licao_atual,
                    data_inicio
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    nome.strip(),
                    telefone.strip(),
                    observacao.strip(),
                    endereco.strip(),
                    modalidade,
                    horario_preferido,
                    publicacao_atual.strip(),
                    licao_atual.strip(),
                    data_inicio,
                ),
            )
            return int(cursor.lastrowid)

    def obter(self, estudante_id: int) -> dict | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    nome,
                    telefone,
                    status,
                    observacao,
                    endereco,
                    modalidade,
                    horario_preferido,
                    publicacao_atual,
                    licao_atual,
                    data_inicio
                FROM estudantes
                WHERE id = ?
                """,
                (estudante_id,),
            ).fetchone()
        return dict(row) if row else None

    def listar(self) -> list[dict]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    nome,
                    telefone,
                    status,
                    observacao,
                    endereco,
                    modalidade,
                    horario_preferido,
                    publicacao_atual,
                    licao_atual,
                    data_inicio
                FROM estudantes
                ORDER BY nome COLLATE NOCASE
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def atualizar(self, estudante_id: int, dados: dict) -> None:
        campos = {
            "nome",
            "telefone",
            "status",
            "observacao",
            "endereco",
            "modalidade",
            "horario_preferido",
            "publicacao_atual",
            "licao_atual",
            "data_inicio",
        }
        atualizacoes = {chave: dados[chave] for chave in campos if chave in dados}
        if not atualizacoes:
            return

        definicoes = ", ".join(f"{chave} = ?" for chave in atualizacoes)
        valores = list(atualizacoes.values()) + [estudante_id]

        with self.database.connect() as connection:
            connection.execute(
                f"UPDATE estudantes SET {definicoes} WHERE id = ?",
                valores,
            )

    def excluir(self, estudante_id: int) -> None:
        with self.database.connect() as connection:
            connection.execute(
                "DELETE FROM estudantes WHERE id = ?",
                (estudante_id,),
            )

    def quantidade_ativos(self) -> int:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS total FROM estudantes WHERE status = 'ativo'"
            ).fetchone()
        return int(row["total"])
