from __future__ import annotations

import os
import sqlite3
from pathlib import Path


class Database:
    def __init__(self, path: str | Path | None = None) -> None:
        if path is None:
            app_data = os.getenv("FLET_APP_STORAGE_DATA")
            data_dir = Path(app_data) if app_data else Path.cwd() / ".pioneiro_pro"
            data_dir.mkdir(parents=True, exist_ok=True)
            path = data_dir / "pioneiro_pro.db"

        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS atividades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    minutos INTEGER NOT NULL DEFAULT 0,
                    observacao TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS estudantes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    telefone TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'ativo',
                    observacao TEXT NOT NULL DEFAULT '',
                    endereco TEXT NOT NULL DEFAULT '',
                    modalidade TEXT NOT NULL DEFAULT '',
                    horario_preferido TEXT NOT NULL DEFAULT '',
                    publicacao_atual TEXT NOT NULL DEFAULT '',
                    licao_atual TEXT NOT NULL DEFAULT '',
                    data_inicio TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS visitas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    estudante_id INTEGER,
                    data TEXT NOT NULL,
                    horario TEXT NOT NULL DEFAULT '',
                    tipo TEXT NOT NULL DEFAULT 'estudo',
                    observacao TEXT NOT NULL DEFAULT '',
                    concluida INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (estudante_id) REFERENCES estudantes(id) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS configuracoes (
                    chave TEXT PRIMARY KEY,
                    valor TEXT NOT NULL
                );
                """
            )

            self._ensure_column(connection, "estudantes", "endereco", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(connection, "estudantes", "modalidade", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(
                connection,
                "estudantes",
                "horario_preferido",
                "TEXT NOT NULL DEFAULT ''",
            )
            self._ensure_column(
                connection,
                "estudantes",
                "publicacao_atual",
                "TEXT NOT NULL DEFAULT ''",
            )
            self._ensure_column(
                connection,
                "estudantes",
                "licao_atual",
                "TEXT NOT NULL DEFAULT ''",
            )
            self._ensure_column(
                connection,
                "estudantes",
                "data_inicio",
                "TEXT NOT NULL DEFAULT ''",
            )

    @staticmethod
    def _ensure_column(
        connection: sqlite3.Connection,
        table: str,
        column: str,
        definition: str,
    ) -> None:
        columns = {
            row["name"]
            for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
        }
        if column not in columns:
            connection.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
            )
