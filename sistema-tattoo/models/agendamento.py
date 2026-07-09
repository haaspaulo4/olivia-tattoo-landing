from database.conexao import get_conexao
from typing import Optional, List, Dict


class Agendamento:
    def __init__(self, id: Optional[int] = None, cliente_id: int = 0,
                 data_sessao: str = "", horario: str = "", descricao: str = "",
                 valor_total: float = 0, valor_entrada: float = 0,
                 status: str = "confirmada", observacoes: str = "",
                 data_criacao: str = ""):
        self.id = id
        self.cliente_id = cliente_id
        self.data_sessao = data_sessao
        self.horario = horario
        self.descricao = descricao
        self.valor_total = valor_total
        self.valor_entrada = valor_entrada
        self.status = status
        self.observacoes = observacoes
        self.data_criacao = data_criacao

    def salvar(self):
        conn = get_conexao()
        try:
            if self.id:
                conn.execute("""
                    UPDATE agendamentos SET cliente_id=?, data_sessao=?, horario=?,
                    descricao=?, valor_total=?, valor_entrada=?, status=?, observacoes=?
                    WHERE id=?
                """, (self.cliente_id, self.data_sessao, self.horario, self.descricao,
                      self.valor_total, self.valor_entrada, self.status,
                      self.observacoes, self.id))
            else:
                cursor = conn.execute("""
                    INSERT INTO agendamentos (cliente_id, data_sessao, horario,
                    descricao, valor_total, valor_entrada, status, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (self.cliente_id, self.data_sessao, self.horario, self.descricao,
                      self.valor_total, self.valor_entrada, self.status, self.observacoes))
                self.id = cursor.lastrowid
            conn.commit()
        finally:
            conn.close()

    def excluir(self):
        if not self.id:
            return
        conn = get_conexao()
        try:
            conn.execute("DELETE FROM agendamentos WHERE id=?", (self.id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def buscar_por_id(id: int) -> Optional['Agendamento']:
        conn = get_conexao()
        try:
            row = conn.execute("SELECT * FROM agendamentos WHERE id=?", (id,)).fetchone()
            if row:
                return Agendamento(**dict(row))
            return None
        finally:
            conn.close()

    @staticmethod
    def listar_por_data(data: str) -> List[Dict]:
        conn = get_conexao()
        try:
            rows = conn.execute("""
                SELECT a.*, c.nome as cliente_nome
                FROM agendamentos a
                JOIN clientes c ON a.cliente_id = c.id
                WHERE a.data_sessao = ?
                ORDER BY a.horario
            """, (data,)).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def listar_por_mes(ano: int, mes: int) -> List[Dict]:
        conn = get_conexao()
        try:
            data_inicio = f"{ano:04d}-{mes:02d}-01"
            if mes == 12:
                data_fim = f"{ano + 1:04d}-01-01"
            else:
                data_fim = f"{ano:04d}-{mes + 1:02d}-01"
            rows = conn.execute("""
                SELECT a.*, c.nome as cliente_nome
                FROM agendamentos a
                JOIN clientes c ON a.cliente_id = c.id
                WHERE a.data_sessao >= ? AND a.data_sessao < ?
                ORDER BY a.data_sessao, a.horario
            """, (data_inicio, data_fim)).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def listar_por_cliente(cliente_id: int) -> List[Dict]:
        conn = get_conexao()
        try:
            rows = conn.execute("""
                SELECT a.*, c.nome as cliente_nome
                FROM agendamentos a
                JOIN clientes c ON a.cliente_id = c.id
                WHERE a.cliente_id = ?
                ORDER BY a.data_sessao DESC
            """, (cliente_id,)).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def listar_todos(status: Optional[str] = None) -> List[Dict]:
        conn = get_conexao()
        try:
            if status:
                rows = conn.execute("""
                    SELECT a.*, c.nome as cliente_nome
                    FROM agendamentos a
                    JOIN clientes c ON a.cliente_id = c.id
                    WHERE a.status = ?
                    ORDER BY a.data_sessao DESC, a.horario
                """, (status,)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT a.*, c.nome as cliente_nome
                    FROM agendamentos a
                    JOIN clientes c ON a.cliente_id = c.id
                    ORDER BY a.data_sessao DESC, a.horario
                """).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()