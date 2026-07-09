import customtkinter as ctk
from tkinter import ttk, messagebox
import datetime
from models.transacao import Transacao
from utils.helpers import formatar_data, formatar_moeda
from utils.cores import CORES

# Matplotlib é opcional - gráficos não quebram se não estiver instalado
HAS_MATPLOTLIB = False
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib
    matplotlib.use("TkAgg")
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rcParams['text.color'] = '#e8e8e8'
    HAS_MATPLOTLIB = True
except ImportError:
    pass


class TelaFinanceiro(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        hoje = datetime.date.today()
        self.ano = hoje.year
        self.mes = hoje.month

        # Topo
        frame_topo = ctk.CTkFrame(self, fg_color="transparent")
        frame_topo.grid(row=0, column=0, padx=25, pady=(25, 10), sticky="ew")
        frame_topo.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame_topo, text="💰  Financeiro",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=CORES["text_primary"]
        ).grid(row=0, column=0, padx=(0, 20))

        # Navegação mês
        frame_mes = ctk.CTkFrame(frame_topo, fg_color=CORES["bg_card"], corner_radius=10)
        frame_mes.grid(row=0, column=1)

        btn_ant = ctk.CTkButton(frame_mes, text="◀", width=36, command=self.mes_anterior,
                                fg_color="transparent", hover_color=CORES["hover"], corner_radius=6)
        btn_ant.pack(side="left", padx=2)

        meses_pt = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                     "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.label_mes = ctk.CTkLabel(frame_mes, text=f"{meses_pt[self.mes - 1]} {self.ano}",
                                      font=ctk.CTkFont(size=14, weight="bold"))
        self.label_mes.pack(side="left", padx=15)

        btn_prox = ctk.CTkButton(frame_mes, text="▶", width=36, command=self.proximo_mes,
                                 fg_color="transparent", hover_color=CORES["hover"], corner_radius=6)
        btn_prox.pack(side="left", padx=2)

        btn_nova = ctk.CTkButton(
            frame_topo, text="＋  Nova Transação",
            command=self.nova_transacao,
            fg_color=CORES["accent_gold"],
            text_color="#1a1a2e",
            hover_color="#b8942e",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8,
            height=38,
        )
        btn_nova.grid(row=0, column=2, padx=5)

        # Resumo cards
        frame_resumo = ctk.CTkFrame(self, fg_color="transparent")
        frame_resumo.grid(row=1, column=0, padx=25, pady=5, sticky="ew")
        frame_resumo.grid_columnconfigure((0, 1, 2), weight=1)

        # Card Entradas
        card_ent = ctk.CTkFrame(frame_resumo, fg_color="#1a3a2a", corner_radius=12)
        card_ent.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(card_ent, text="💰  Entradas", font=ctk.CTkFont(size=11),
                     text_color=CORES["success"]).pack(pady=(12, 2))
        self.label_entradas = ctk.CTkLabel(card_ent, text="R$ 0,00",
                                           font=ctk.CTkFont(size=22, weight="bold"),
                                           text_color=CORES["success"])
        self.label_entradas.pack(pady=(0, 12))

        # Card Saídas
        card_sai = ctk.CTkFrame(frame_resumo, fg_color="#3a1a1a", corner_radius=12)
        card_sai.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(card_sai, text="📤  Saídas", font=ctk.CTkFont(size=11),
                     text_color=CORES["danger"]).pack(pady=(12, 2))
        self.label_saidas = ctk.CTkLabel(card_sai, text="R$ 0,00",
                                         font=ctk.CTkFont(size=22, weight="bold"),
                                         text_color=CORES["danger"])
        self.label_saidas.pack(pady=(0, 12))

        # Card Saldo
        card_saldo = ctk.CTkFrame(frame_resumo, fg_color=CORES["bg_card"], corner_radius=12)
        card_saldo.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(card_saldo, text="⚖️  Saldo", font=ctk.CTkFont(size=11),
                     text_color=CORES["text_secondary"]).pack(pady=(12, 2))
        self.label_saldo = ctk.CTkLabel(card_saldo, text="R$ 0,00",
                                        font=ctk.CTkFont(size=22, weight="bold"),
                                        text_color=CORES["accent_gold"])
        self.label_saldo.pack(pady=(0, 12))

        # Conteúdo dividido: Gráfico + Tabela
        frame_conteudo = ctk.CTkFrame(self, fg_color="transparent")
        frame_conteudo.grid(row=2, column=0, padx=25, pady=10, sticky="nsew")
        frame_conteudo.grid_columnconfigure(0, weight=1)
        frame_conteudo.grid_columnconfigure(1, weight=2)
        frame_conteudo.grid_rowconfigure(0, weight=1)

        # Gráfico
        frame_grafico = ctk.CTkFrame(frame_conteudo, fg_color=CORES["bg_card"], corner_radius=12)
        frame_grafico.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        frame_grafico.grid_rowconfigure(0, weight=1)
        frame_grafico.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_grafico, text="Distribuição", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CORES["text_secondary"]).grid(row=0, column=0, pady=(10, 0))

        if HAS_MATPLOTLIB:
            self.fig = Figure(figsize=(3, 3), dpi=80, facecolor=CORES["bg_card"])
            self.ax = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=frame_grafico)
            self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        else:
            self.grafico_placeholder = ctk.CTkLabel(
                frame_grafico, text="📊\nInstale matplotlib\npara ver gráficos",
                font=ctk.CTkFont(size=12), text_color=CORES["text_secondary"]
            )
            self.grafico_placeholder.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Tabela
        frame_tabela = ctk.CTkFrame(frame_conteudo, fg_color=CORES["bg_card"], corner_radius=12)
        frame_tabela.grid(row=0, column=1, sticky="nsew")
        frame_tabela.grid_rowconfigure(0, weight=1)
        frame_tabela.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Financ.Treeview",
            background=CORES["bg_card"], foreground=CORES["text_primary"],
            fieldbackground=CORES["bg_card"], rowheight=32,
            font=("Segoe UI", 10),
        )
        style.configure("Financ.Treeview.Heading",
            background=CORES["bg_secondary"], foreground=CORES["accent_gold"],
            font=("Segoe UI", 9, "bold"), borderwidth=0,
        )
        style.map("Financ.Treeview",
            background=[("selected", CORES["hover"])],
            foreground=[("selected", CORES["text_primary"])],
        )

        self.tree = ttk.Treeview(
            frame_tabela,
            columns=("data", "tipo", "descricao", "categoria", "valor"),
            show="headings", selectmode="browse",
            style="Financ.Treeview", height=12,
        )
        self.tree.heading("data", text="Data")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("descricao", text="Descrição")
        self.tree.heading("categoria", text="Categoria")
        self.tree.heading("valor", text="Valor")
        self.tree.column("data", width=90, anchor="center")
        self.tree.column("tipo", width=70, anchor="center")
        self.tree.column("descricao", width=200)
        self.tree.column("categoria", width=100)
        self.tree.column("valor", width=100, anchor="e")

        scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Ações
        frame_acoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_acoes.grid(row=3, column=0, padx=25, pady=(5, 20), sticky="ew")

        ctk.CTkButton(frame_acoes, text="✏️  Editar", fg_color=CORES["bg_card"],
                       hover_color=CORES["hover"], corner_radius=8,
                       command=self.editar_transacao).pack(side="left", padx=5)
        ctk.CTkButton(frame_acoes, text="🗑️  Excluir", fg_color=CORES["accent_burgundy"],
                       hover_color="#a00000", corner_radius=8,
                       command=self.excluir_transacao).pack(side="left", padx=5)

        self.atualizar_dados()

    def atualizar_dados(self):
        """Atualiza tabela, resumo e gráfico."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        data_inicio = f"{self.ano:04d}-{self.mes:02d}-01"
        if self.mes == 12:
            data_fim = f"{self.ano + 1:04d}-01-01"
        else:
            data_fim = f"{self.ano:04d}-{self.mes + 1:02d}-01"

        transacoes = Transacao.listar_por_periodo(data_inicio, data_fim)
        for t in transacoes:
            cor_tipo = "🟢" if t["tipo"] == "entrada" else "🔴"
            self.tree.insert("", "end", values=(
                formatar_data(t["data_transacao"]),
                f"{cor_tipo} {t['tipo'].upper()}",
                t["descricao"],
                t["categoria"] or "-",
                formatar_moeda(t["valor"]),
            ))

        # Resumo
        resumo = Transacao.resumo_mensal(self.ano, self.mes)
        meses_pt = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                     "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.label_mes.configure(text=f"{meses_pt[self.mes - 1]} {self.ano}")
        self.label_entradas.configure(text=formatar_moeda(resumo["entradas"]))
        self.label_saidas.configure(text=formatar_moeda(resumo["saidas"]))
        self.label_saldo.configure(text=formatar_moeda(resumo["saldo"]))
        cor_saldo = CORES["success"] if resumo["saldo"] >= 0 else CORES["danger"]
        self.label_saldo.configure(text_color=cor_saldo)

        # Gráfico
        self.atualizar_grafico(resumo["entradas"], resumo["saidas"])

    def atualizar_grafico(self, entradas, saidas):
        """Atualiza o gráfico de pizza."""
        if not HAS_MATPLOTLIB:
            return
        self.ax.clear()
        valores = [entradas, saidas]
        labels = ["Entradas", "Saídas"]
        cores = [CORES["success"], CORES["danger"]]
        if sum(valores) > 0:
            self.ax.pie(valores, labels=labels, autopct="%1.1f%%",
                        colors=cores, textprops={'color': '#e8e8e8', 'size': 9},
                        startangle=90)
        else:
            self.ax.text(0.5, 0.5, "Sem dados", ha='center', va='center',
                        color='#a0a0b0', fontsize=12)
        self.ax.set_facecolor(CORES["bg_card"])
        self.canvas.draw()

    def mes_anterior(self):
        if self.mes == 1:
            self.mes = 12; self.ano -= 1
        else:
            self.mes -= 1
        self.atualizar_dados()

    def proximo_mes(self):
        if self.mes == 12:
            self.mes = 1; self.ano += 1
        else:
            self.mes += 1
        self.atualizar_dados()

    def nova_transacao(self):
        JanelaTransacao(self, None)

    def editar_transacao(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma transação.")
            return
        item = self.tree.item(selected[0])
        transacoes = Transacao.listar_por_periodo(
            f"{self.ano:04d}-{self.mes:02d}-01",
            f"{self.ano:04d}-{self.mes + 1 if self.mes < 12 else 1:02d}-01"
        )
        # Encontrar pelo índice na tree
        idx = self.tree.index(selected[0])
        if idx < len(transacoes):
            JanelaTransacao(self, transacoes[idx]["id"])

    def excluir_transacao(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma transação.")
            return
        item = self.tree.item(selected[0])
        if messagebox.askyesno("Confirmar", f"Excluir transação '{item['values'][2]}'?"):
            transacoes = Transacao.listar_por_periodo(
                f"{self.ano:04d}-{self.mes:02d}-01",
                f"{self.ano:04d}-{self.mes + 1 if self.mes < 12 else 1:02d}-01"
            )
            idx = self.tree.index(selected[0])
            if idx < len(transacoes):
                transacao = Transacao.buscar_por_id(transacoes[idx]["id"])
                if transacao:
                    transacao.excluir()
                    self.atualizar_dados()


class JanelaTransacao(ctk.CTkToplevel):
    def __init__(self, parent, transacao_id=None):
        super().__init__(parent)
        self.transacao_id = transacao_id
        self.parent = parent

        if transacao_id:
            self.title("✏️  Editar Transação")
            transacao = Transacao.buscar_por_id(transacao_id)
            self.transacao = transacao
        else:
            self.title("➕  Nova Transação")
            self.transacao = Transacao()

        self.geometry("500x450")
        self.resizable(False, False)
        self.transient(parent); self.grab_set(); self.focus_force(); self.lift()
        self.configure(fg_color=CORES["bg_primary"])

        frame = ctk.CTkFrame(self, fg_color=CORES["bg_card"], corner_radius=12)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        campos = [
            ("Tipo:", ctk.CTkComboBox, {"values": ["entrada", "saida"]}),
            ("Descrição:", ctk.CTkEntry, {}),
            ("Valor (R$):", ctk.CTkEntry, {}),
            ("Categoria:", ctk.CTkEntry, {}),
            ("Data (AAAA-MM-DD):", ctk.CTkEntry, {}),
            ("Forma Pagamento:", ctk.CTkComboBox, {"values": ["Dinheiro", "Pix", "Cartão de Crédito", "Cartão de Débito", ""]}),
        ]

        self.entries = {}
        for i, (label, widget, kwargs) in enumerate(campos):
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=12),
                        text_color=CORES["text_secondary"]).grid(row=i, column=0, padx=15, pady=8, sticky="w")
            if widget == ctk.CTkComboBox:
                entry = widget(frame, width=300, **kwargs)
            else:
                entry = widget(frame, fg_color=CORES["bg_primary"], corner_radius=8, border_width=0)
            entry.grid(row=i, column=1, padx=15, pady=8, sticky="ew")
            self.entries[label] = entry

        # Observações
        ctk.CTkLabel(frame, text="Observações:", font=ctk.CTkFont(size=12),
                    text_color=CORES["text_secondary"]).grid(row=6, column=0, padx=15, pady=8, sticky="w")
        self.entry_obs = ctk.CTkTextbox(frame, height=60, fg_color=CORES["bg_primary"], corner_radius=8)
        self.entry_obs.grid(row=6, column=1, padx=15, pady=8, sticky="ew")

        frame.grid_columnconfigure(1, weight=1)

        if self.transacao_id and self.transacao:
            self.entries["Tipo:"].set(self.transacao.tipo)
            self.entries["Descrição:"].insert(0, self.transacao.descricao or "")
            self.entries["Valor (R$):"].insert(0, str(self.transacao.valor or ""))
            self.entries["Categoria:"].insert(0, self.transacao.categoria or "")
            self.entries["Data (AAAA-MM-DD):"].insert(0, self.transacao.data_transacao or "")
            self.entries["Forma Pagamento:"].set(self.transacao.forma_pagamento or "")
            if self.transacao.observacoes:
                self.entry_obs.insert("1.0", self.transacao.observacoes)
        else:
            self.entries["Data (AAAA-MM-DD):"].insert(0, datetime.date.today().isoformat())

        frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_botoes.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(frame_botoes, text="💾  Salvar", command=self.salvar,
                      fg_color=CORES["accent_gold"], text_color="#1a1a2e",
                      hover_color="#b8942e", font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=8).pack(side="right", padx=5)
        ctk.CTkButton(frame_botoes, text="Cancelar", fg_color=CORES["bg_card"],
                      hover_color=CORES["hover"], corner_radius=8,
                      command=self.destroy).pack(side="right", padx=5)

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def salvar(self):
        descricao = self.entries["Descrição:"].get().strip()
        if not descricao:
            messagebox.showwarning("Aviso", "Descrição é obrigatória.", parent=self)
            return

        try:
            valor = float(self.entries["Valor (R$):"].get().replace(",", ".") or 0)
        except ValueError:
            valor = 0

        self.transacao.tipo = self.entries["Tipo:"].get()
        self.transacao.descricao = descricao
        self.transacao.valor = valor
        self.transacao.categoria = self.entries["Categoria:"].get().strip()
        self.transacao.data_transacao = self.entries["Data (AAAA-MM-DD):"].get().strip()
        self.transacao.forma_pagamento = self.entries["Forma Pagamento:"].get()
        self.transacao.observacoes = self.entry_obs.get("1.0", "end").strip()

        self.transacao.salvar()
        self.parent.atualizar_dados()
        messagebox.showinfo("Sucesso", "Transação salva!", parent=self)
        self.destroy()