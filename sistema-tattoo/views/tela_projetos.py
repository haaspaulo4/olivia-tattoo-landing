import customtkinter as ctk
from tkinter import ttk, messagebox
from models.projeto import Projeto
from models.cliente import Cliente
from utils.helpers import formatar_data, formatar_moeda


class TelaProjetos(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Topo
        frame_topo = ctk.CTkFrame(self)
        frame_topo.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        frame_topo.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame_topo, text="🎨  Projetos", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=(0, 20))

        btn_novo = ctk.CTkButton(frame_topo, text="+ Novo Projeto", command=self.novo_projeto)
        btn_novo.grid(row=0, column=2, padx=5)

        btn_recarregar = ctk.CTkButton(frame_topo, text="↻", width=40, command=self.carregar_dados)
        btn_recarregar.grid(row=0, column=3, padx=5)

        # Tabela
        frame_tabela = ctk.CTkFrame(self)
        frame_tabela.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        frame_tabela.grid_rowconfigure(0, weight=1)
        frame_tabela.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            frame_tabela,
            columns=("id", "cliente", "nome", "descricao", "valor", "status", "data"),
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("cliente", text="Cliente")
        self.tree.heading("nome", text="Projeto")
        self.tree.heading("descricao", text="Descrição")
        self.tree.heading("valor", text="Valor")
        self.tree.heading("status", text="Status")
        self.tree.heading("data", text="Criação")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("cliente", width=150)
        self.tree.column("nome", width=200)
        self.tree.column("descricao", width=250)
        self.tree.column("valor", width=120, anchor="e")
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("data", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Ações
        frame_acoes = ctk.CTkFrame(self)
        frame_acoes.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")

        ctk.CTkButton(frame_acoes, text="✏️  Editar", command=lambda: self.editar_projeto()).pack(side="left", padx=5)
        ctk.CTkButton(frame_acoes, text="🗑️  Excluir", fg_color="#c0392b", hover_color="#e74c3c",
                       command=lambda: self.excluir_projeto()).pack(side="left", padx=5)

        self.carregar_dados()

    def carregar_dados(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        projetos = Projeto.listar_todos()
        for p in projetos:
            status_icon = {"rascunho": "📝", "aprovado": "✅", "realizado": "🎯"}
            self.tree.insert("", "end", values=(
                p["id"], p.get("cliente_nome", "-"), p["nome"],
                p["descricao"][:80] + "..." if p["descricao"] and len(p["descricao"]) > 80 else (p["descricao"] or ""),
                formatar_moeda(p["valor"]),
                f"{status_icon.get(p['status'], '')} {p['status'].upper()}",
                formatar_data(p["data_criacao"]),
            ))

    def novo_projeto(self):
        JanelaProjeto(self, None)

    def editar_projeto(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um projeto.")
            return
        item = self.tree.item(selected[0])
        JanelaProjeto(self, item["values"][0])

    def excluir_projeto(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um projeto.")
            return
        item = self.tree.item(selected[0])
        if messagebox.askyesno("Confirmar", f"Excluir projeto '{item['values'][2]}'?"):
            projeto = Projeto.buscar_por_id(item["values"][0])
            if projeto:
                projeto.excluir()
                self.carregar_dados()


class JanelaProjeto(ctk.CTkToplevel):
    def __init__(self, parent, projeto_id=None):
        super().__init__(parent)
        self.projeto_id = projeto_id
        self.parent = parent

        if projeto_id:
            self.title("Editar Projeto")
            projeto = Projeto.buscar_por_id(projeto_id)
            self.projeto = projeto
        else:
            self.title("Novo Projeto")
            self.projeto = Projeto()

        self.geometry("500x450")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self.lift()

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Cliente:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.combo_cliente = ctk.CTkComboBox(frame, values=[], width=300)
        self.combo_cliente.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.carregar_clientes()

        ctk.CTkLabel(frame, text="Nome do Projeto:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_nome = ctk.CTkEntry(frame)
        self.entry_nome.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(frame, text="Descrição:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_descricao = ctk.CTkTextbox(frame, height=80)
        self.entry_descricao.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(frame, text="Valor (R$):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.entry_valor = ctk.CTkEntry(frame)
        self.entry_valor.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(frame, text="Status:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.combo_status = ctk.CTkComboBox(frame, values=["rascunho", "aprovado", "realizado"], width=300)
        self.combo_status.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(frame, text="Foto Antes (caminho):").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.entry_foto_antes = ctk.CTkEntry(frame)
        self.entry_foto_antes.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(frame, text="Foto Depois (caminho):").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.entry_foto_depois = ctk.CTkEntry(frame)
        self.entry_foto_depois.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        frame.grid_columnconfigure(1, weight=1)

        if self.projeto_id and self.projeto:
            self.combo_cliente.set(str(self.projeto.cliente_id))
            self.entry_nome.insert(0, self.projeto.nome or "")
            if self.projeto.descricao:
                self.entry_descricao.insert("1.0", self.projeto.descricao)
            self.entry_valor.insert(0, str(self.projeto.valor or ""))
            self.combo_status.set(self.projeto.status or "rascunho")
            self.entry_foto_antes.insert(0, self.projeto.foto_antes or "")
            self.entry_foto_depois.insert(0, self.projeto.foto_depois or "")

        frame_botoes = ctk.CTkFrame(self)
        frame_botoes.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(frame_botoes, text="💾  Salvar", command=self.salvar).pack(side="right", padx=5)
        ctk.CTkButton(frame_botoes, text="Cancelar", fg_color="gray", command=self.destroy).pack(side="right", padx=5)

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def carregar_clientes(self):
        clientes = Cliente.listar_todos()
        self.clientes_dict = {}
        for c in clientes:
            label = f"{c['id']} - {c['nome']}"
            self.clientes_dict[label] = c["id"]
        self.combo_cliente.configure(values=list(self.clientes_dict.keys()))

    def salvar(self):
        cliente_selecionado = self.combo_cliente.get()
        if not cliente_selecionado or cliente_selecionado not in self.clientes_dict:
            messagebox.showwarning("Aviso", "Selecione um cliente.", parent=self)
            return

        nome = self.entry_nome.get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "Nome do projeto é obrigatório.", parent=self)
            return

        try:
            valor = float(self.entry_valor.get().replace(",", ".") or 0)
        except ValueError:
            valor = 0

        self.projeto.cliente_id = self.clientes_dict[cliente_selecionado]
        self.projeto.nome = nome
        self.projeto.descricao = self.entry_descricao.get("1.0", "end").strip()
        self.projeto.valor = valor
        self.projeto.status = self.combo_status.get()
        self.projeto.foto_antes = self.entry_foto_antes.get().strip()
        self.projeto.foto_depois = self.entry_foto_depois.get().strip()

        self.projeto.salvar()
        self.parent.carregar_dados()
        messagebox.showinfo("Sucesso", "Projeto salvo com sucesso!", parent=self)
        self.destroy()