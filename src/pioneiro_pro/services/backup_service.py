from __future__ import annotations

import json
from datetime import datetime, timezone

from pioneiro_pro.database import Database


class BackupService:
    TABLES = ("atividades", "estudantes", "visitas", "configuracoes")

    def __init__(self, database: Database) -> None:
        self.database = database

    def exportar_bytes(self) -> bytes:
        dados: dict[str, object] = {
            "formato": "pioneiro-pro-backup",
            "versao": 1,
            "exportado_em": datetime.now(timezone.utc).isoformat(),
            "dados": {},
        }

        with self.database.connect() as connection:
            tabelas: dict[str, list[dict]] = {}
            for tabela in self.TABLES:
                rows = connection.execute(f"SELECT * FROM {tabela}").fetchall()
                tabelas[tabela] = [dict(row) for row in rows]

        dados["dados"] = tabelas
        return json.dumps(
            dados,
            ensure_ascii=False,
            indent=2,
        ).encode("utf-8")

    def restaurar_bytes(self, conteudo: bytes) -> None:
        payload = json.loads(conteudo.decode("utf-8"))
        if payload.get("formato") != "pioneiro-pro-backup":
            raise ValueError("Arquivo de backup inválido.")

        dados = payload.get("dados")
        if not isinstance(dados, dict):
            raise ValueError("Backup sem dados válidos.")

        with self.database.connect() as connection:
            connection.execute("PRAGMA foreign_keys = OFF")
            try:
                connection.execute("BEGIN")
                for tabela in ("visitas", "atividades", "estudantes", "configuracoes"):
                    connection.execute(f"DELETE FROM {tabela}")

                for tabela in self.TABLES:
                    registros = dados.get(tabela, [])
                    if not isinstance(registros, list):
                        continue

                    for registro in registros:
                        if not isinstance(registro, dict) or not registro:
                            continue
                        colunas = list(registro.keys())
                        placeholders = ", ".join("?" for _ in colunas)
                        nomes = ", ".join(colunas)
                        valores = [registro[coluna] for coluna in colunas]
                        connection.execute(
                            f"INSERT INTO {tabela} ({nomes}) VALUES ({placeholders})",
                            valores,
                        )

                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                connection.execute("PRAGMA foreign_keys = ON")
