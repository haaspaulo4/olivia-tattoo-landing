#!/usr/bin/env python3
"""
Sistema de Gestão - Olivia Tattoo
Sistema local para gestão de estúdio de tatuagem
"""

import sys
import os

# Adiciona o diretório raiz ao path do Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.conexao import inicializar_banco
from utils.helpers import carregar_config, salvar_config
from views.app import App
from services.agente_whatsapp import agente
from services.whatsapp_service import start_client, is_connected


def main():
    """Função principal que inicializa o sistema."""
    try:
        # Inicializar banco de dados
        inicializar_banco()

        # Iniciar conexão WhatsApp
        start_client()

        # Aguardar alguns segundos para conexão inicial
        import time as _time
        _time.sleep(3)

        # Iniciar agente WhatsApp
        agente.iniciar()

        # Iniciar interface gráfica
        app = App()

        # Parar agente ao fechar
        def on_closing():
            agente.parar()
            app.quit()

        app.protocol("WM_DELETE_WINDOW", on_closing)
        app.mainloop()

    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror(
            "Erro",
            f"Ocorreu um erro ao iniciar o sistema:\n\n{str(e)}\n\n"
            "Verifique se o Python e as dependências estão instalados corretamente."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()