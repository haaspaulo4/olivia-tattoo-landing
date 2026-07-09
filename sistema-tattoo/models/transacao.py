from database.conexao import get_conexao
from typing import Optional, List, Dict


class Transacao:
    def __init__(self, id: Optional[int] = None, tipo: str = "entrada",
                 descricao: str = "", valor: float = 0, categoria: str = "",
                 data_transacao: str = "", cliente_id: Optional[int] = None,
                 agendamento_id: Optional[int] = None,
                 forma_pagamento: str = "", observacoes: str = "",
                 data_criacao: str = ""):
        self.id = id
        self.tipo = tipo
        self.descricao = descricao
        self.valor = valor
        self.categoria = categoria
        self.data_transacao = data_transacao
        self.cliente_id = cliente_id
        self.agendamento_id = agendamento_id
        self.forma_pagamento = forma_pagamento
        self.observacoes = observacoes
        self.data_criacao = data_criacao

    def salvar(self):
        conn = get_conexao()
        try:
            if self.id:
                conn.execute("""
                    UPDATE transacoes SET tipo=?, descricao=?, valor=?,
                    categoria=?, data_transacao=?, cliente_id=?,
                    agendamento_id=?, forma_pagamento=?, observacoes=?
                    WHERE id=?
                """, (self.tipo, self.descricao, self.valor, self.categoria,
                      self.data_transacao, self.cliente_id, self.agendamento_id,
                      self.forma_pagamento, self.observacoes, self.id))
            else:
                cursor = conn.execute("""
                    INSERT INTO transacoes (tipo, descricao, valor, categoria,
                    data_transacao, cliente_id, agendamento_id, forma_pagamento,
                    observacoes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (self.tipo, self.descricao, self.valor, self.categoria,
                      self.data_transacao, self.cliente_id, self.agendamento_id,
                      self.forma_pagamento, self.observacoes))
                self.id = cursor.lastrowid
            conn.commit()
        finally:
            conn.close()

    def excluir(self):
        if not self.id:
            return
        conn = get_conexao()
        try:
            conn.execute("DELETE FROM transacoes WHERE id=?", (self.id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def buscar_por_id(id: int) -> Optional['Transacao']:
        conn = get_conexao()
        try:
            row = conn.execute("SELECT * FROM transacoes WHERE id=?", (id,)).fetchone()
            if row:
                return Transacao(**dict(row))
            return None
        finally:
            conn.close()

    @staticmethod
    def listar_por_periodo(data_inicio: str, data_fim: str) -> List[Dict]:
        conn = get_conexao()
        try:
            rows = conn.execute("""
                SELECT t.*, c.nome as cliente_nome
                FROM transacoes t
                LEFT JOIN clientes c ON t.cliente_id = c.id
                WHERE t.data_transacao >= ? AND t.data_transacao <= ?
                ORDER BY t.data_transacao DESC
            """, (data_inicio, data_fim)).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def listar_todos() -> List[Dict]:
        conn = get_conexao()
        try:
            rows = conn.execute("""
                SELECT t.*, c.nome as cliente_nome
                FROM transacoes t
                LEFT JOIN clientes c ON t.cliente_id = c.id
                ORDER BY t.data_transacao DESC
            """).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def resumo_mensal(ano: int, mes: int) -> Dict:
        conn = get_conexao()
        try:
            data_inicio = f"{ano:04d}-{mes:02d}-01"
            if mes == 12:
                data_fim = f"{ano + 1:04d}-01-01"
            else:
                data_fim = f"{ano:04d}-{mes + 1:02d}-01"

            entradas = conn.execute("""
                SELECT COALESCE(SUM(valor), 0) as total
                FROM transacoes
                WHERE tipo='entrada' AND data_transacao >= ? AND data_transacao < ?
            """, (data_inicio, data_fim)).fetchone()["total"]

            saidas = conn.execute("""
                SELECT COALESCE(SUM(valor), 0) as total
                FROM transacoes
                WHERE tipo='saida' AND data_transacao >= ? AND data_transacao < ?
            """, (data_inicio, data_fim)).fetchone()["total"]

            return {
                "entradas": entradas,
                "saidas": saidas,
                "saldo": entradas - saidas
            }
        finally:
            conn.close()

    @staticmethod
    def listar_por_cliente(cliente_id: int) -> List[Dict]:
        conn = get_conexao()
        try:
            rows = conn.execute("""
                SELECT t.*, c.nome as cliente_nome
                FROM transacoes t
                LEFT JOIN clientes c ON t.cliente_id = c.id
                WHERE t.cliente_id = ?
                ORDER BY t.data_transacao DESC
            """, (cliente_id,)).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()