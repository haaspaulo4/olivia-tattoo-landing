from database.conexao import get_conexao
from typing import Optional, List, Dict


class Cliente:
    def __init__(self, id: Optional[int] = None, nome: str = "", telefone: str = "",
                 email: str = "", instagram: str = "", data_nascimento: str = "",
                 observacoes: str = "", data_cadastro: str = "", ativo: int = 1):
        self.id = id
        self.nome = nome
        self.telefone = telefone
        self.email = email
        self.instagram = instagram
        self.data_nascimento = data_nascimento
        self.observacoes = observacoes
        self.data_cadastro = data_cadastro
        self.ativo = ativo

    @staticmethod
    def criar_tabela():
        """Tabela já é criada pelo schema.sql"""
        pass

    def salvar(self):
        conn = get_conexao()
        try:
            if self.id:
                conn.execute("""
                    UPDATE clientes SET nome=?, telefone=?, email=?, instagram=?,
                    data_nascimento=?, observacoes=?, ativo=?
                    WHERE id=?
                """, (self.nome, self.telefone, self.email, self.instagram,
                      self.data_nascimento, self.observacoes, self.ativo, self.id))
            else:
                cursor = conn.execute("""
                    INSERT INTO clientes (nome, telefone, email, instagram,
                    data_nascimento, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (self.nome, self.telefone, self.email, self.instagram,
                      self.data_nascimento, self.observacoes))
                self.id = cursor.lastrowid
            conn.commit()
        finally:
            conn.close()

    def excluir(self):
        if not self.id:
            return
        conn = get_conexao()
        try:
            conn.execute("UPDATE clientes SET ativo=0 WHERE id=?", (self.id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def buscar_por_id(id: int) -> Optional['Cliente']:
        conn = get_conexao()
        try:
            row = conn.execute("SELECT * FROM clientes WHERE id=?", (id,)).fetchone()
            if row:
                return Cliente(**dict(row))
            return None
        finally:
            conn.close()

    @staticmethod
    def listar_todos(ativos: bool = True) -> List[Dict]:
        conn = get_conexao()
        try:
            if ativos:
                rows = conn.execute("SELECT * FROM clientes WHERE ativo=1 ORDER BY nome").fetchall()
            else:
                rows = conn.execute("SELECT * FROM clientes ORDER BY nome").fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def buscar(termo: str) -> List[Dict]:
        conn = get_conexao()
        try:
            rows = conn.execute("""
                SELECT * FROM clientes 
                WHERE ativo=1 AND (nome LIKE ? OR telefone LIKE ? OR email LIKE ? OR instagram LIKE ?)
                ORDER BY nome
            """, (f"%{termo}%", f"%{termo}%", f"%{termo}%", f"%{termo}%")).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()