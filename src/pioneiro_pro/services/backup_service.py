from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timezone

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from pioneiro_pro.database import Database


class BackupService:
    TABLES = ("atividades", "estudantes", "visitas", "configuracoes")
    FORMAT = "pioneiro-pro-backup"
    PROTECTED_FORMAT = "pioneiro-pro-backup-protected"
    PROTECTED_VERSION = 1
    KDF_ITERATIONS = 600_000
    AAD = b"pioneiro-pro-backup:v1"

    def __init__(self, database: Database) -> None:
        self.database = database

    def exportar_bytes(self) -> bytes:
        dados: dict[str, object] = {
            "formato": self.FORMAT,
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

    @staticmethod
    def _derive_key(password: str, salt: bytes, iterations: int) -> bytes:
        if not password:
            raise ValueError("Informe uma senha para proteger o backup.")
        if not 100_000 <= iterations <= 2_000_000:
            raise ValueError("Parâmetros de criptografia inválidos.")

        return PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
        ).derive(password.encode("utf-8"))

    def exportar_protegido_bytes(self, password: str) -> bytes:
        if len(password) < 8:
            raise ValueError("A senha do backup deve ter pelo menos 8 caracteres.")

        plaintext = self.exportar_bytes()
        salt = os.urandom(16)
        nonce = os.urandom(12)
        key = self._derive_key(password, salt, self.KDF_ITERATIONS)
        ciphertext = AESGCM(key).encrypt(nonce, plaintext, self.AAD)

        envelope = {
            "formato": self.PROTECTED_FORMAT,
            "versao": self.PROTECTED_VERSION,
            "kdf": "pbkdf2-sha256",
            "iteracoes": self.KDF_ITERATIONS,
            "salt": base64.b64encode(salt).decode("ascii"),
            "nonce": base64.b64encode(nonce).decode("ascii"),
            "conteudo": base64.b64encode(ciphertext).decode("ascii"),
        }
        return json.dumps(envelope, separators=(",", ":")).encode("utf-8")

    def eh_backup_protegido(self, conteudo: bytes) -> bool:
        try:
            payload = json.loads(conteudo.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return False
        return payload.get("formato") == self.PROTECTED_FORMAT

    def restaurar_protegido_bytes(self, conteudo: bytes, password: str) -> None:
        try:
            envelope = json.loads(conteudo.decode("utf-8"))
            if envelope.get("formato") != self.PROTECTED_FORMAT:
                raise ValueError("Arquivo de backup protegido inválido.")
            if envelope.get("versao") != self.PROTECTED_VERSION:
                raise ValueError("Versão de backup protegido não suportada.")
            if envelope.get("kdf") != "pbkdf2-sha256":
                raise ValueError("Método de proteção do backup não suportado.")

            iterations = int(envelope["iteracoes"])
            salt = base64.b64decode(envelope["salt"], validate=True)
            nonce = base64.b64decode(envelope["nonce"], validate=True)
            ciphertext = base64.b64decode(envelope["conteudo"], validate=True)

            if len(salt) != 16 or len(nonce) != 12:
                raise ValueError("Parâmetros de criptografia inválidos.")

            key = self._derive_key(password, salt, iterations)
            plaintext = AESGCM(key).decrypt(nonce, ciphertext, self.AAD)
        except InvalidTag as exc:
            raise ValueError("Senha incorreta ou backup alterado.") from exc
        except (
            KeyError,
            TypeError,
            ValueError,
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:
            if isinstance(exc, ValueError) and str(exc):
                raise
            raise ValueError("Backup protegido inválido.") from exc

        self.restaurar_bytes(plaintext)

    def restaurar_bytes(self, conteudo: bytes) -> None:
        try:
            payload = json.loads(conteudo.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Arquivo de backup inválido.") from exc

        if payload.get("formato") != self.FORMAT:
            raise ValueError("Arquivo de backup inválido.")
        if payload.get("versao") != 1:
            raise ValueError("Versão de backup não suportada.")

        dados = payload.get("dados")
        if not isinstance(dados, dict):
            raise ValueError("Backup sem dados válidos.")

        with self.database.connect() as connection:
            connection.execute("PRAGMA foreign_keys = OFF")
            try:
                connection.execute("BEGIN")
                allowed_columns = {
                    tabela: {
                        str(row["name"])
                        for row in connection.execute(
                            f"PRAGMA table_info({tabela})"
                        ).fetchall()
                    }
                    for tabela in self.TABLES
                }

                for tabela in ("visitas", "atividades", "estudantes", "configuracoes"):
                    connection.execute(f"DELETE FROM {tabela}")

                for tabela in self.TABLES:
                    registros = dados.get(tabela, [])
                    if not isinstance(registros, list):
                        raise ValueError(f"Dados inválidos na tabela {tabela}.")

                    for registro in registros:
                        if not isinstance(registro, dict) or not registro:
                            continue

                        colunas = list(registro.keys())
                        if not set(colunas) <= allowed_columns[tabela]:
                            raise ValueError(
                                f"O backup contém campos desconhecidos em {tabela}."
                            )

                        placeholders = ", ".join("?" for _ in colunas)
                        nomes = ", ".join(f'"{coluna}"' for coluna in colunas)
                        valores = [registro[coluna] for coluna in colunas]
                        connection.execute(
                            f"INSERT INTO {tabela} ({nomes}) VALUES ({placeholders})",
                            valores,
                        )

                inconsistencias = connection.execute(
                    "PRAGMA foreign_key_check"
                ).fetchall()
                if inconsistencias:
                    raise ValueError("O backup contém relações de dados inválidas.")

                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                connection.execute("PRAGMA foreign_keys = ON")
