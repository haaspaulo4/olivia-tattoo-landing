import customtkinter as ctk
from tkinter import ttk, messagebox
from models.cliente import Cliente
from utils.helpers import formatar_data
from utils.cores import CORES


class TelaClientes(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Topo
        frame_topo = ctk.CTkFrame(self, fg_color="transparent")
        frame_topo.grid(row=0, column=0, padx=25, pady=(25, 10), sticky="ew")
        frame_topo.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame_topo, text="👥  Clientes",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=CORES["text_primary"]
        ).grid(row=0, column=0, padx=(0, 20))

        # Busca
        busca_frame = ctk.CTkFrame(frame_topo, fg_color=CORES["bg_card"], corner_radius=10)
        busca_frame.grid(row=0, column=1, padx=10, sticky="ew")

        ctk.CTkLabel(busca_frame, text="🔍", font=ctk.CTkFont(size=14)).pack(side="left", padx=(10, 5))
        self.entry_busca = ctk.CTkEntry(
            busca_frame, placeholder_text="Buscar por nome, telefone, email...",
            width=300, fg_color="transparent", border_width=0
        )
        self.entry_busca.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.entry_busca.bind("<KeyRelease>", self.buscar)

        # Botões
        btn_novo = ctk.CTkButton(
            frame_topo, text="＋  Novo Cliente",
            command=self.novo_cliente,
            fg_color=CORES["accent_gold"],
            text_color="#1a1a2e",
            hover_color="#b8942e",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8,
            height=38,
        )
        btn_novo.grid(row=0, column=2, padx=5)

        btn_recarregar = ctk.CTkButton(
            frame_topo, text="↻", width=38,
            command=self.carregar_dados,
            fg_color=CORES["bg_card"],
            hover_color=CORES["hover"],
            corner_radius=8,
            height=38,
        )
        btn_recarregar.grid(row=0, column=3, padx=5)

        # Cards de resumo
        frame_cards = ctk.CTkFrame(self, fg_color="transparent")
        frame_cards.grid(row=1, column=0, padx=25, pady=5, sticky="ew")
        frame_cards.grid_columnconfigure((0, 1, 2), weight=1)

        # Card Total
        self.card_total = ctk.CTkFrame(frame_cards, fg_color=CORES["bg_card"], corner_radius=12)
        self.card_total.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(self.card_total, text="👥  Total", font=ctk.CTkFont(size=11), text_color=CORES["text_secondary"]).pack(pady=(12, 2))
        self.label_total = ctk.CTkLabel(self.card_total, text="0", font=ctk.CTkFont(size=28, weight="bold"), text_color=CORES["accent_gold"])
        self.label_total.pack(pady=(0, 12))

        # Card Ativos
        self.card_ativos = ctk.CTkFrame(frame_cards, fg_color=CORES["bg_card"], corner_radius=12)
        self.card_ativos.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(self.card_ativos, text="✅  Ativos", font=ctk.CTkFont(size=11), text_color=CORES["text_secondary"]).pack(pady=(12, 2))
        self.label_ativos = ctk.CTkLabel(self.card_ativos, text="0", font=ctk.CTkFont(size=28, weight="bold"), text_color=CORES["success"])
        self.label_ativos.pack(pady=(0, 12))

        # Card Instagram
        self.card_insta = ctk.CTkFrame(frame_cards, fg_color=CORES["bg_card"], corner_radius=12)
        self.card_insta.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(self.card_insta, text="📸  Com Instagram", font=ctk.CTkFont(size=11), text_color=CORES["text_secondary"]).pack(pady=(12, 2))
        self.label_insta = ctk.CTkLabel(self.card_insta, text="0", font=ctk.CTkFont(size=28, weight="bold"), text_color=CORES["info"])
        self.label_insta.pack(pady=(0, 12))

        # Tabela
        frame_tabela = ctk.CTkFrame(self, fg_color=CORES["bg_card"], corner_radius=12)
        frame_tabela.grid(row=2, column=0, padx=25, pady=10, sticky="nsew")
        frame_tabela.grid_rowconfigure(0, weight=1)
        frame_tabela.grid_columnconfigure(0, weight=1)

        # Treeview com estilo
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Clientes.Treeview",
            background=CORES["bg_card"],
            foreground=CORES["text_primary"],
            fieldbackground=CORES["bg_card"],
            rowheight=36,
            font=("Segoe UI", 11),
        )
        style.configure("Clientes.Treeview.Heading",
            background=CORES["bg_secondary"],
            foreground=CORES["accent_gold"],
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
        )
        style.map("Clientes.Treeview",
            background=[("selected", CORES["hover"])],
            foreground=[("selected", CORES["text_primary"])],
        )

        self.tree = ttk.Treeview(
            frame_tabela,
            columns=("id", "nome", "telefone", "email", "instagram", "data_cadastro"),
            show="headings",
            selectmode="browse",
            style="Clientes.Treeview",
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("telefone", text="Telefone")
        self.tree.heading("email", text="Email")
        self.tree.heading("instagram", text="Instagram")
        self.tree.heading("data_cadastro", text="Cadastro")
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nome", width=250)
        self.tree.column("telefone", width=140)
        self.tree.column("email", width=200)
        self.tree.column("instagram", width=150)
        self.tree.column("data_cadastro", width=110, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<Double-1>", self.editar_cliente)
        self.tree.bind("<Delete>", self.deletar_cliente)

        # Ações
        frame_acoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_acoes.grid(row=3, column=0, padx=25, pady=(0, 20), sticky="ew")

        btn_editar = ctk.CTkButton(
            frame_acoes, text="✏️  Editar",
            command=lambda: self.editar_cliente(None),
            fg_color=CORES["bg_card"],
            hover_color=CORES["hover"],
            corner_radius=8,
        )
        btn_editar.pack(side="left", padx=5)

        btn_excluir = ctk.CTkButton(
            frame_acoes, text="🗑️  Excluir",
            fg_color=CORES["accent_burgundy"],
            hover_color="#a00000",
            corner_radius=8,
            command=lambda: self.deletar_cliente(None),
        )
        btn_excluir.pack(side="left", padx=5)

        btn_whatsapp = ctk.CTkButton(
            frame_acoes, text="📱  WhatsApp",
            fg_color="#25D366",
            hover_color="#1da851",
            text_color="#1a1a2e",
            corner_radius=8,
            command=self.abrir_whatsapp,
        )
        btn_whatsapp.pack(side="left", padx=5)

        self.carregar_dados()

    def carregar_dados(self):
        """Carrega todos os clientes na tabela."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        clientes = Cliente.listar_todos(ativos=True)
        for c in clientes:
            self.tree.insert("", "end", values=(
                c["id"], c["nome"], c["telefone"], c["email"],
                c["instagram"], formatar_data(c["data_cadastro"])
            ))

        # Atualizar cards
        total = len(clientes)
        ativos = len([c for c in clientes if c.get("ativo", 1)])
        com_insta = len([c for c in clientes if c.get("instagram")])
        self.label_total.configure(text=str(total))
        self.label_ativos.configure(text=str(ativos))
        self.label_insta.configure(text=str(com_insta))

    def buscar(self, event=None):
        termo = self.entry_busca.get()
        for item in self.tree.get_children():
            self.tree.delete(item)
        if termo:
            clientes = Cliente.buscar(termo)
        else:
            clientes = Cliente.listar_todos()
        for c in clientes:
            self.tree.insert("", "end", values=(
                c["id"], c["nome"], c["telefone"], c["email"],
                c["instagram"], formatar_data(c["data_cadastro"])
            ))

    def novo_cliente(self):
        JanelaCliente(self, None)

    def editar_cliente(self, event):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um cliente para editar.")
            return
        item = self.tree.item(selected[0])
        cliente_id = item["values"][0]
        JanelaCliente(self, cliente_id)

    def deletar_cliente(self, event):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um cliente para excluir.")
            return
        item = self.tree.item(selected[0])
        nome = item["values"][1]
        if messagebox.askyesno("Confirmar", f"Excluir cliente '{nome}'?"):
            cliente = Cliente.buscar_por_id(item["values"][0])
            if cliente:
                cliente.excluir()
                self.carregar_dados()

    def abrir_whatsapp(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um cliente para abrir WhatsApp.")
            return
        item = self.tree.item(selected[0])
        telefone = item["values"][2]
        if telefone:
            import webbrowser
            numero = telefone.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
            webbrowser.open(f"https://wa.me/55{numero}")
        else:
            messagebox.showwarning("Aviso", "Cliente não possui telefone cadastrado.")


class JanelaCliente(ctk.CTkToplevel):
    def __init__(self, parent, cliente_id=None):
        super().__init__(parent)
        self.cliente_id = cliente_id
        self.parent = parent

        if cliente_id:
            self.title("✏️  Editar Cliente")
            cliente = Cliente.buscar_por_id(cliente_id)
            self.cliente = cliente
        else:
            self.title("➕  Novo Cliente")
            self.cliente = Cliente()

        self.geometry("520x520")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self.lift()
        self.configure(fg_color=CORES["bg_primary"])

        # Formulário
        frame = ctk.CTkFrame(self, fg_color=CORES["bg_card"], corner_radius=12)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        labels = ["Nome:", "Telefone:", "Email:", "Instagram:", "Data Nascimento:", "Observações:"]
        self.entries = {}

        for i, label in enumerate(labels):
            ctk.CTkLabel(
                frame, text=label,
                font=ctk.CTkFont(size=12),
                text_color=CORES["text_secondary"]
            ).grid(row=i, column=0, padx=15, pady=8, sticky="w")

            if label == "Observações:":
                entry = ctk.CTkTextbox(frame, height=80, fg_color=CORES["bg_primary"], corner_radius=8)
                entry.grid(row=i, column=1, padx=15, pady=8, sticky="ew")
            else:
                entry = ctk.CTkEntry(frame, fg_color=CORES["bg_primary"], corner_radius=8, border_width=0)
                entry.grid(row=i, column=1, padx=15, pady=8, sticky="ew")
            self.entries[label] = entry

        frame.grid_columnconfigure(1, weight=1)

        if self.cliente_id and self.cliente:
            self.entries["Nome:"].insert(0, self.cliente.nome or "")
            self.entries["Telefone:"].insert(0, self.cliente.telefone or "")
            self.entries["Email:"].insert(0, self.cliente.email or "")
            self.entries["Instagram:"].insert(0, self.cliente.instagram or "")
            self.entries["Data Nascimento:"].insert(0, self.cliente.data_nascimento or "")
            if self.cliente.observacoes:
                self.entries["Observações:"].insert("1.0", self.cliente.observacoes)

        # Botões
        frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_botoes.pack(fill="x", padx=20, pady=(0, 20))

        btn_salvar = ctk.CTkButton(
            frame_botoes, text="💾  Salvar",
            command=self.salvar,
            fg_color=CORES["accent_gold"],
            text_color="#1a1a2e",
            hover_color="#b8942e",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8,
        )
        btn_salvar.pack(side="right", padx=5)

        btn_cancelar = ctk.CTkButton(
            frame_botoes, text="Cancelar",
            fg_color=CORES["bg_card"],
            hover_color=CORES["hover"],
            corner_radius=8,
            command=self.destroy,
        )
        btn_cancelar.pack(side="right", padx=5)

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def salvar(self):
        nome = self.entries["Nome:"].get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "Nome é obrigatório.", parent=self)
            return

        is_novo = self.cliente.id is None

        self.cliente.nome = nome
        self.cliente.telefone = self.entries["Telefone:"].get().strip()
        self.cliente.email = self.entries["Email:"].get().strip()
        self.cliente.instagram = self.entries["Instagram:"].get().strip()
        self.cliente.data_nascimento = self.entries["Data Nascimento:"].get().strip()
        self.cliente.observacoes = self.entries["Observações:"].get("1.0", "end").strip()

        self.cliente.salvar()
        
        # Enviar mensagem de boas vindas se for novo cliente e tiver WhatsApp Conectado
        if is_novo and self.cliente.telefone:
            from services import notificacoes_service
            notificacoes_service.notificar_novo_cliente(self.cliente.nome, self.cliente.telefone)

        self.parent.carregar_dados()
        messagebox.showinfo("Sucesso", "Cliente salvo com sucesso!", parent=self)
        self.destroy()