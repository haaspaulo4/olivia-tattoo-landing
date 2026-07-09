import customtkinter as ctk
from tkinter import ttk, messagebox
import threading
from utils.cores import CORES
from services.whatsapp_service import (
    formatar_numero, send_message, testar_conexao,
    start_client, disconnect, is_connected
)
from services.agente_whatsapp import agente
import services.whatsapp_service as ws


class TelaWhatsApp(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Registrar callbacks da neonize
        self._registrar_callbacks()

        # Topo
        frame_topo = ctk.CTkFrame(self, fg_color="transparent")
        frame_topo.grid(row=0, column=0, padx=25, pady=(25, 10), sticky="ew")
        frame_topo.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            frame_topo, text="📱  WhatsApp",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=CORES["text_primary"]
        ).grid(row=0, column=0, padx=(0, 20))

        # Status da instância
        self.label_status = ctk.CTkLabel(
            frame_topo, text="🔴  Desconectado",
            font=ctk.CTkFont(size=11), text_color=CORES["danger"]
        )
        self.label_status.grid(row=0, column=1, padx=5)

        btn_config = ctk.CTkButton(
            frame_topo, text="⚙️  Config",
            command=self.ir_config,
            fg_color=CORES["bg_card"], hover_color=CORES["hover"],
            corner_radius=8, width=80, height=32,
            font=ctk.CTkFont(size=11),
        )
        btn_config.grid(row=0, column=3, padx=5)

        # Frame scrollável principal
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.grid(row=1, column=0, padx=25, pady=10, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)

        # ===== CARD 1: Conexão / QR Code =====
        card_conexao = ctk.CTkFrame(scroll_frame, fg_color=CORES["bg_card"], corner_radius=12)
        card_conexao.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        card_conexao.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card_conexao, text="🔌  Conexão",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=CORES["accent_gold"]
        ).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        # Área do QR Code
        self.frame_qr = ctk.CTkFrame(card_conexao, fg_color=CORES["bg_primary"], corner_radius=8,
                                      width=300, height=300)
        self.frame_qr.grid(row=1, column=0, padx=20, pady=10)
        self.frame_qr.grid_propagate(False)

        self.label_qr = ctk.CTkLabel(
            self.frame_qr, text="🔗\nConecte-se ao WhatsApp\npara gerenciar mensagens",
            font=ctk.CTkFont(size=13),
            text_color=CORES["text_secondary"],
            justify="center",
        )
        self.label_qr.place(relx=0.5, rely=0.5, anchor="center")

        # Informações da instância
        self.frame_info = ctk.CTkFrame(card_conexao, fg_color=CORES["bg_primary"], corner_radius=8)
        self.frame_info.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.frame_info.grid_columnconfigure(1, weight=1)

        self.info_itens = {}
        infos = [("Status:", "❓ Desconhecido"),
                 ("Número:", "—"),
                 ("Nome:", "—"),
                 ("Última conexão:", "—")]

        for i, (label, valor) in enumerate(infos):
            ctk.CTkLabel(self.frame_info, text=label, font=ctk.CTkFont(size=11),
                         text_color=CORES["text_secondary"]).grid(row=i, column=0, padx=10, pady=3, sticky="w")
            lbl = ctk.CTkLabel(self.frame_info, text=valor, font=ctk.CTkFont(size=11),
                               text_color=CORES["text_primary"])
            lbl.grid(row=i, column=1, padx=10, pady=3, sticky="w")
            self.info_itens[label] = lbl

        # Botões de ação
        frame_acoes = ctk.CTkFrame(card_conexao, fg_color="transparent")
        frame_acoes.grid(row=3, column=0, padx=20, pady=(5, 15), sticky="ew")

        self.btn_conectar = ctk.CTkButton(
            frame_acoes, text="🔌  Conectar",
            command=self.conectar_instancia,
            fg_color="#25D366", hover_color="#1da851",
            text_color="#1a1a2e", font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8, height=36,
        )
        self.btn_conectar.pack(side="left", padx=5)

        self.btn_desconectar = ctk.CTkButton(
            frame_acoes, text="❌  Desconectar",
            command=self.desconectar_instancia,
            fg_color=CORES["accent_burgundy"], hover_color="#a00000",
            corner_radius=8, height=36, state="disabled",
        )
        self.btn_desconectar.pack(side="left", padx=5)

        ctk.CTkButton(
            frame_acoes, text="🔄  Atualizar",
            command=self.verificar_status,
            fg_color=CORES["bg_card"], hover_color=CORES["hover"],
            corner_radius=8, height=36,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_acoes, text="📱  Abrir WhatsApp",
            command=self.abrir_whatsapp_web,
            fg_color=CORES["bg_card"], hover_color=CORES["hover"],
            corner_radius=8, height=36,
        ).pack(side="left", padx=5)

        # ===== CARD 2: Envio Rápido =====
        card_envio = ctk.CTkFrame(scroll_frame, fg_color=CORES["bg_card"], corner_radius=12)
        card_envio.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        card_envio.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            card_envio, text="📤  Enviar Mensagem",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=CORES["accent_gold"]
        ).grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 5), sticky="w")

        ctk.CTkLabel(card_envio, text="Número:",
                     font=ctk.CTkFont(size=11), text_color=CORES["text_secondary"]
                     ).grid(row=1, column=0, padx=15, pady=8, sticky="w")
        self.entry_numero = ctk.CTkEntry(card_envio, fg_color=CORES["bg_primary"],
                                          corner_radius=8, border_width=0,
                                          placeholder_text="5511999999999")
        self.entry_numero.grid(row=1, column=1, padx=15, pady=8, sticky="ew")

        ctk.CTkLabel(card_envio, text="Mensagem:",
                     font=ctk.CTkFont(size=11), text_color=CORES["text_secondary"]
                     ).grid(row=2, column=0, padx=15, pady=8, sticky="w")
        self.entry_mensagem = ctk.CTkTextbox(card_envio, fg_color=CORES["bg_primary"],
                                              corner_radius=8, height=80)
        self.entry_mensagem.grid(row=2, column=1, padx=15, pady=8, sticky="ew")

        ctk.CTkLabel(card_envio, text="",
                     font=ctk.CTkFont(size=11), text_color=CORES["text_secondary"]
                     ).grid(row=2, column=2, padx=5)

        btn_enviar = ctk.CTkButton(
            card_envio, text="📤  Enviar",
            command=self.enviar_mensagem_rapida,
            fg_color=CORES["accent_gold"], text_color="#1a1a2e",
            hover_color="#b8942e", font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8, height=36,
        )
        btn_enviar.grid(row=3, column=1, padx=15, pady=(5, 15), sticky="ew")

        self.label_envio_status = ctk.CTkLabel(card_envio, text="",
                                                font=ctk.CTkFont(size=10))
        self.label_envio_status.grid(row=4, column=1, padx=15, pady=(0, 10), sticky="w")

        # ===== CARD 3: Agentes Automáticos =====
        card_agentes = ctk.CTkFrame(scroll_frame, fg_color=CORES["bg_card"], corner_radius=12)
        card_agentes.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        card_agentes.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            card_agentes, text="🤖  Agentes Automáticos",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=CORES["accent_gold"]
        ).grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 5), sticky="w")

        # Lembretes
        ctk.CTkLabel(card_agentes, text="🔔  Lembretes:",
                     font=ctk.CTkFont(size=11), text_color=CORES["text_primary"]
                     ).grid(row=1, column=0, padx=15, pady=5, sticky="w")
        from utils.helpers import carregar_config, salvar_config
        self.var_lembrete = ctk.BooleanVar(value=carregar_config("wpp_lembrete_auto") == "1")
        ctk.CTkSwitch(card_agentes, text="", variable=self.var_lembrete,
                      onvalue=True, offvalue=False, fg_color=CORES["accent_gold"],
                      progress_color=CORES["success"],
                      command=lambda: salvar_config("wpp_lembrete_auto", "1" if self.var_lembrete.get() else "0")
                      ).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(card_agentes, text="Lembrar clientes 24h antes",
                     font=ctk.CTkFont(size=9), text_color=CORES["text_secondary"]
                     ).grid(row=1, column=2, padx=5, pady=5, sticky="w")

        # Cobrança
        ctk.CTkLabel(card_agentes, text="💰  Cobrança:",
                     font=ctk.CTkFont(size=11), text_color=CORES["text_primary"]
                     ).grid(row=2, column=0, padx=15, pady=5, sticky="w")
        self.var_cobranca = ctk.BooleanVar(value=carregar_config("wpp_cobranca_auto") == "1")
        ctk.CTkSwitch(card_agentes, text="", variable=self.var_cobranca,
                      onvalue=True, offvalue=False, fg_color=CORES["accent_gold"],
                      progress_color=CORES["success"],
                      command=lambda: salvar_config("wpp_cobranca_auto", "1" if self.var_cobranca.get() else "0")
                      ).grid(row=2, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(card_agentes, text="Cobrar pagamentos pendentes",
                     font=ctk.CTkFont(size=9), text_color=CORES["text_secondary"]
                     ).grid(row=2, column=2, padx=5, pady=5, sticky="w")

        # Boas-vindas
        ctk.CTkLabel(card_agentes, text="👋  Boas-vindas:",
                     font=ctk.CTkFont(size=11), text_color=CORES["text_primary"]
                     ).grid(row=3, column=0, padx=15, pady=5, sticky="w")
        self.var_boasvindas = ctk.BooleanVar(value=carregar_config("wpp_boasvindas_auto") == "1")
        ctk.CTkSwitch(card_agentes, text="", variable=self.var_boasvindas,
                      onvalue=True, offvalue=False, fg_color=CORES["accent_gold"],
                      progress_color=CORES["success"],
                      command=lambda: salvar_config("wpp_boasvindas_auto", "1" if self.var_boasvindas.get() else "0")
                      ).grid(row=3, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(card_agentes, text="Boas-vindas ao cadastrar cliente",
                     font=ctk.CTkFont(size=9), text_color=CORES["text_secondary"]
                     ).grid(row=3, column=2, padx=5, pady=5, sticky="w")

        # Status do agente
        self.label_agente = ctk.CTkLabel(card_agentes, text="✅  Agente ativo",
                                          font=ctk.CTkFont(size=10), text_color=CORES["success"])
        self.label_agente.grid(row=4, column=0, columnspan=3, padx=15, pady=(10, 15), sticky="w")

        # Verificar status inicial
        self.verificar_status()

    def _registrar_callbacks(self):
        """Registra callbacks para eventos da neonize."""
        def on_qr(qr_texto, qr_base64):
            self.after(0, lambda: self._mostrar_qr_recebido(qr_texto, qr_base64))

        def on_connected():
            self.after(0, lambda: self._atualizar_apos_conexao())

        def on_disconnected():
            self.after(0, lambda: self._atualizar_apos_desconexao())

        ws.on_qr_callback = on_qr
        ws.on_connected_callback = on_connected
        ws.on_disconnected_callback = on_disconnected

    def verificar_status(self):
        """Verifica status atual."""
        conectado = is_connected()
        if conectado:
            self._atualizar_apos_conexao()
        else:
            self._atualizar_apos_desconexao()

    def _atualizar_apos_conexao(self):
        self.label_status.configure(text="🟢  Conectado", text_color=CORES["success"])
        self.info_itens["Status:"].configure(text="🟢 Conectado", text_color=CORES["success"])
        self.btn_conectar.configure(state="disabled", text="🔌  Conectar")
        self.btn_desconectar.configure(state="normal")
        self.label_qr.configure(text="✅\nWhatsApp Conectado!\n\nGerencie suas conversas\ne envie mensagens.")
        import datetime
        agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        self.info_itens["Última conexão:"].configure(text=agora)

    def _atualizar_apos_desconexao(self):
        self.label_status.configure(text="🔴  Desconectado", text_color=CORES["danger"])
        self.info_itens["Status:"].configure(text="🔴 Desconectado", text_color=CORES["danger"])
        self.btn_conectar.configure(state="normal")
        self.btn_desconectar.configure(state="disabled")
        self.label_qr.configure(text="📱\nConecte seu WhatsApp\n\nClique em \"Conectar\"\ne escaneie o QR Code")

    def conectar_instancia(self):
        """Inicia conexão real com neonize."""
        self.label_qr.configure(text="⏳\nIniciando...\n\nAguardando QR Code...")
        self.btn_conectar.configure(state="disabled", text="⏳ Conectando...")
        self.label_status.configure(text="⏳  Conectando...", text_color=CORES["warning"])

        threading.Thread(target=self._conectar_real, daemon=True).start()

    def _conectar_real(self):
        """Inicia o cliente neonize."""
        resultado = start_client()
        if not resultado:
            self.after(0, lambda: self._erro_conexao("Erro ao iniciar cliente WhatsApp."))

    def _mostrar_qr_recebido(self, qr_texto, qr_base64):
        """Mostra QR Code recebido como imagem base64."""
        self.label_status.configure(text="⏳  Escaneie o QR Code", text_color=CORES["warning"])
        self.btn_conectar.configure(state="normal", text="🔌  Conectar")

        if qr_base64:
            try:
                import base64
                from PIL import Image, ImageTk
                import io

                img_data = base64.b64decode(qr_base64)
                pil_img = Image.open(io.BytesIO(img_data))
                pil_img = pil_img.resize((280, 280), Image.LANCZOS)
                ctk_img = ctk.CTkImage(pil_img, size=(280, 280))

                self.label_qr.configure(text="", image=ctk_img)
                self.label_qr.image = ctk_img
            except Exception as e:
                self.label_qr.configure(
                    text=f"📱 QR Code gerado!\n\n{qr_texto[:60]}...",
                    font=ctk.CTkFont(size=11)
                )
        else:
            self.label_qr.configure(
                text=f"📱 QR Code:\n\n{qr_texto[:100]}",
                font=ctk.CTkFont(size=11)
            )

    def _erro_conexao(self, msg):
        self.label_qr.configure(text=f"❌\n{msg}", font=ctk.CTkFont(size=11))
        self.btn_conectar.configure(state="normal", text="🔌  Conectar")
        self.label_status.configure(text="🔴  Erro", text_color=CORES["danger"])

    def desconectar_instancia(self):
        """Desconecta usando neonize."""
        if messagebox.askyesno("Confirmar", "Desconectar WhatsApp?\nA sessão será apagada."):
            disconnect()
            messagebox.showinfo("Sucesso", "WhatsApp desconectado!")

    def abrir_whatsapp_web(self):
        """Abre WhatsApp Web no navegador."""
        import webbrowser
        webbrowser.open("https://web.whatsapp.com")

    def enviar_mensagem_rapida(self):
        """Envia mensagem rápida."""
        numero = self.entry_numero.get().strip()
        texto = self.entry_mensagem.get("1.0", "end").strip()

        if not numero or not texto:
            self.label_envio_status.configure(text="⚠️  Preencha número e mensagem", text_color=CORES["warning"])
            return

        numero_formatado = formatar_numero(numero)
        self.label_envio_status.configure(text="⏳  Enviando...", text_color=CORES["info"])

        threading.Thread(target=self._enviar, args=(numero_formatado, texto), daemon=True).start()

    def _enviar(self, numero, texto):
        resultado = send_message(numero, texto)
        self.after(0, lambda: self._resultado_envio(resultado))

    def _resultado_envio(self, resultado):
        if resultado.get("sucesso"):
            self.label_envio_status.configure(
                text="✅  Mensagem enviada!",
                text_color=CORES["success"]
            )
            self.entry_mensagem.delete("1.0", "end")
        else:
            self.label_envio_status.configure(
                text=f"❌  {resultado.get('erro', 'Erro')}",
                text_color=CORES["danger"]
            )

    def ir_config(self):
        """Vai para tela de configurações."""
        widget = self.master
        while widget:
            if hasattr(widget, "mostrar_tela"):
                widget.mostrar_tela("config")
                break
            widget = widget.master if hasattr(widget, "master") else None
