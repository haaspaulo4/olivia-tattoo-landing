import customtkinter as ctk
from tkinter import ttk, messagebox
import calendar
import datetime
from models.agendamento import Agendamento
from models.cliente import Cliente
from utils.helpers import formatar_data, formatar_moeda
from utils.cores import CORES


class TelaAgendamento(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        hoje = datetime.date.today()
        self.ano = hoje.year
        self.mes = hoje.month
        self.dia_selecionado = hoje.day

        # Topo
        frame_topo = ctk.CTkFrame(self, fg_color="transparent")
        frame_topo.grid(row=0, column=0, padx=25, pady=(25, 10), sticky="ew")
        frame_topo.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame_topo, text="📅  Agenda",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=CORES["text_primary"]
        ).grid(row=0, column=0, padx=(0, 20))

        # Navegação mês
        frame_mes = ctk.CTkFrame(frame_topo, fg_color=CORES["bg_card"], corner_radius=10)
        frame_mes.grid(row=0, column=1)

        meses_pt = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                     "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.label_mes = ctk.CTkLabel(frame_mes, text=f"{meses_pt[self.mes - 1]} {self.ano}",
                                      font=ctk.CTkFont(size=16, weight="bold"))
        self.label_mes.pack(side="left", padx=15)

        ctk.CTkButton(frame_mes, text="◀", width=36, command=self.mes_anterior,
                       fg_color="transparent", hover_color=CORES["hover"], corner_radius=6).pack(side="left", padx=2)
        ctk.CTkButton(frame_mes, text="▶", width=36, command=self.proximo_mes,
                       fg_color="transparent", hover_color=CORES["hover"], corner_radius=6).pack(side="left", padx=2)
        ctk.CTkButton(frame_mes, text="Hoje", width=50, command=self.ir_hoje,
                       fg_color=CORES["accent_gold"], text_color="#1a1a2e",
                       hover_color="#b8942e", corner_radius=6, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=5)

        btn_novo = ctk.CTkButton(
            frame_topo, text="＋  Novo Agendamento",
            command=self.novo_agendamento,
            fg_color=CORES["accent_gold"],
            text_color="#1a1a2e",
            hover_color="#b8942e",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8,
            height=38,
        )
        btn_novo.grid(row=0, column=2, padx=5)

        # Legenda
        frame_legenda = ctk.CTkFrame(self, fg_color="transparent")
        frame_legenda.grid(row=1, column=0, padx=25, pady=5, sticky="ew")

        ctk.CTkLabel(frame_legenda, text="🟢  Confirmada", text_color=CORES["success"],
                     font=ctk.CTkFont(size=11)).pack(side="left", padx=10)
        ctk.CTkLabel(frame_legenda, text="🔵  Realizada", text_color=CORES["info"],
                     font=ctk.CTkFont(size=11)).pack(side="left", padx=10)
        ctk.CTkLabel(frame_legenda, text="🔴  Cancelada", text_color=CORES["danger"],
                     font=ctk.CTkFont(size=11)).pack(side="left", padx=10)

        # Conteúdo dividido: Calendário + Lista
        frame_conteudo = ctk.CTkFrame(self, fg_color="transparent")
        frame_conteudo.grid(row=2, column=0, padx=25, pady=10, sticky="nsew")
        frame_conteudo.grid_columnconfigure(0, weight=3)
        frame_conteudo.grid_columnconfigure(1, weight=2)
        frame_conteudo.grid_rowconfigure(0, weight=1)

        # ===== CALENDÁRIO =====
        frame_calendario = ctk.CTkFrame(frame_conteudo, fg_color=CORES["bg_card"], corner_radius=12)
        frame_calendario.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        frame_calendario.grid_rowconfigure(0, weight=1)
        frame_calendario.grid_columnconfigure(0, weight=1)

        # Frame dos dias com grid
        self.frame_dias = ctk.CTkFrame(frame_calendario, fg_color="transparent")
        self.frame_dias.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)

        # ===== LISTA DE AGENDAMENTOS =====
        frame_lista = ctk.CTkFrame(frame_conteudo, fg_color=CORES["bg_card"], corner_radius=12)
        frame_lista.grid(row=0, column=1, sticky="nsew")
        frame_lista.grid_rowconfigure(1, weight=1)
        frame_lista.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_lista, text="📋  Agendamentos do Dia",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=CORES["accent_gold"]).grid(row=0, column=0, pady=(15, 5), padx=15, sticky="w")

        self.texto_agenda = ctk.CTkTextbox(frame_lista, font=ctk.CTkFont(size=12),
                                           fg_color=CORES["bg_primary"], corner_radius=8)
        self.texto_agenda.grid(row=1, column=0, sticky="nsew", padx=15, pady=(5, 15))

        # Botões de ação na lista
        frame_acoes_lista = ctk.CTkFrame(frame_lista, fg_color="transparent")
        frame_acoes_lista.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")

        ctk.CTkButton(frame_acoes_lista, text="✏️  Editar", fg_color=CORES["bg_card"],
                       hover_color=CORES["hover"], corner_radius=8,
                       command=self.editar_agendamento).pack(side="left", padx=2)
        ctk.CTkButton(frame_acoes_lista, text="🗑️  Excluir", fg_color=CORES["accent_burgundy"],
                       hover_color="#a00000", corner_radius=8,
                       command=self.excluir_agendamento).pack(side="left", padx=2)

        self.renderizar_calendario()

    def renderizar_calendario(self):
        """Renderiza o calendário do mês com células grandes."""
        for widget in self.frame_dias.winfo_children():
            widget.destroy()

        meses_pt = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                     "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.label_mes.configure(text=f"{meses_pt[self.mes - 1]} {self.ano}")

        # Cabeçalho dos dias da semana
        dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        for col, dia in enumerate(dias_semana):
            lbl = ctk.CTkLabel(self.frame_dias, text=dia,
                              font=ctk.CTkFont(size=13, weight="bold"),
                              text_color=CORES["accent_gold"],
                              width=100, height=28)
            lbl.grid(row=0, column=col, padx=3, pady=3)

        # Dias do mês
        primeiro_dia_semana, num_dias = calendar.monthrange(self.ano, self.mes)
        primeiro_dia_semana = (primeiro_dia_semana - calendar.MONDAY) % 7

        # Buscar agendamentos do mês
        agendamentos = Agendamento.listar_por_mes(self.ano, self.mes)
        agendamentos_por_dia = {}
        for ag in agendamentos:
            try:
                dia = int(ag["data_sessao"].split("-")[2])
                if dia not in agendamentos_por_dia:
                    agendamentos_por_dia[dia] = []
                agendamentos_por_dia[dia].append(ag)
            except (IndexError, ValueError):
                pass

        hoje = datetime.date.today()
        linha = 1
        coluna = primeiro_dia_semana

        for dia in range(1, num_dias + 1):
            frame_dia = ctk.CTkFrame(self.frame_dias, width=100, height=100, corner_radius=8)
            frame_dia.grid(row=linha, column=coluna, padx=3, pady=3)

            data_str = f"{self.ano:04d}-{self.mes:02d}-{dia:02d}"
            eh_hoje = (hoje.year == self.ano and hoje.month == self.mes and hoje.day == dia)
            eh_selecionado = (self.dia_selecionado == dia)

            if eh_hoje:
                frame_dia.configure(fg_color="#2c3e50")
            elif eh_selecionado:
                frame_dia.configure(fg_color=CORES["hover"])
            else:
                frame_dia.configure(fg_color="transparent")

            # Número do dia
            lbl_dia = ctk.CTkLabel(frame_dia, text=str(dia),
                                   font=ctk.CTkFont(size=13, weight="bold" if eh_hoje else "normal"),
                                   text_color=CORES["accent_gold"] if eh_hoje else CORES["text_primary"])
            lbl_dia.pack(anchor="nw", padx=6, pady=4)

            # Agendamentos do dia - mostrar como cards pequenos
            if dia in agendamentos_por_dia:
                for ag in agendamentos_por_dia[dia][:3]:
                    cor_status = {"confirmada": CORES["success"], "realizada": CORES["info"], "cancelada": CORES["danger"]}
                    cor = cor_status.get(ag["status"], CORES["success"])

                    card_ag = ctk.CTkFrame(frame_dia, fg_color=cor, corner_radius=4, height=18)
                    card_ag.pack(fill="x", padx=4, pady=1)

                    nome_cliente = ag.get("cliente_nome", "?")[:12]
                    ctk.CTkLabel(card_ag, text=f"{ag['horario'][:5]} {nome_cliente}",
                                font=ctk.CTkFont(size=8), text_color="#1a1a2e").pack(padx=4)

                if len(agendamentos_por_dia[dia]) > 3:
                    ctk.CTkLabel(frame_dia, text=f"+{len(agendamentos_por_dia[dia]) - 3} mais",
                                 font=ctk.CTkFont(size=8), text_color=CORES["text_secondary"]).pack(anchor="w", padx=6)

            # Clique no dia
            frame_dia.bind("<Button-1>", lambda e, d=dia: self.selecionar_dia(d))

            coluna += 1
            if coluna > 6:
                coluna = 0
                linha += 1

    def selecionar_dia(self, dia):
        """Seleciona um dia e mostra agendamentos."""
        self.dia_selecionado = dia
        self.renderizar_calendario()
        data_str = f"{self.ano:04d}-{self.mes:02d}-{dia:02d}"
        self.mostrar_agenda_dia(data_str)

    def mostrar_agenda_dia(self, data):
        """Mostra agendamentos do dia selecionado em formato de cards."""
        self.texto_agenda.delete("1.0", "end")
        agendamentos = Agendamento.listar_por_data(data)
        if not agendamentos:
            self.texto_agenda.insert("1.0", "   Nenhum agendamento para esta data.")
            return

        data_formatada = formatar_data(data)
        self.texto_agenda.insert("1.0", f"   📅  {data_formatada}\n\n", "titulo")

        for i, ag in enumerate(agendamentos):
            cor_status = {"confirmada": "🟢", "realizada": "🔵", "cancelada": "🔴"}
            status_icon = cor_status.get(ag["status"], "🟢")

            texto = (
                f"{'─' * 40}\n"
                f"{status_icon}  {ag['horario'][:5]}  -  {ag['cliente_nome']}\n"
                f"   📝  {ag['descricao'] or 'Sem descrição'}\n"
                f"   💰  {formatar_moeda(ag['valor_total'])}  |  "
                f"📌  {ag['status'].upper()}\n\n"
            )
            self.texto_agenda.insert("end", texto)

    def mes_anterior(self):
        if self.mes == 1:
            self.mes = 12
            self.ano -= 1
        else:
            self.mes -= 1
        self.dia_selecionado = 1
        self.renderizar_calendario()

    def proximo_mes(self):
        if self.mes == 12:
            self.mes = 1
            self.ano += 1
        else:
            self.mes += 1
        self.dia_selecionado = 1
        self.renderizar_calendario()

    def ir_hoje(self):
        hoje = datetime.date.today()
        self.ano = hoje.year
        self.mes = hoje.month
        self.dia_selecionado = hoje.day
        self.renderizar_calendario()
        data_str = hoje.isoformat()
        self.mostrar_agenda_dia(data_str)

    def novo_agendamento(self):
        JanelaAgendamento(self, None)

    def editar_agendamento(self):
        """Edita um agendamento do dia selecionado."""
        data_str = f"{self.ano:04d}-{self.mes:02d}-{self.dia_selecionado:02d}"
        agendamentos = Agendamento.listar_por_data(data_str)
        if not agendamentos:
            messagebox.showwarning("Aviso", "Nenhum agendamento neste dia.")
            return
        if len(agendamentos) == 1:
            JanelaAgendamento(self, agendamentos[0]["id"])
        else:
            # Selecionar qual editar
            nomes = [f"{a['horario'][:5]} - {a['cliente_nome']}" for a in agendamentos]
            # Simplificar: pega o primeiro
            JanelaAgendamento(self, agendamentos[0]["id"])

    def excluir_agendamento(self):
        data_str = f"{self.ano:04d}-{self.mes:02d}-{self.dia_selecionado:02d}"
        agendamentos = Agendamento.listar_por_data(data_str)
        if not agendamentos:
            messagebox.showwarning("Aviso", "Nenhum agendamento neste dia.")
            return
        if messagebox.askyesno("Confirmar", f"Excluir agendamento de {agendamentos[0]['cliente_nome']}?"):
            ag = Agendamento.buscar_por_id(agendamentos[0]["id"])
            if ag:
                ag.excluir()
                self.renderizar_calendario()
                self.mostrar_agenda_dia(data_str)


class JanelaAgendamento(ctk.CTkToplevel):
    def __init__(self, parent, agendamento_id=None):
        super().__init__(parent)
        self.agendamento_id = agendamento_id
        self.parent = parent

        if agendamento_id:
            self.title("✏️  Editar Agendamento")
            ag = Agendamento.buscar_por_id(agendamento_id)
            self.agendamento = ag
        else:
            self.title("➕  Novo Agendamento")
            self.agendamento = Agendamento()

        self.geometry("520x580")
        self.resizable(False, False)
        self.transient(parent); self.grab_set(); self.focus_force(); self.lift()
        self.configure(fg_color=CORES["bg_primary"])

        frame = ctk.CTkFrame(self, fg_color=CORES["bg_card"], corner_radius=12)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Campos
        campos = [
            ("Cliente:", ctk.CTkComboBox, {"values": []}),
            ("Data (AAAA-MM-DD):", ctk.CTkEntry, {}),
            ("Horário (HH:MM):", ctk.CTkEntry, {}),
            ("Descrição:", ctk.CTkEntry, {}),
            ("Valor Total (R$):", ctk.CTkEntry, {}),
            ("Valor Entrada (R$):", ctk.CTkEntry, {}),
            ("Status:", ctk.CTkComboBox, {"values": ["confirmada", "realizada", "cancelada"]}),
        ]

        self.entries = {}
        for i, (label, widget, kwargs) in enumerate(campos):
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=12),
                        text_color=CORES["text_secondary"]).grid(row=i, column=0, padx=15, pady=7, sticky="w")
            if widget == ctk.CTkComboBox:
                entry = widget(frame, width=300, **kwargs)
            else:
                entry = widget(frame, fg_color=CORES["bg_primary"], corner_radius=8, border_width=0)
            entry.grid(row=i, column=1, padx=15, pady=7, sticky="ew")
            self.entries[label] = entry

        # Observações
        ctk.CTkLabel(frame, text="Observações:", font=ctk.CTkFont(size=12),
                    text_color=CORES["text_secondary"]).grid(row=7, column=0, padx=15, pady=7, sticky="w")
        self.entry_obs = ctk.CTkTextbox(frame, height=60, fg_color=CORES["bg_primary"], corner_radius=8)
        self.entry_obs.grid(row=7, column=1, padx=15, pady=7, sticky="ew")

        frame.grid_columnconfigure(1, weight=1)

        # Carregar clientes
        self.carregar_clientes()

        if self.agendamento_id and self.agendamento:
            self.entries["Cliente:"].set(str(self.agendamento.cliente_id))
            self.entries["Data (AAAA-MM-DD):"].insert(0, self.agendamento.data_sessao or "")
            self.entries["Horário (HH:MM):"].insert(0, self.agendamento.horario or "")
            self.entries["Descrição:"].insert(0, self.agendamento.descricao or "")
            self.entries["Valor Total (R$):"].insert(0, str(self.agendamento.valor_total or ""))
            self.entries["Valor Entrada (R$):"].insert(0, str(self.agendamento.valor_entrada or ""))
            self.entries["Status:"].set(self.agendamento.status or "confirmada")
            if self.agendamento.observacoes:
                self.entry_obs.insert("1.0", self.agendamento.observacoes)
        else:
            hoje = datetime.date.today()
            self.entries["Data (AAAA-MM-DD):"].insert(0, hoje.isoformat())
            self.entries["Status:"].set("confirmada")
            if hasattr(parent, 'dia_selecionado'):
                data = f"{parent.ano:04d}-{parent.mes:02d}-{parent.dia_selecionado:02d}"
                self.entries["Data (AAAA-MM-DD):"].delete(0, "end")
                self.entries["Data (AAAA-MM-DD):"].insert(0, data)

        # Botões
        frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_botoes.pack(fill="x", padx=20, pady=(0, 20))

        if self.agendamento_id:
            ctk.CTkButton(frame_botoes, text="💸 Cobrar Saldo", command=self.cobrar_saldo,
                          fg_color="#8B0000", text_color="white",
                          hover_color="#A52A2A", font=ctk.CTkFont(size=12, weight="bold"),
                          corner_radius=8).pack(side="left", padx=5)
            
            ctk.CTkButton(frame_botoes, text="✨ Pós-Venda (Cuidados)", command=self.enviar_pos_venda,
                          fg_color="#2E8B57", text_color="white",
                          hover_color="#3CB371", font=ctk.CTkFont(size=12, weight="bold"),
                          corner_radius=8).pack(side="left", padx=5)

        ctk.CTkButton(frame_botoes, text="💾  Salvar", command=self.salvar,
                      fg_color=CORES["accent_gold"], text_color="#1a1a2e",
                      hover_color="#b8942e", font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=8).pack(side="right", padx=5)
        ctk.CTkButton(frame_botoes, text="Cancelar", fg_color=CORES["bg_card"],
                      hover_color=CORES["hover"], corner_radius=8,
                      command=self.destroy).pack(side="right", padx=5)

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def enviar_pos_venda(self):
        cliente_selecionado = self.entries["Cliente:"].get()
        if not cliente_selecionado or cliente_selecionado not in self.clientes_dict:
            messagebox.showwarning("Aviso", "Selecione o cliente primeiro.", parent=self)
            return
            
        descricao = self.entries["Descrição:"].get().strip() or "sua sessão"
        cliente_id = self.clientes_dict[cliente_selecionado]
        
        from models.cliente import Cliente
        from services import notificacoes_service
        
        cli = Cliente.buscar_por_id(cliente_id)
        if not cli or not cli.telefone:
            messagebox.showwarning("Aviso", "O cliente não possui um telefone/WhatsApp cadastrado.", parent=self)
            return
            
        notificacoes_service.notificar_pos_venda(cli.nome, cli.telefone, descricao)
        messagebox.showinfo("Sucesso", "Mensagem de Pós-Venda e Cuidados enviada pelo WhatsApp!", parent=self)

    def cobrar_saldo(self):
        cliente_selecionado = self.entries["Cliente:"].get()
        if not cliente_selecionado or cliente_selecionado not in self.clientes_dict:
            messagebox.showwarning("Aviso", "Selecione o cliente primeiro.", parent=self)
            return
            
        try:
            valor_total = float(self.entries["Valor Total (R$):"].get().replace(",", ".") or 0)
            valor_entrada = float(self.entries["Valor Entrada (R$):"].get().replace(",", ".") or 0)
        except ValueError:
            messagebox.showwarning("Aviso", "Valores inválidos (use formato 0.00).", parent=self)
            return
            
        if valor_total <= valor_entrada:
            messagebox.showinfo("Aviso", "Não há saldo pendente para cobrar.", parent=self)
            return
            
        descricao = self.entries["Descrição:"].get().strip() or "Sessão de Tattoo"
        cliente_id = self.clientes_dict[cliente_selecionado]
        
        from models.cliente import Cliente
        from services import notificacoes_service
        
        cli = Cliente.buscar_por_id(cliente_id)
        if not cli or not cli.telefone:
            messagebox.showwarning("Aviso", "O cliente não possui um telefone/WhatsApp cadastrado.", parent=self)
            return
            
        notificacoes_service.notificar_cobranca(cli.nome, cli.telefone, valor_total, valor_entrada, descricao)
        messagebox.showinfo("Sucesso", "Lembrete de cobrança enviado para o WhatsApp do cliente!", parent=self)

    def carregar_clientes(self):
        clientes = Cliente.listar_todos()
        self.clientes_dict = {}
        for c in clientes:
            label = f"{c['id']} - {c['nome']}"
            self.clientes_dict[label] = c["id"]
        self.entries["Cliente:"].configure(values=list(self.clientes_dict.keys()))

    def salvar(self):
        cliente_selecionado = self.entries["Cliente:"].get()
        if not cliente_selecionado or cliente_selecionado not in self.clientes_dict:
            messagebox.showwarning("Aviso", "Selecione um cliente.", parent=self)
            return

        data = self.entries["Data (AAAA-MM-DD):"].get().strip()
        horario = self.entries["Horário (HH:MM):"].get().strip()
        if not data or not horario:
            messagebox.showwarning("Aviso", "Data e horário são obrigatórios.", parent=self)
            return

        is_novo = self.agendamento.id is None

        self.agendamento.cliente_id = self.clientes_dict[cliente_selecionado]
        self.agendamento.data_sessao = data
        self.agendamento.horario = horario
        self.agendamento.descricao = self.entries["Descrição:"].get().strip()
        try:
            self.agendamento.valor_total = float(self.entries["Valor Total (R$):"].get().replace(",", ".") or 0)
        except ValueError:
            self.agendamento.valor_total = 0
        try:
            self.agendamento.valor_entrada = float(self.entries["Valor Entrada (R$):"].get().replace(",", ".") or 0)
        except ValueError:
            self.agendamento.valor_entrada = 0
        self.agendamento.status = self.entries["Status:"].get()
        self.agendamento.observacoes = self.entry_obs.get("1.0", "end").strip()

        self.agendamento.salvar()
        
        # Obter telefone do cliente para notificação
        if is_novo:
            from models.cliente import Cliente
            from services import notificacoes_service
            cli = Cliente.buscar_por_id(self.agendamento.cliente_id)
            if cli and cli.telefone:
                notificacoes_service.notificar_novo_agendamento(
                    cli.nome, cli.telefone, self.agendamento.data_sessao, 
                    self.agendamento.horario, self.agendamento.descricao, 
                    self.agendamento.valor_entrada
                )

        self.parent.renderizar_calendario()
        data_str = f"{self.agendamento.data_sessao}"
        self.parent.mostrar_agenda_dia(data_str)
        messagebox.showinfo("Sucesso", "Agendamento salvo!", parent=self)
        self.destroy()