import customtkinter as ctk
from tkinter import ttk
import datetime
from models.cliente import Cliente
from models.agendamento import Agendamento
from models.transacao import Transacao
from utils.helpers import formatar_data, formatar_moeda
from utils.cores import CORES

# Matplotlib é opcional
HAS_MATPLOTLIB = False
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib
    matplotlib.use("TkAgg")
    HAS_MATPLOTLIB = True
except ImportError:
    pass


class TelaRelatorios(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Topo
        frame_topo = ctk.CTkFrame(self, fg_color="transparent")
        frame_topo.grid(row=0, column=0, padx=25, pady=(25, 10), sticky="ew")

        ctk.CTkLabel(
            frame_topo, text="📊  Relatórios",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=CORES["text_primary"]
        ).pack(side="left", padx=(0, 20))

        # Cards de resumo
        frame_cards = ctk.CTkFrame(self, fg_color="transparent")
        frame_cards.grid(row=1, column=0, padx=25, pady=5, sticky="ew")
        frame_cards.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Card Clientes
        card_clientes = ctk.CTkFrame(frame_cards, fg_color=CORES["bg_card"], corner_radius=12)
        card_clientes.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(card_clientes, text="👥  Clientes", font=ctk.CTkFont(size=11),
                     text_color=CORES["text_secondary"]).pack(pady=(12, 2))
        self.label_total_clientes = ctk.CTkLabel(card_clientes, text="0",
            font=ctk.CTkFont(size=28, weight="bold"), text_color=CORES["accent_gold"])
        self.label_total_clientes.pack(pady=(0, 12))

        # Card Agenda
        card_agenda = ctk.CTkFrame(frame_cards, fg_color=CORES["bg_card"], corner_radius=12)
        card_agenda.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(card_agenda, text="📅  Agenda Mês", font=ctk.CTkFont(size=11),
                     text_color=CORES["text_secondary"]).pack(pady=(12, 2))
        self.label_agenda_mes = ctk.CTkLabel(card_agenda, text="0",
            font=ctk.CTkFont(size=28, weight="bold"), text_color=CORES["info"])
        self.label_agenda_mes.pack(pady=(0, 12))

        # Card Entradas
        card_entradas = ctk.CTkFrame(frame_cards, fg_color="#1a3a2a", corner_radius=12)
        card_entradas.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(card_entradas, text="💰  Entradas Mês", font=ctk.CTkFont(size=11),
                     text_color=CORES["success"]).pack(pady=(12, 2))
        self.label_entradas_mes = ctk.CTkLabel(card_entradas, text="R$ 0,00",
            font=ctk.CTkFont(size=20, weight="bold"), text_color=CORES["success"])
        self.label_entradas_mes.pack(pady=(0, 12))

        # Card Saídas
        card_saidas = ctk.CTkFrame(frame_cards, fg_color="#3a1a1a", corner_radius=12)
        card_saidas.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(card_saidas, text="📤  Saídas Mês", font=ctk.CTkFont(size=11),
                     text_color=CORES["danger"]).pack(pady=(12, 2))
        self.label_saidas_mes = ctk.CTkLabel(card_saidas, text="R$ 0,00",
            font=ctk.CTkFont(size=20, weight="bold"), text_color=CORES["danger"])
        self.label_saidas_mes.pack(pady=(0, 12))

        # Conteúdo principal: Gráfico + Abas
        frame_conteudo = ctk.CTkFrame(self, fg_color="transparent")
        frame_conteudo.grid(row=2, column=0, padx=25, pady=10, sticky="nsew")
        frame_conteudo.grid_columnconfigure(0, weight=1)
        frame_conteudo.grid_columnconfigure(1, weight=1)
        frame_conteudo.grid_rowconfigure(0, weight=1)

        # Gráfico de evolução mensal
        frame_grafico = ctk.CTkFrame(frame_conteudo, fg_color=CORES["bg_card"], corner_radius=12)
        frame_grafico.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        frame_grafico.grid_rowconfigure(1, weight=1)
        frame_grafico.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_grafico, text="Evolução Financeira (últimos 6 meses)",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CORES["text_secondary"]).grid(row=0, column=0, pady=(10, 0))

        if HAS_MATPLOTLIB:
            self.fig = Figure(figsize=(4, 3), dpi=80, facecolor=CORES["bg_card"])
            self.ax = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=frame_grafico)
            self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        else:
            ctk.CTkLabel(
                frame_grafico, text="📊\nInstale matplotlib\npara ver gráficos",
                font=ctk.CTkFont(size=12), text_color=CORES["text_secondary"]
            ).grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Abas
        self.tab_view = ctk.CTkTabview(frame_conteudo, fg_color=CORES["bg_card"])
        self.tab_view.grid(row=0, column=1, sticky="nsew")

        # Aba Clientes Recentes
        tab_clientes = self.tab_view.add("👥  Clientes")
        tab_clientes.grid_rowconfigure(0, weight=1)
        tab_clientes.grid_columnconfigure(0, weight=1)

        self.tree_clientes = ttk.Treeview(
            tab_clientes,
            columns=("nome", "telefone", "instagram", "data"),
            show="headings", selectmode="browse", height=12,
        )
        style_clientes = ttk.Style()
        style_clientes.theme_use("clam")
        style_clientes.configure("RelClientes.Treeview",
            background=CORES["bg_card"], foreground=CORES["text_primary"],
            fieldbackground=CORES["bg_card"], rowheight=28,
            font=("Segoe UI", 9),
        )
        style_clientes.configure("RelClientes.Treeview.Heading",
            background=CORES["bg_secondary"], foreground=CORES["accent_gold"],
            font=("Segoe UI", 8, "bold"), borderwidth=0,
        )
        style_clientes.map("RelClientes.Treeview",
            background=[("selected", CORES["hover"])],
            foreground=[("selected", CORES["text_primary"])],
        )

        for col in ("nome", "telefone", "instagram", "data"):
            self.tree_clientes.heading(col, text=col.capitalize())
        self.tree_clientes.column("nome", width=150)
        self.tree_clientes.column("telefone", width=100)
        self.tree_clientes.column("instagram", width=120)
        self.tree_clientes.column("data", width=80, anchor="center")
        self.tree_clientes.grid(row=0, column=0, sticky="nsew")

        # Aba Transações
        tab_transacoes = self.tab_view.add("💰  Transações")
        tab_transacoes.grid_rowconfigure(0, weight=1)
        tab_transacoes.grid_columnconfigure(0, weight=1)

        self.tree_transacoes = ttk.Treeview(
            tab_transacoes,
            columns=("data", "tipo", "descricao", "valor"),
            show="headings", selectmode="browse", height=12,
        )
        for col in ("data", "tipo", "descricao", "valor"):
            self.tree_transacoes.heading(col, text=col.capitalize())
        self.tree_transacoes.column("data", width=80, anchor="center")
        self.tree_transacoes.column("tipo", width=70, anchor="center")
        self.tree_transacoes.column("descricao", width=200)
        self.tree_transacoes.column("valor", width=100, anchor="e")
        self.tree_transacoes.grid(row=0, column=0, sticky="nsew")

        # Aba Agenda
        tab_agenda = self.tab_view.add("📅  Agenda")
        tab_agenda.grid_rowconfigure(0, weight=1)
        tab_agenda.grid_columnconfigure(0, weight=1)

        self.tree_agenda = ttk.Treeview(
            tab_agenda,
            columns=("data", "horario", "cliente", "status"),
            show="headings", selectmode="browse", height=12,
        )
        for col in ("data", "horario", "cliente", "status"):
            self.tree_agenda.heading(col, text=col.capitalize())
        self.tree_agenda.column("data", width=90, anchor="center")
        self.tree_agenda.column("horario", width=60, anchor="center")
        self.tree_agenda.column("cliente", width=200)
        self.tree_agenda.column("status", width=80, anchor="center")
        self.tree_agenda.grid(row=0, column=0, sticky="nsew")

        self.atualizar_dados()

    def atualizar_dados(self):
        """Atualiza todos os dados dos relatórios."""
        hoje = datetime.date.today()
        ano, mes = hoje.year, hoje.month

        # Cards
        clientes = Cliente.listar_todos(ativos=True)
        self.label_total_clientes.configure(text=str(len(clientes)))

        agendamentos_mes = Agendamento.listar_por_mes(ano, mes)
        self.label_agenda_mes.configure(text=str(len(agendamentos_mes)))

        resumo = Transacao.resumo_mensal(ano, mes)
        self.label_entradas_mes.configure(text=formatar_moeda(resumo["entradas"]))
        self.label_saidas_mes.configure(text=formatar_moeda(resumo["saidas"]))

        # Gráfico de evolução
        self.atualizar_grafico_evolucao()

        # Últimos clientes
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        for c in clientes[-10:]:
            self.tree_clientes.insert("", "end", values=(
                c["nome"], c["telefone"], c["instagram"],
                formatar_data(c["data_cadastro"])
            ))

        # Últimas 20 transações
        for item in self.tree_transacoes.get_children():
            self.tree_transacoes.delete(item)
        transacoes = Transacao.listar_todos()[:20]
        for t in transacoes:
            cor_tipo = "🟢 ENTRADA" if t["tipo"] == "entrada" else "🔴 SAÍDA"
            self.tree_transacoes.insert("", "end", values=(
                formatar_data(t["data_transacao"]), cor_tipo,
                t["descricao"], formatar_moeda(t["valor"])
            ))

        # Próximos agendamentos
        for item in self.tree_agenda.get_children():
            self.tree_agenda.delete(item)
        agendamentos = Agendamento.listar_todos(status="confirmada")[:15]
        for ag in agendamentos:
            self.tree_agenda.insert("", "end", values=(
                formatar_data(ag["data_sessao"]), ag["horario"][:5],
                ag.get("cliente_nome", "-"), "🟢 Confirmada"
            ))

    def atualizar_grafico_evolucao(self):
        """Gera gráfico de barras com evolução dos últimos 6 meses."""
        if not HAS_MATPLOTLIB:
            return
        self.ax.clear()
        hoje = datetime.date.today()

        meses = []
        entradas_meses = []
        saidas_meses = []
        meses_pt = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                     "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

        for i in range(5, -1, -1):
            m = hoje.month - i
            a = hoje.year
            while m < 1:
                m += 12
                a -= 1
            while m > 12:
                m -= 12
                a += 1

            meses.append(meses_pt[m - 1])
            resumo = Transacao.resumo_mensal(a, m)
            entradas_meses.append(resumo["entradas"])
            saidas_meses.append(resumo["saidas"])

        x = range(len(meses))
        width = 0.35

        bars1 = self.ax.bar([i - width/2 for i in x], entradas_meses, width,
                           label="Entradas", color=CORES["success"], alpha=0.8)
        bars2 = self.ax.bar([i + width/2 for i in x], saidas_meses, width,
                           label="Saídas", color=CORES["danger"], alpha=0.8)

        self.ax.set_xlabel("")
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(meses, color='#a0a0b0', fontsize=8)
        self.ax.legend(loc='upper left', fontsize=8, facecolor=CORES["bg_card"],
                      edgecolor='none', labelcolor='#a0a0b0')
        self.ax.set_facecolor(CORES["bg_card"])
        self.ax.tick_params(colors='#a0a0b0', labelsize=8)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#2a3a5c')
        self.ax.spines['bottom'].set_color('#2a3a5c')

        self.fig.tight_layout()
        self.canvas.draw()