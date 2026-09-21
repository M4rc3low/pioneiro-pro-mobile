import sqlite3

from pioneiro_pro.database import Database
from pioneiro_pro.repositories import AtividadeRepository, EstudanteRepository
from pioneiro_pro.services import BackupService


def test_migracao_adiciona_campos_novos_sem_perder_dados(tmp_path):
    path = tmp_path / "legado.db"

    with sqlite3.connect(path) as connection:
        connection.executescript(
            """
            CREATE TABLE atividades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                tipo TEXT NOT NULL,
                minutos INTEGER NOT NULL DEFAULT 0,
                observacao TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE estudantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'ativo',
                observacao TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE visitas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estudante_id INTEGER,
                data TEXT NOT NULL,
                horario TEXT NOT NULL DEFAULT '',
                tipo TEXT NOT NULL DEFAULT 'estudo',
                observacao TEXT NOT NULL DEFAULT '',
                concluida INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            );

            INSERT INTO atividades (data, tipo, minutos, observacao)
            VALUES ('2026-09-21', 'ministerio', 60, 'Legado');

            INSERT INTO estudantes (nome, telefone)
            VALUES ('Maria', '11999999999');
            """
        )

    db = Database(path)
    db.initialize()

    atividades = AtividadeRepository(db)
    estudantes = EstudanteRepository(db)

    assert atividades.listar()[0]["minutos"] == 60
    assert estudantes.listar()[0]["nome"] == "Maria"

    with db.connect() as connection:
        atividade_cols = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(atividades)").fetchall()
        }
        estudante_cols = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(estudantes)").fetchall()
        }

    assert {"brochuras", "folhetos", "outras_publicacoes"} <= atividade_cols
    assert {"latitude", "longitude", "raio_alerta_m", "alerta_proximidade"} <= estudante_cols


def test_backup_preserva_publicacoes_e_localizacao(tmp_path):
    origem = Database(tmp_path / "origem.db")
    origem.initialize()

    atividades_origem = AtividadeRepository(origem)
    estudantes_origem = EstudanteRepository(origem)

    atividades_origem.criar(
        "2026-09-21",
        "ministerio",
        90,
        brochuras=4,
        folhetos=7,
        outras_publicacoes=2,
    )
    estudante_id = estudantes_origem.criar("Ana")
    estudantes_origem.atualizar_localizacao(
        estudante_id,
        -23.588,
        -46.681,
        300,
    )

    conteudo = BackupService(origem).exportar_bytes()

    destino = Database(tmp_path / "destino.db")
    destino.initialize()
    BackupService(destino).restaurar_bytes(conteudo)

    atividade = AtividadeRepository(destino).listar()[0]
    estudante = EstudanteRepository(destino).listar()[0]

    assert atividade["brochuras"] == 4
    assert atividade["folhetos"] == 7
    assert atividade["outras_publicacoes"] == 2
    assert estudante["latitude"] == -23.588
    assert estudante["longitude"] == -46.681
    assert estudante["raio_alerta_m"] == 300
