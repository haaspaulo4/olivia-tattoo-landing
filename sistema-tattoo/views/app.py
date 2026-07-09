import customtkinter as ctk
import datetime
from views.tela_clientes import TelaClientes
from views.tela_agendamento import TelaAgendamento
from views.tela_financeiro import TelaFinanceiro
from views.tela_projetos import TelaProjetos
from views.tela_relatorios import TelaRelatorios
from views.tela_config import TelaConfig
from views.tela_assistente import TelaAssistente
from views.tela_whatsapp import TelaWhatsApp
from utils.helpers import carregar_config
from utils.cores import CORES


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurar tema
        tema = carregar_config("tema")
        ctk.set_appearance_mode(tema if tema else "dark")
        ctk.set_default_color_theme("dark-blue")

        # Configurar janela
        self.title("Olivia Tattoo - Sistema de Gestão")
        self.geometry("1280x750")
        self.minsize(1100, 650)

        # Grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ========== SIDEBAR ==========
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=CORES["bg_secondary"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)

        # Logo / Título
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, padx=15, pady=(25, 15))

        ctk.CTkLabel(
            self.logo_frame,
            text="💀",
            font=ctk.CTkFont(size=36),
        ).pack()

        ctk.CTkLabel(
            self.logo_frame,
            text="OLIVIA TATTOO",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=CORES["accent_gold"],
        ).pack()

        ctk.CTkLabel(
            self.logo_frame,
            text="Sistema de Gestão",
            font=ctk.CTkFont(size=10),
            text_color=CORES["text_secondary"],
        ).pack(pady=(2, 0))

        # Separador
        ctk.CTkFrame(self.sidebar, height=1, fg_color=CORES["accent_gold"]).grid(
            row=1, column=0, padx=20, pady=5, sticky="ew"
        )

        # Botões do menu
        self.botoes_menu = []
        itens_menu = [
            ("👥", "Clientes", "clientes"),
            ("📅", "Agenda", "agenda"),
            ("💰", "Financeiro", "financeiro"),
            ("🎨", "Projetos", "projetos"),
            ("📊", "Relatórios", "relatorios"),
        ("📱", "WhatsApp", "whatsapp"),
        ("🤖", "Assistente", "assistente"),
        ("⚙️", "Config", "config"),
        ]

        for i, (icone, texto, nome) in enumerate(itens_menu):
            if texto == "Assistente":
                ctk.CTkFrame(self.sidebar, height=1, fg_color=CORES["accent_gold"]).grid(
                    row=len(self.botoes_menu) + 2, column=0, padx=20, pady=5, sticky="ew"
                )

            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icone}   {texto}",
                command=lambda n=nome: self.mostrar_tela(n),
                fg_color="transparent",
                text_color=CORES["text_primary"],
                hover_color=CORES["hover"],
                anchor="w",
                height=44,
                font=ctk.CTkFont(size=13),
                corner_radius=8,
            )
            btn.grid(row=len(self.botoes_menu) + 2, column=0, padx=10, pady=3, sticky="ew")
            self.botoes_menu.append(btn)

        # Versão no final
        ctk.CTkLabel(
            self.sidebar,
            text="v1.0.0",
            font=ctk.CTkFont(size=9),
            text_color=CORES["text_secondary"],
        ).grid(row=len(self.botoes_menu) + 3, column=0, pady=(0, 10))

        # ========== CONTEÚDO PRINCIPAL ==========
        self.frame_conteudo = ctk.CTkFrame(self, corner_radius=0, fg_color=CORES["bg_primary"])
        self.frame_conteudo.grid(row=0, column=1, sticky="nsew")
        self.frame_conteudo.grid_rowconfigure(0, weight=1)
        self.frame_conteudo.grid_columnconfigure(0, weight=1)

        # ========== STATUS BAR ==========
        self.status_bar = ctk.CTkFrame(self, height=30, fg_color=CORES["bg_secondary"], corner_radius=0)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_bar.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="✅  Pronto",
            font=ctk.CTkFont(size=10),
            text_color=CORES["text_secondary"],
        )
        self.status_label.pack(side="left", padx=15)

        # Relógio na status bar
        self.clock_label = ctk.CTkLabel(
            self.status_bar,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=CORES["text_secondary"],
        )
        self.clock_label.pack(side="right", padx=15)
        self.atualizar_relogio()

        # Dicionário de telas
        self.telas = {}
        self.tela_atual = None

        # Mostrar tela inicial
        self.mostrar_tela("clientes")

        # Teclas de atalho
        self.bind("<Control-n>", lambda e: self.novo_item())
        self.bind("<Control-f>", lambda e: self.focar_busca())
        self.bind("<F5>", lambda e: self.recarregar())

    def atualizar_relogio(self):
        """Atualiza o relógio na status bar."""
        agora = datetime.datetime.now()
        self.clock_label.configure(text=agora.strftime("%d/%m/%Y  %H:%M"))
        self.after(1000, self.atualizar_relogio)

    def set_status(self, texto):
        """Atualiza o texto da status bar."""
        self.status_label.configure(text=texto)

    def mostrar_tela(self, nome_tela):
        """Alterna entre as telas do sistema."""
        if self.tela_atual:
            self.tela_atual.grid_forget()

        if nome_tela not in self.telas:
            if nome_tela == "clientes":
                self.telas[nome_tela] = TelaClientes(self.frame_conteudo)
            elif nome_tela == "agenda":
                self.telas[nome_tela] = TelaAgendamento(self.frame_conteudo)
            elif nome_tela == "financeiro":
                self.telas[nome_tela] = TelaFinanceiro(self.frame_conteudo)
            elif nome_tela == "projetos":
                self.telas[nome_tela] = TelaProjetos(self.frame_conteudo)
            elif nome_tela == "relatorios":
                self.telas[nome_tela] = TelaRelatorios(self.frame_conteudo)
            elif nome_tela == "whatsapp":
                self.telas[nome_tela] = TelaWhatsApp(self.frame_conteudo)
            elif nome_tela == "assistente":
                self.telas[nome_tela] = TelaAssistente(self.frame_conteudo)
            elif nome_tela == "config":
                self.telas[nome_tela] = TelaConfig(self.frame_conteudo)

        self.tela_atual = self.telas[nome_tela]
        self.tela_atual.grid(row=0, column=0, sticky="nsew")

        # Destacar botão ativo
        for btn in self.botoes_menu:
            btn.configure(fg_color="transparent")

        self.set_status(f"📍  {nome_tela.capitalize()}")

    def novo_item(self):
        """Atalho Ctrl+N - Novo item na tela atual."""
        if hasattr(self.tela_atual, "novo_cliente"):
            self.tela_atual.novo_cliente()
        elif hasattr(self.tela_atual, "novo_agendamento"):
            self.tela_atual.novo_agendamento()
        elif hasattr(self.tela_atual, "nova_transacao"):
            self.tela_atual.nova_transacao()
        elif hasattr(self.tela_atual, "novo_projeto"):
            self.tela_atual.novo_projeto()

    def focar_busca(self):
        """Atalho Ctrl+F - Foca no campo de busca."""
        if hasattr(self.tela_atual, "entry_busca"):
            self.tela_atual.entry_busca.focus()

    def recarregar(self):
        """Atalho F5 - Recarrega dados da tela atual."""
        if hasattr(self.tela_atual, "carregar_dados"):
            self.tela_atual.carregar_dados()
        elif hasattr(self.tela_atual, "atualizar_dados"):
            self.tela_atual.atualizar_dados()
        elif hasattr(self.tela_atual, "renderizar_calendario"):
            self.tela_atual.renderizar_calendario()
