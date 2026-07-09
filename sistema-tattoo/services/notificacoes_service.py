"""
Serviço de Notificações Automáticas por WhatsApp.
Gerencia os envios em background para não travar a interface do usuário.
"""
import threading
from services import whatsapp_service
from datetime import datetime

def _enviar_async(numero, texto):
    """Envia a mensagem em uma thread separada se o WhatsApp estiver conectado."""
    if not numero or not whatsapp_service.is_connected():
        return
    def _run():
        whatsapp_service.send_message(numero, texto)
    threading.Thread(target=_run, daemon=True).start()

def notificar_novo_cliente(nome, telefone):
    """Enviado quando um novo cliente é salvo na base."""
    if not telefone: return
    primeiro_nome = nome.split()[0] if nome else ""
    texto = (
        f"Olá {primeiro_nome}, tudo bem? Seja muito bem-vindo(a) ao estúdio Olivia Tattoo! 🖤\n\n"
        f"Seu cadastro foi realizado com sucesso. Se precisar de qualquer coisa, quiser orçar uma nova tattoo ou tirar dúvidas, "
        f"é só mandar mensagem aqui mesmo.\n\n"
        f"Acompanhe também nosso trabalho no Instagram!"
    )
    _enviar_async(telefone, texto)

def notificar_novo_agendamento(nome, telefone, data_str, horario, descricao, valor_entrada):
    """Enviado quando um novo agendamento é salvo."""
    if not telefone: return
    primeiro_nome = nome.split()[0] if nome else ""
    
    # Formata data para BR se estiver em AAAA-MM-DD
    data_formatada = data_str
    if "-" in data_str:
        try:
            data_formatada = datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
        except:
            pass
            
    texto = (
        f"Olá {primeiro_nome}! Passando para confirmar que seu agendamento está marcado! 🗓️🖋️\n\n"
        f"*Detalhes da Sessão:*\n"
        f"▪️ *Data:* {data_formatada}\n"
        f"▪️ *Horário:* {horario}\n"
        f"▪️ *Referência/Tattoo:* {descricao}\n"
    )
    
    if valor_entrada > 0:
        texto += f"▪️ *Entrada / Sinal:* R$ {valor_entrada:.2f}\n"
        
    texto += (
        f"\nQualquer dúvida, necessidade de remarcação ou alterações, por favor me avise com antecedência. "
        f"Até lá! 🖤"
    )
    _enviar_async(telefone, texto)

def notificar_cobranca(nome, telefone, valor_total, valor_entrada, descricao):
    """Aviso de cobrança / lembrete financeiro da sessão."""
    if not telefone: return
    primeiro_nome = nome.split()[0] if nome else ""
    saldo = valor_total - valor_entrada
    
    if saldo <= 0:
        return # Nada a cobrar
        
    texto = (
        f"Olá {primeiro_nome}! Tudo bem?\n"
        f"Passando para lembrar referente ao valor pendente da sessão de tattoo ({descricao}).\n\n"
        f"▪️ *Valor Total:* R$ {valor_total:.2f}\n"
        f"▪️ *Valor Recebido (Sinal):* R$ {valor_entrada:.2f}\n"
        f"▪️ *Saldo Restante:* R$ {saldo:.2f}\n\n"
        f"Você pode realizar o pagamento no dia da sessão via Pix ou Cartão. Se preferir adiantar, é só me pedir a chave. "
        f"Obrigada! 🖤"
    )
    _enviar_async(telefone, texto)

def notificar_pos_venda(nome, telefone, descricao):
    """Lembrete de pós-venda e cuidados com a tattoo enviada após a sessão."""
    if not telefone: return
    primeiro_nome = nome.split()[0] if nome else ""
    
    texto = (
        f"Olá {primeiro_nome}! Passando para agradecer pela confiança no meu trabalho hoje! 🖤\n\n"
        f"Espero que tenha gostado do resultado da sua tattoo ({descricao}).\n\n"
        f"🚨 *Lembretes importantes de Cuidados:*\n"
        f"▪️ Lave suavemente com sabonete neutro (sem esfregar).\n"
        f"▪️ Passe uma camada beeeem fina de pomada cicatrizante (conforme orientei).\n"
        f"▪️ Não coce e não arranque as casquinhas.\n"
        f"▪️ Evite sol direto, mar e piscina nos próximos 15 dias.\n\n"
        f"Qualquer dúvida sobre a cicatrização, me manda uma foto aqui! E se puder, me marca lá no Instagram quando postar a tattoo! ✨"
    )
    _enviar_async(telefone, texto)
