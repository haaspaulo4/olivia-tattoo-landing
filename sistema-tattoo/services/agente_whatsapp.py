"""
Agente Automático WhatsApp
Gerencia envio de lembretes, cobranças e boas-vindas via neonize
"""
import threading
import time
import datetime
from models.agendamento import Agendamento
from models.cliente import Cliente
from services.whatsapp_service import (
    send_message, is_connected, formatar_numero
)
from utils.helpers import carregar_config, formatar_data


class AgenteWhatsApp:
    """
    Agente automático que gerencia envios de WhatsApp.
    Roda em background e verifica tarefas periodicamente.
    """

    def __init__(self):
        self._rodando = False
        self._thread = None

    def iniciar(self):
        """Inicia o agente em background."""
        if self._rodando:
            return
        self._rodando = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def parar(self):
        """Para o agente."""
        self._rodando = False

    def _loop(self):
        """Loop principal do agente."""
        while self._rodando:
            try:
                conectado = is_connected()
                print(f"[Agente WhatsApp] Verificando... conectado={conectado}")
                if conectado:
                    self._processar_lembretes()
                    self._processar_cobrancas()
                else:
                    print("[Agente WhatsApp] WhatsApp nao conectado, aguardando...")
            except Exception as e:
                print(f"[Agente WhatsApp] Erro: {e}")
            # Verifica a cada 5 minutos (300 segundos)
            for _ in range(300):
                if not self._rodando:
                    return
                time.sleep(1)

    def _processar_lembretes(self):
        """Envia lembretes para agendamentos de amanhã."""
        if carregar_config("wpp_lembrete_auto") != "1":
            return

        hoje = datetime.date.today()
        amanha = hoje + datetime.timedelta(days=1)
        data_str = amanha.isoformat()

        agendamentos = Agendamento.listar_por_data(data_str)
        print(f"[Agente WhatsApp] Lembretes: {len(agendamentos)} agendamentos amanha")
        enviados = 0

        for ag in agendamentos:
            if ag["status"] != "confirmada":
                continue

            cliente = Cliente.buscar_por_id(ag["cliente_id"])
            if not cliente or not cliente.telefone:
                continue

            from utils.helpers import formatar_data as fmt_data
            data_br = fmt_data(ag["data_sessao"])

            texto = (
                f"🖤 Olivia Tattoo - Lembrete de Agendamento 🖤\n\n"
                f"Olá, {cliente.nome}! 👋\n\n"
                f"Passando pra lembrar que sua sessão é amanhã:\n\n"
                f"📅 Data: {data_br}\n"
                f"⏰ Horário: {ag['horario'][:5]}\n"
                f"{'📝 Descrição: ' + ag.get('descricao', '') if ag.get('descricao') else ''}\n\n"
                f"Confirma presença? É só responder! 😊"
            )

            numero = formatar_numero(cliente.telefone)
            print(f"[Agente WhatsApp] Enviando lembrete para {cliente.nome} ({numero})")
            resultado = send_message(numero, texto)
            print(f"[Agente WhatsApp] Resultado: {resultado}")
            if resultado.get("sucesso"):
                enviados += 1

        if enviados > 0:
            print(f"[Agente WhatsApp] {enviados} lembretes enviados")

    def _processar_cobrancas(self):
        """Envia cobranças para agendamentos realizados com saldo pendente."""
        if carregar_config("wpp_cobranca_auto") != "1":
            return

        agendamentos = Agendamento.listar_todos(status="realizada")
        print(f"[Agente WhatsApp] Cobrancas: {len(agendamentos)} agendamentos realizados")
        enviados = 0

        for ag in agendamentos:
            valor_pendente = ag["valor_total"] - ag["valor_entrada"]
            if valor_pendente <= 0:
                continue

            cliente = Cliente.buscar_por_id(ag["cliente_id"])
            if not cliente or not cliente.telefone:
                continue

            from utils.helpers import formatar_data as fmt_data
            data_br = fmt_data(ag["data_sessao"])

            texto = (
                f"🖤 Olivia Tattoo\n\n"
                f"Olá, {cliente.nome}! 👋\n\n"
                f"Tudo bem? Passando pra lembrar sobre o pagamento:\n\n"
                f"💰 Valor pendente: R$ {valor_pendente:.2f}\n"
                f"📅 Sessão: {data_br}\n\n"
                f"Formas de pagamento:\n"
                f"💵 Dinheiro | 💳 Cartão | 📱 Pix\n\n"
                f"Qualquer dúvida, estou à disposição! 🖤"
            )

            numero = formatar_numero(cliente.telefone)
            print(f"[Agente WhatsApp] Enviando cobranca para {cliente.nome} ({numero})")
            resultado = send_message(numero, texto)
            print(f"[Agente WhatsApp] Resultado: {resultado}")
            if resultado.get("sucesso"):
                enviados += 1
                # Marca como cobrado
                from models.agendamento import Agendamento as AgModel
                a = AgModel.buscar_por_id(ag["id"])
                if a:
                    a.valor_entrada = ag["valor_total"]
                    a.salvar()

        if enviados > 0:
            print(f"[Agente WhatsApp] {enviados} cobranças enviadas")


# Instância global do agente
agente = AgenteWhatsApp()


def enviar_boas_vindas_auto(cliente_id: int):
    """Envia boas-vindas automático quando cadastra cliente."""
    if carregar_config("wpp_boasvindas_auto") != "1":
        return False
    if not is_connected():
        return False

    cliente = Cliente.buscar_por_id(cliente_id)
    if not cliente or not cliente.telefone:
        return False

    texto = (
        f"🖤 Olivia Tattoo 🖤\n\n"
        f"Olá, {cliente.nome}! Seja bem-vindo(a)! 🤗\n\n"
        f"Ficamos muito felizes em ter você conosco!\n"
        f"Em breve entraremos em contato para agendar sua sessão.\n\n"
        f"Nos vemos em breve! 🖤💀"
    )

    numero = formatar_numero(cliente.telefone)
    resultado = send_message(numero, texto)
    return resultado.get("sucesso", False)