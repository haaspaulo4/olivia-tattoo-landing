import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "sistema_tattoo.db"


def get_conexao():
    """Retorna uma conexão com o banco de dados SQLite."""
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_banco():
    """Cria as tabelas do banco de dados se não existirem."""
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = f.read()

    conn = get_conexao()
    try:
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()