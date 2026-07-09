import customtkinter as ctk
from tkinter import messagebox
import threading
from utils.cores import CORES
from services.ia_service import perguntar, get_api_key


class TelaAssistente(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Topo
        frame_topo = ctk.CTkFrame(self, fg_color="transparent")
        frame_topo.grid(row=0, column=0, padx=25, pady=(25, 10), sticky="ew")
        frame_topo.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame_topo, text="🤖  Assistente IA",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=CORES["text_primary"]
        ).grid(row=0, column=0, padx=(0, 20))

        # Status da API
        self.label_status = ctk.CTkLabel(
            frame_topo,
            text="✅  Conectado" if get_api_key() else "⚠️  Sem chave API",
            font=ctk.CTkFont(size=11),
            text_color=CORES["success"] if get_api_key() else CORES["warning"],
        )
        self.label_status.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(
            frame_topo,
            text="💡 Pergunte sobre clientes, agenda, finanças...",
            font=ctk.CTkFont(size=11),
            text_color=CORES["text_secondary"],
        ).grid(row=0, column=2, padx=5)

        # Área do chat
        frame_chat = ctk.CTkFrame(self, fg_color=CORES["bg_card"], corner_radius=12)
        frame_chat.grid(row=1, column=0, padx=25, pady=10, sticky="nsew")
        frame_chat.grid_rowconfigure(0, weight=1)
        frame_chat.grid_columnconfigure(0, weight=1)

        self.texto_chat = ctk.CTkTextbox(
            frame_chat, font=ctk.CTkFont(size=12),
            fg_color=CORES["bg_primary"], corner_radius=8,
            wrap="word",
        )
        self.texto_chat.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.texto_chat.configure(state="disabled")

        # Mensagem de boas-vindas
        self.adicionar_mensagem("sistema", "🤖  Olá! Sou o assistente IA do Olivia Tattoo.\n\n"
            "Você pode me perguntar sobre:\n"
            "👥  Sugestões para clientes\n"
            "📅  Dicas de agendamento\n"
            "💰  Análise financeira\n"
            "🎨  Descrições de projetos\n"
            "📱  Mensagens para WhatsApp\n\n"
            "Como posso ajudar hoje?")

        # Input
        frame_input = ctk.CTkFrame(self, fg_color=CORES["bg_card"], corner_radius=12)
        frame_input.grid(row=2, column=0, padx=25, pady=(0, 20), sticky="ew")
        frame_input.grid_columnconfigure(0, weight=1)

        self.entry_pergunta = ctk.CTkEntry(
            frame_input, placeholder_text="Digite sua pergunta...",
            fg_color=CORES["bg_primary"], corner_radius=8, border_width=0,
            font=ctk.CTkFont(size=12),
        )
        self.entry_pergunta.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        self.entry_pergunta.bind("<Return>", self.enviar_pergunta)

        btn_enviar = ctk.CTkButton(
            frame_input, text="Enviar  ➤",
            command=self.enviar_pergunta,
            fg_color=CORES["accent_gold"],
            text_color="#1a1a2e",
            hover_color="#b8942e",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8,
        )
        btn_enviar.grid(row=0, column=1, padx=(0, 15), pady=15)

        # Sugestões rápidas
        frame_sugestoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_sugestoes.grid(row=3, column=0, padx=25, pady=(0, 20), sticky="ew")

        ctk.CTkLabel(frame_sugestoes, text="Perguntas rápidas:",
                     font=ctk.CTkFont(size=10), text_color=CORES["text_secondary"]).pack(side="left", padx=5)

        sugestoes = [
            "📊 Analise minhas finanças",
            "📱 Mensagem para cliente",
            "🎨 Descreva um projeto",
            "💡 Dica de gestão",
        ]
        for sugestao in sugestoes:
            btn = ctk.CTkButton(
                frame_sugestoes, text=sugestao,
                command=lambda s=sugestao: self.usar_sugestao(s),
                fg_color=CORES["bg_card"],
                hover_color=CORES["hover"],
                corner_radius=8,
                font=ctk.CTkFont(size=10),
                height=28,
            )
            btn.pack(side="left", padx=3)

        # Focar no input
        self.entry_pergunta.focus()

    def adicionar_mensagem(self, tipo: str, texto: str):
        """Adiciona uma mensagem ao chat."""
        self.texto_chat.configure(state="normal")

        if tipo == "usuario":
            self.texto_chat.insert("end", f"\n🧑  Você:\n", "usuario_tag")
            self.texto_chat.insert("end", f"{texto}\n\n", "usuario_texto")
        elif tipo == "ia":
            self.texto_chat.insert("end", f"\n🤖  Assistente:\n", "ia_tag")
            self.texto_chat.insert("end", f"{texto}\n\n", "ia_texto")
        else:
            self.texto_chat.insert("end", f"{texto}\n\n")

        self.texto_chat.configure(state="disabled")
        self.texto_chat.see("end")

    def usar_sugestao(self, texto: str):
        """Preenche o input com uma sugestão."""
        self.entry_pergunta.delete(0, "end")
        self.entry_pergunta.insert(0, texto)
        self.enviar_pergunta()

    def enviar_pergunta(self, event=None):
        """Envia a pergunta para a IA."""
        pergunta = self.entry_pergunta.get().strip()
        if not pergunta:
            return

        # Mostrar no chat
        self.adicionar_mensagem("usuario", pergunta)
        self.entry_pergunta.delete(0, "end")

        # Desabilitar input durante carregamento
        self.entry_pergunta.configure(state="disabled")
        self.adicionar_mensagem("sistema", "⏳  Pensando...")

        # Enviar em thread separada
        thread = threading.Thread(target=self.processar_resposta, args=(pergunta,), daemon=True)
        thread.start()

    def processar_resposta(self, pergunta: str):
        """Processa a resposta da IA em background."""
        try:
            resposta = perguntar(pergunta)
            # Atualizar UI na thread principal
            self.after(0, lambda: self.mostrar_resposta(resposta))
        except Exception as e:
            self.after(0, lambda: self.mostrar_resposta(f"❌  Erro: {str(e)}"))

    def mostrar_resposta(self, resposta: str):
        """Mostra a resposta no chat."""
        # Remove o "Pensando..."
        self.texto_chat.configure(state="normal")
        # Encontra e remove a última linha de loading
        conteudo = self.texto_chat.get("1.0", "end-1c")
        linhas = conteudo.split("\n")
        # Remove a última mensagem de loading
        for i in range(len(linhas) - 1, -1, -1):
            if "Pensando..." in linhas[i]:
                linhas.pop(i)
                break
        self.texto_chat.delete("1.0", "end")
        self.texto_chat.insert("1.0", "\n".join(linhas))
        self.texto_chat.configure(state="disabled")

        # Adiciona a resposta
        self.adicionar_mensagem("ia", resposta)

        # Reabilitar input
        self.entry_pergunta.configure(state="normal")
        self.entry_pergunta.focus()