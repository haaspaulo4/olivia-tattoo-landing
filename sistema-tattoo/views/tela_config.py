import customtkinter as ctk
from tkinter import messagebox
from utils.helpers import carregar_config, salvar_config
from utils.cores import CORES


class TelaConfig(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Topo
        frame_topo = ctk.CTkFrame(self, fg_color="transparent")
        frame_topo.grid(row=0, column=0, padx=25, pady=(25, 10), sticky="ew")

        ctk.CTkLabel(
            frame_topo, text="⚙️  Configurações",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=CORES["text_primary"]
        ).pack(side="left", padx=(0, 20))

        # TabView para organizar
        self.tab_view = ctk.CTkTabview(self, fg_color=CORES["bg_card"])
        self.tab_view.grid(row=1, column=0, padx=25, pady=10, sticky="nsew")

        # ===== ABA GERAL =====
        tab_geral = self.tab_view.add("🏪  Estúdio")
        tab_geral.grid_columnconfigure(1, weight=1)

        campos_geral = [
            ("Nome do Estúdio:", "nome_estudio"),
            ("Telefone:", "telefone"),
            ("Email:", "email"),
            ("Endereço:", "endereco"),
        ]

        self.entries = {}
        for i, (label, chave) in enumerate(campos_geral):
            ctk.CTkLabel(tab_geral, text=label, font=ctk.CTkFont(size=12),
                        text_color=CORES["text_secondary"]).grid(row=i, column=0, padx=15, pady=10, sticky="w")
            entry = ctk.CTkEntry(tab_geral, fg_color=CORES["bg_primary"], corner_radius=8, border_width=0)
            entry.grid(row=i, column=1, padx=15, pady=10, sticky="ew")
            entry.insert(0, carregar_config(chave))
            self.entries[chave] = entry

        # Tema
        ctk.CTkLabel(tab_geral, text="Tema:", font=ctk.CTkFont(size=12),
                    text_color=CORES["text_secondary"]).grid(row=4, column=0, padx=15, pady=10, sticky="w")
        self.combo_tema = ctk.CTkComboBox(tab_geral, values=["dark", "light", "system"], width=200,
                                          fg_color=CORES["bg_primary"], corner_radius=8)
        self.combo_tema.grid(row=4, column=1, padx=15, pady=10, sticky="w")
        self.combo_tema.set(carregar_config("tema") or "dark")

        # ===== ABA IA =====
        tab_ia = self.tab_view.add("🤖  Inteligência Artificial")
        tab_ia.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(tab_ia, text="Chave da API Groq (principal):",
                     font=ctk.CTkFont(size=12), text_color=CORES["text_secondary"]).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.entry_groq_key = ctk.CTkEntry(tab_ia, fg_color=CORES["bg_primary"], corner_radius=8, border_width=0,
                                           show="*", width=400)
        self.entry_groq_key.grid(row=0, column=1, padx=15, pady=10, sticky="ew")
        self.entry_groq_key.insert(0, carregar_config("groq_api_key"))

        ctk.CTkLabel(tab_ia, text="Chave fallback (opcional):",
                     font=ctk.CTkFont(size=12), text_color=CORES["text_secondary"]).grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.entry_groq_fallback = ctk.CTkEntry(tab_ia, fg_color=CORES["bg_primary"], corner_radius=8, border_width=0,
                                                show="*", width=400)
        self.entry_groq_fallback.grid(row=1, column=1, padx=15, pady=10, sticky="ew")
        self.entry_groq_fallback.insert(0, carregar_config("groq_api_key_fallback"))

        ctk.CTkLabel(tab_ia, text="Provider:",
                     font=ctk.CTkFont(size=12), text_color=CORES["text_secondary"]).grid(row=2, column=0, padx=15, pady=10, sticky="w")
        self.combo_provider = ctk.CTkComboBox(tab_ia, values=["Groq", "Custom"], width=200,
                                              fg_color=CORES["bg_primary"], corner_radius=8,
                                              command=self.on_provider_change)
        self.combo_provider.grid(row=2, column=1, padx=15, pady=10, sticky="w")
        self.combo_provider.set(carregar_config("ia_provider") or "Groq")

        from services.ia_service import descobrir_modelos_groq

        frame_modelo = ctk.CTkFrame(tab_ia, fg_color="transparent")
        frame_modelo.grid(row=3, column=1, padx=15, pady=10, sticky="ew")
        frame_modelo.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(tab_ia, text="Modelo:",
                     font=ctk.CTkFont(size=12), text_color=CORES["text_secondary"]).grid(row=3, column=0, padx=15, pady=10, sticky="w")

        # Combobox com modelos descobertos + campo livre
        self.combo_modelo = ctk.CTkComboBox(frame_modelo, values=[], width=400,
                                            fg_color=CORES["bg_primary"], corner_radius=8)
        self.combo_modelo.grid(row=0, column=0, sticky="ew")

        btn_atualizar = ctk.CTkButton(frame_modelo, text="↻", width=36,
                                      command=self.atualizar_modelos,
                                      fg_color=CORES["bg_card"], hover_color=CORES["hover"],
                                      corner_radius=8)
        btn_atualizar.grid(row=0, column=1, padx=(5, 0))

        from services.ia_service import modelo_padrao
        modelo_atual = carregar_config("groq_modelo") or modelo_padrao()
        self.combo_modelo.set(modelo_atual)

        # Label de status
        self.label_status_modelos = ctk.CTkLabel(tab_ia, text="",
                     font=ctk.CTkFont(size=9), text_color=CORES["text_secondary"])
        self.label_status_modelos.grid(row=4, column=1, padx=15, sticky="w")

        # Atualizar modelos automaticamente se tiver chave
        if carregar_config("groq_api_key"):
            self.atualizar_modelos()

        self.label_url_custom = ctk.CTkLabel(tab_ia, text="URL da API (Custom):",
                     font=ctk.CTkFont(size=12), text_color=CORES["text_secondary"])
        self.label_url_custom.grid(row=5, column=0, padx=15, pady=10, sticky="w")
        self.entry_url_custom = ctk.CTkEntry(tab_ia, fg_color=CORES["bg_primary"], corner_radius=8, border_width=0, width=400)
        self.entry_url_custom.grid(row=5, column=1, padx=15, pady=10, sticky="ew")
        self.entry_url_custom.insert(0, carregar_config("ia_url_custom") or "")

        ctk.CTkLabel(tab_ia, text="💡 Dicas:", font=ctk.CTkFont(size=10),
                     text_color=CORES["text_secondary"]).grid(row=6, column=0, columnspan=2, padx=15, pady=(20, 5), sticky="w")
        ctk.CTkLabel(tab_ia, text="• Groq: chave gratuita em console.groq.com",
                     font=ctk.CTkFont(size=10), text_color=CORES["info"]).grid(row=7, column=0, columnspan=2, padx=15, sticky="w")
        ctk.CTkLabel(tab_ia, text='• Custom: use para modelos como "GPTOSS-120B" rodando em outro servidor.',
                     font=ctk.CTkFont(size=10), text_color=CORES["warning"]).grid(row=8, column=0, columnspan=2, padx=15, pady=(2, 0), sticky="w")
        ctk.CTkLabel(tab_ia, text="• Clique ↻ para descobrir modelos disponíveis na sua API",
                     font=ctk.CTkFont(size=10), text_color=CORES["text_secondary"]).grid(row=9, column=0, columnspan=2, padx=15, pady=(2, 0), sticky="w")

        self.atualizar_visibilidade_custom()

        # ===== ABA WHATSAPP =====
        tab_wpp = self.tab_view.add("📱  WhatsApp")
        tab_wpp.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(tab_wpp, text="Token da Neomize:",
                     font=ctk.CTkFont(size=12), text_color=CORES["text_secondary"]).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.entry_neomize_token = ctk.CTkEntry(tab_wpp, fg_color=CORES["bg_primary"], corner_radius=8,
                                                border_width=0, show="*", width=400)
        self.entry_neomize_token.grid(row=0, column=1, padx=15, pady=10, sticky="ew")
        self.entry_neomize_token.insert(0, carregar_config("neomize_token"))

        ctk.CTkLabel(tab_wpp, text="Número do Estúdio:",
                     font=ctk.CTkFont(size=12), text_color=CORES["text_secondary"]).grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.entry_neomize_numero = ctk.CTkEntry(tab_wpp, fg_color=CORES["bg_primary"], corner_radius=8,
                                                 border_width=0, width=400, placeholder_text="5511999999999")
        self.entry_neomize_numero.grid(row=1, column=1, padx=15, pady=10, sticky="ew")
        self.entry_neomize_numero.insert(0, carregar_config("neomize_numero"))

        # Status da conexão
        btn_testar = ctk.CTkButton(tab_wpp, text="🔌  Testar Conexão",
                                   command=self.testar_neomize,
                                   fg_color=CORES["bg_card"], hover_color=CORES["hover"], corner_radius=8)
        btn_testar.grid(row=2, column=1, padx=15, pady=5, sticky="w")

        self.label_status_neomize = ctk.CTkLabel(tab_wpp, text="",
                     font=ctk.CTkFont(size=10), text_color=CORES["text_secondary"])
        self.label_status_neomize.grid(row=3, column=1, padx=15, pady=2, sticky="w")

        # Separador
        ctk.CTkFrame(tab_wpp, height=1, fg_color=CORES["hover"]).grid(row=4, column=0, columnspan=2, padx=15, pady=10, sticky="ew")

        ctk.CTkLabel(tab_wpp, text="🤖  Agentes Automáticos:",
                     font=ctk.CTkFont(size=13, weight="bold"), text_color=CORES["accent_gold"]).grid(row=5, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")

        # Lembretes
        frame_lembrete = ctk.CTkFrame(tab_wpp, fg_color=CORES["bg_card"], corner_radius=8)
        frame_lembrete.grid(row=6, column=0, columnspan=2, padx=15, pady=5, sticky="ew")
        frame_lembrete.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame_lembrete, text="🔔  Lembretes de Agendamento",
                     font=ctk.CTkFont(size=11), text_color=CORES["text_primary"]).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.var_lembrete = ctk.BooleanVar(value=carregar_config("wpp_lembrete_auto") == "1")
        ctk.CTkSwitch(frame_lembrete, text="Ativo", variable=self.var_lembrete,
                      onvalue=True, offvalue=False, fg_color=CORES["accent_gold"],
                      progress_color=CORES["success"]).grid(row=0, column=1, padx=10, pady=5, sticky="e")

        ctk.CTkLabel(frame_lembrete, text="Envia lembrete automático 24h antes do agendamento",
                     font=ctk.CTkFont(size=9), text_color=CORES["text_secondary"]).grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="w")

        # Cobrança
        frame_cobranca = ctk.CTkFrame(tab_wpp, fg_color=CORES["bg_card"], corner_radius=8)
        frame_cobranca.grid(row=7, column=0, columnspan=2, padx=15, pady=5, sticky="ew")
        frame_cobranca.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame_cobranca, text="💰  Cobrança Automática",
                     font=ctk.CTkFont(size=11), text_color=CORES["text_primary"]).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.var_cobranca = ctk.BooleanVar(value=carregar_config("wpp_cobranca_auto") == "1")
        ctk.CTkSwitch(frame_cobranca, text="Ativo", variable=self.var_cobranca,
                      onvalue=True, offvalue=False, fg_color=CORES["accent_gold"],
                      progress_color=CORES["success"]).grid(row=0, column=1, padx=10, pady=5, sticky="e")

        ctk.CTkLabel(frame_cobranca, text="Envia cobrança automática para pagamentos pendentes",
                     font=ctk.CTkFont(size=9), text_color=CORES["text_secondary"]).grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="w")

        # Boas-vindas
        frame_bv = ctk.CTkFrame(tab_wpp, fg_color=CORES["bg_card"], corner_radius=8)
        frame_bv.grid(row=8, column=0, columnspan=2, padx=15, pady=5, sticky="ew")
        frame_bv.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame_bv, text="👋  Boas-vindas Automático",
                     font=ctk.CTkFont(size=11), text_color=CORES["text_primary"]).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.var_boasvindas = ctk.BooleanVar(value=carregar_config("wpp_boasvindas_auto") == "1")
        ctk.CTkSwitch(frame_bv, text="Ativo", variable=self.var_boasvindas,
                      onvalue=True, offvalue=False, fg_color=CORES["accent_gold"],
                      progress_color=CORES["success"]).grid(row=0, column=1, padx=10, pady=5, sticky="e")

        ctk.CTkLabel(frame_bv, text="Envia mensagem de boas-vindas quando cadastra novo cliente",
                     font=ctk.CTkFont(size=9), text_color=CORES["text_secondary"]).grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="w")

        # Botão salvar
        frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_botoes.grid(row=2, column=0, padx=25, pady=(10, 20), sticky="ew")

        btn_salvar = ctk.CTkButton(
            frame_botoes, text="💾  Salvar Configurações",
            command=self.salvar,
            fg_color=CORES["accent_gold"],
            text_color="#1a1a2e",
            hover_color="#b8942e",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8,
        )
        btn_salvar.pack(side="right", padx=5)

        # Info
        frame_info = ctk.CTkFrame(self, fg_color="transparent")
        frame_info.grid(row=3, column=0, padx=25, pady=(0, 20), sticky="ew")

        ctk.CTkLabel(
            frame_info,
            text="Olivia Tattoo - Sistema de Gestão v1.0\nDesenvolvido para gerenciamento local do estúdio.",
            font=ctk.CTkFont(size=11),
            text_color=CORES["text_secondary"],
            justify="center",
        ).pack(pady=20)

    def on_provider_change(self, choice):
        """Atualiza visibilidade dos campos conforme provider."""
        self.atualizar_visibilidade_custom()

    def atualizar_visibilidade_custom(self):
        """Mostra/esconde campo de URL customizada."""
        is_custom = self.combo_provider.get() == "Custom"
        if is_custom:
            self.label_url_custom.grid()
            self.entry_url_custom.grid()
        else:
            self.label_url_custom.grid_remove()
            self.entry_url_custom.grid_remove()

    def atualizar_modelos(self):
        """Descobre modelos disponíveis na API Groq."""
        from services.ia_service import descobrir_modelos_groq
        from threading import Thread
        
        self.label_status_modelos.configure(text="⏳ Descobrindo modelos...")
        
        def task():
            modelos = descobrir_modelos_groq(forcar_atualizar=True)
            self.after(0, lambda: self._modelos_carregados(modelos))
        
        Thread(target=task, daemon=True).start()

    def _modelos_carregados(self, modelos):
        """Atualiza combobox com modelos descobertos."""
        if modelos:
            self.combo_modelo.configure(values=modelos)
            if not self.combo_modelo.get():
                self.combo_modelo.set(modelos[0])
            self.label_status_modelos.configure(
                text=f"✅ {len(modelos)} modelos encontrados",
                text_color=CORES["success"]
            )
        else:
            self.label_status_modelos.configure(
                text="⚠️ Não foi possível descobrir modelos. Digite manualmente.",
                text_color=CORES["warning"]
            )

    def testar_neomize(self):
        """Testa conexão com Neomize."""
        from services.whatsapp_service import testar_conexao
        from threading import Thread
        self.label_status_neomize.configure(text="⏳  Testando conexão...")
        def task():
            resultado = testar_conexao()
            self.after(0, lambda: self._resultado_neomize(resultado))
        Thread(target=task, daemon=True).start()

    def _resultado_neomize(self, resultado):
        if resultado.get("status") == "ok":
            self.label_status_neomize.configure(text=resultado.get("mensagem", "✅ Conectado!"), text_color=CORES["success"])
        else:
            self.label_status_neomize.configure(text=resultado.get("mensagem", "❌ Falha"), text_color=CORES["danger"])

    def salvar(self):
        """Salva todas as configurações."""
        for chave, entry in self.entries.items():
            salvar_config(chave, entry.get().strip())

        salvar_config("tema", self.combo_tema.get())
        salvar_config("groq_api_key", self.entry_groq_key.get().strip())
        salvar_config("groq_api_key_fallback", self.entry_groq_fallback.get().strip())
        salvar_config("groq_modelo", self.combo_modelo.get())
        salvar_config("ia_provider", self.combo_provider.get())
        salvar_config("ia_url_custom", self.entry_url_custom.get().strip())
        salvar_config("neomize_token", self.entry_neomize_token.get().strip())
        salvar_config("neomize_numero", self.entry_neomize_numero.get().strip())
        salvar_config("wpp_lembrete_auto", "1" if self.var_lembrete.get() else "0")
        salvar_config("wpp_cobranca_auto", "1" if self.var_cobranca.get() else "0")
        salvar_config("wpp_boasvindas_auto", "1" if self.var_boasvindas.get() else "0")

        messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
