"""
WhatsApp Service - Integração com neonize
Baseado no python-bot que funciona
"""
from neonize.client import NewClient
from neonize.events import MessageEv, ConnectedEv, PairStatusEv, QREv, event
from neonize.utils import build_jid
import threading
import time
import sys
import io
import base64
import os
import shutil
import ctypes
from pathlib import Path

BOT_NAME = "olivia_tattoo"
client = None
current_qr_code = ""
current_qr_base64 = ""
processed_msg_ids = set()

on_qr_callback = None
on_connected_callback = None
on_message_callback = None
on_disconnected_callback = None

_last_pairing = "unknown"


def _gerar_qr_base64(texto_qr):
    try:
        import segno
        buf = io.BytesIO()
        qr = segno.make(texto_qr)
        qr.save(buf, kind='png', scale=5)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
    except:
        return None


def get_client():
    return client


def start_client():
    """Inicia o cliente em background, igual ao python-bot que funciona."""
    global client, current_qr_code, current_qr_base64

    current_qr_code = ""
    current_qr_base64 = ""

    try:
        client = NewClient(BOT_NAME)

        @client.event(PairStatusEv)
        def on_pair_status(c: NewClient, evt: PairStatusEv):
            global _last_pairing
            _last_pairing = str(evt.Status)
            print(f"[WhatsApp] PairStatus: {evt.Status}")

        @client.event(QREv)
        def on_qr(c: NewClient, evt: QREv):
            global current_qr_code, _last_pairing
            _last_pairing = "qr"
            code = getattr(evt, "Codes", None) or getattr(evt, "codes", None) or ""
            if isinstance(code, bytes):
                code = code.decode('utf-8', errors='ignore')
            current_qr_code = str(code)
            b64 = _gerar_qr_base64(current_qr_code)
            if on_qr_callback:
                on_qr_callback(current_qr_code, b64)

        @client.event(ConnectedEv)
        def on_connected(c: NewClient, evt: ConnectedEv):
            global current_qr_code, _last_pairing
            _last_pairing = "connected"
            current_qr_code = ""
            print("[WhatsApp] Conectado e pronto!")
            if on_connected_callback:
                on_connected_callback()

        @client.event(MessageEv)
        def on_message(c: NewClient, evt: MessageEv):
            if on_message_callback:
                on_message_callback(evt)

        def _run():
            try:
                print(f"[WhatsApp] Iniciando cliente {BOT_NAME}...")
                client.connect()
                event.wait()
            except Exception as e:
                print(f"[WhatsApp] Erro na conexao: {e}")
                if on_disconnected_callback:
                    on_disconnected_callback()

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        return True

    except Exception as e:
        return False


def is_connected():
    """Verifica conexao - igual ao python-bot"""
    global client
    return client is not None and client.is_connected


def disconnect():
    """Desconecta e apaga sessao - igual ao python-bot"""
    global client, current_qr_code, current_qr_base64
    if client:
        try:
            client.disconnect()
        except:
            pass
        client = None
    current_qr_code = ""
    current_qr_base64 = ""
    import shutil
    if os.path.exists(BOT_NAME):
        try:
            shutil.rmtree(BOT_NAME)
        except:
            pass
    if on_disconnected_callback:
        on_disconnected_callback()
    return True


def send_message(numero: str, texto: str) -> dict:
    """Envia texto validando o número via is_on_whatsapp primeiro.
    
    O build_jid() cria JIDs com o número cru, mas o WhatsApp reformata
    números brasileiros (ex: remove o 9° dígito). Precisamos usar
    is_on_whatsapp() para obter o JID REAL antes de enviar.
    """
    if not client:
        return {"erro": "WhatsApp nao iniciado."}
    if not client.is_connected:
        return {"erro": "WhatsApp nao conectado."}
    try:
        # Normaliza numero
        n = "".join(c for c in numero if c.isdigit())
        if not n:
            return {"erro": "Numero invalido."}
        numero_fmt = f"55{n}" if not n.startswith("55") else n

        # Resolve o JID REAL via WhatsApp (corrige formatação do número)
        try:
            resultados = client.is_on_whatsapp(numero_fmt)
            jid_envio = None
            for r in resultados:
                if r.IsIn:
                    jid_envio = r.JID
                    print(f"[WhatsApp] Número validado: {numero_fmt} -> {jid_envio.User}@{jid_envio.Server}")
                    break

            if jid_envio is None:
                print(f"[WhatsApp] Número {numero_fmt} NÃO está no WhatsApp!")
                return {"erro": f"O número {numero_fmt} não está registrado no WhatsApp."}
        except Exception as e:
            print(f"[WhatsApp] Falha ao validar número, tentando build_jid: {e}")
            jid_envio = build_jid(numero_fmt)

        print(f"[WhatsApp] Sincronizando dispositivos (Signal Protocol)...")
        try:
            client.get_user_devices(jid_envio)
        except Exception as e:
            print(f"[WhatsApp] Aviso ao sincronizar dispositivos: {e}")

        print(f"[WhatsApp] Enviando para {jid_envio.User}@{jid_envio.Server} texto={texto[:60]}...")
        response = client.send_message(jid_envio, texto)
        print(f"[WhatsApp] Envio concluido! ID={response.ID} Timestamp={response.Timestamp}")
        return {"sucesso": True, "id": response.ID}
    except Exception as e:
        erro_str = str(e)
        print(f"[WhatsApp] ERRO envio: {erro_str}")
        return {"erro": erro_str}


def formatar_numero(numero: str) -> str:
    n = "".join(c for c in numero if c.isdigit())
    if not n:
        return ""
    return f"55{n}" if not n.startswith("55") else n


def testar_conexao():
    if is_connected():
        return {"status": "ok", "mensagem": "WhatsApp Conectado!"}
    if client is not None:
        return {"status": "espera", "mensagem": "Aguardando conexao..."}
    return {"status": "erro", "mensagem": "WhatsApp desconectado."}