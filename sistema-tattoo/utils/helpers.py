import datetime
import os
from pathlib import Path
from database.conexao import get_conexao


def formatar_data(data_str):
    """Formata data ISO para formato brasileiro."""
    if not data_str:
        return ""
    try:
        data = datetime.datetime.strptime(data_str, "%Y-%m-%d")
        return data.strftime("%d/%m/%Y")
    except ValueError:
        return data_str


def formatar_moeda(valor):
    """Formata valor para moeda brasileira."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def data_atual_iso():
    """Retorna data atual no formato ISO."""
    return datetime.date.today().isoformat()


def carregar_config(chave):
    """Carrega uma configuração do banco."""
    conn = get_conexao()
    try:
        row = conn.execute(
            "SELECT valor FROM configuracoes WHERE chave=?", (chave,)
        ).fetchone()
        return row["valor"] if row else ""
    finally:
        conn.close()


def salvar_config(chave, valor):
    """Salva uma configuração no banco."""
    conn = get_conexao()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES (?, ?)",
            (chave, valor),
        )
        conn.commit()
    finally:
        conn.close()


def get_assets_path():
    """Retorna caminho da pasta assets."""
    path = Path(__file__).parent.parent / "assets"
    os.makedirs(path, exist_ok=True)
    return path


def get_icon_path(nome):
    """Retorna caminho para um ícone."""
    return str(Path(__file__).parent.parent / "icons" / nome)