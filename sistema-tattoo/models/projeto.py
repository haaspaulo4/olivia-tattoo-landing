from database.conexao import get_conexao
from typing import Optional, List, Dict


class Projeto:
    def __init__(self, id: Optional[int] = None, cliente_id: int = 0,
                 nome: str = "", descricao: str = "", valor: float = 0,
                 status: str = "rascunho", foto_antes: str = "",
                 foto_depois: str = "", data_criacao: str = ""):
        self.id = id
        self.cliente_id = cliente_id
        self.nome = nome
        self.descricao = descricao
        self.valor = valor
        self.status = status
        self.foto_antes = foto_antes
        self.foto_depois = foto_depois
        self.data_criacao = data_criacao

    def salvar(self):
        conn = get_conexao()
        try:
            if self.id:
                conn.execute("""
                    UPDATE projetos SET cliente_id=?, nome=?, descricao=?,
                    valor=?, status=?, foto_antes=?, foto_depois=?
                    WHERE id=?
                """, (self.cliente_id, self.nome, self.descricao, self.valor,
                      self.status, self.foto_antes, self.foto_depois, self.id))
            else:
                cursor = conn.execute("""
                    INSERT INTO projetos (cliente_id, nome, descricao, valor,
                    status, foto_antes, foto_depois)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (self.cliente_id, self.nome, self.descricao, self.valor,
                      self.status, self.foto_antes, self.foto_depois))
                self.id = cursor.lastrowid
            conn.commit()
        finally:
            conn.close()

    def excluir(self):
        if not self.id:
            return
        conn = get_conexao()
        try:
            conn.execute("DELETE FROM projetos WHERE id=?", (self.id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def buscar_por_id(id: int) -> Optional['Projeto']:
        conn = get_conexao()
        try:
            row = conn.execute("SELECT * FROM projetos WHERE id=?", (id,)).fetchone()
            if row:
                return Projeto(**dict(row))
            return None
        finally:
            conn.close()

    @staticmethod
    def listar_por_cliente(cliente_id: int) -> List[Dict]:
        conn = get_conexao()
        try:
            rows = conn.execute("""
                SELECT p.*, c.nome as cliente_nome
                FROM projetos p
                JOIN clientes c ON p.cliente_id = c.id
                WHERE p.cliente_id = ?
                ORDER BY p.data_criacao DESC
            """, (cliente_id,)).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def listar_todos() -> List[Dict]:
        conn = get_conexao()
        try:
            rows = conn.execute("""
                SELECT p.*, c.nome as cliente_nome
                FROM projetos p
                JOIN clientes c ON p.cliente_id = c.id
                ORDER BY p.data_criacao DESC
            """).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()