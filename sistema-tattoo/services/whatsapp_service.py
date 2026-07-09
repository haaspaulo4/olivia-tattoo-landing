"""
WhatsApp Service - Integração com neonize
Baseado no python-bot que funciona
"""
import sys
import io
import os
import base64
import threading
import time
import shutil
import ctypes
import traceback
from pathlib import Path

# ── Fix stdout/stderr para modo --windowed (PyInstaller) ──
class _DummyStream:
    encoding = 'utf-8'
    def write(self, *a, **kw): pass
    def flush(self): pass
    def fileno(self): raise OSError("no fileno in windowed mode")

if getattr(sys, 'frozen', False):
    if sys.stdout is None:
        sys.stdout = _DummyStream()
    if sys.stderr is None:
        sys.stderr = _DummyStream()

# ── Paths ──
if getattr(sys, 'frozen', False):
    base_dir = Path(sys.executable).parent
else:
    base_dir = Path(__file__).parent.parent

LOG_FILE = str(base_dir / "whatsapp_debug.log")

def _log(msg):
    """Log para arquivo, funciona mesmo sem console."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            import datetime
            f.write(f"[{datetime.datetime.now():%H:%M:%S}] {msg}\n")
    except:
        pass

# ── Monkey-patch SEGNO ANTES de importar neonize ──
# O neonize.events importa segno na inicialização e usa segno.make_qr().terminal()
# Isso causa UnicodeEncodeError no modo --windowed.
# Precisamos patchear ANTES de qualquer import do neonize.
try:
    import segno
    _original_segno_make = segno.make
    _original_segno_make_qr = getattr(segno, 'make_qr', segno.make)

    class _SafeQR:
        """Wrapper que silencia .terminal() mas preserva .save()"""
        def __init__(self, qr):
            self._qr = qr
        def terminal(self, *a, **kw):
            pass  # Silenciar impressão no console
        def save(self, *a, **kw):
            return self._qr.save(*a, **kw)
        def __getattr__(self, name):
            return getattr(self._qr, name)

    def _safe_make_qr(*args, **kwargs):
        return _SafeQR(_original_segno_make_qr(*args, **kwargs))

    # Patchear o módulo segno globalmente ANTES de importar neonize
    segno.make_qr = _safe_make_qr
    _log("segno patcheado com sucesso")
except ImportError as e:
    _log(f"AVISO: segno nao encontrado: {e}")
    _original_segno_make = None
    _original_segno_make_qr = None

# ── Agora sim importar neonize (que vai usar segno já patcheado) ──
try:
    from neonize.client import NewClient
    from neonize.events import MessageEv, ConnectedEv, PairStatusEv, QREv, event
    from neonize.utils import build_jid
    _log("neonize importado com sucesso")
except ImportError as e:
    _log(f"ERRO CRITICO: neonize nao encontrado: {e}\n{traceback.format_exc()}")
    raise

# ── Garantir que o módulo neonize.events use nosso segno patcheado ──
try:
    import neonize.events as _neonize_events
    if 'segno' in dir(_neonize_events) and _original_segno_make_qr is not None:
        import segno as _segno_mod
        _neonize_events.segno = _segno_mod
        _log("neonize.events.segno patcheado")
except Exception as e:
    _log(f"AVISO ao patchear neonize.events: {e}")

BOT_NAME = str(base_dir / "olivia_tattoo")
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
    """Gera imagem PNG do QR Code e retorna como base64."""
    try:
        if _original_segno_make is None:
            _log("segno nao disponivel para gerar QR base64")
            return None
        buf = io.BytesIO()
        qr = _original_segno_make(texto_qr)
        qr.save(buf, kind='png', scale=5)
        buf.seek(0)
        resultado = base64.b64encode(buf.read()).decode('utf-8')
        _log(f"QR base64 gerado com sucesso ({len(resultado)} chars)")
        return resultado
    except Exception as e:
        _log(f"ERRO ao gerar QR base64: {e}\n{traceback.format_exc()}")
        return None


def get_client():
    return client


def start_client():
    """Inicia o cliente em background, igual ao python-bot que funciona."""
    global client, current_qr_code, current_qr_base64

    current_qr_code = ""
    current_qr_base64 = ""

    try:
        _log(f"Criando NewClient em {BOT_NAME}")
        client = NewClient(BOT_NAME)
        _log("NewClient criado com sucesso")

        @client.event(PairStatusEv)
        def on_pair_status(c: NewClient, evt: PairStatusEv):
            global _last_pairing
            _last_pairing = str(evt.Status)
            _log(f"PairStatus: {evt.Status}")

        # ── QR Code handler via client.event.qr() ──
        # IMPORTANTE: Usamos client.event.qr() em vez de @client.event(QREv)
        # porque o QR é despachado via event._qr (raw bytes), NÃO via
        # event.execute/list_func. Isso substitui o handler default do neonize
        # (segno.make_qr().terminal()) que crasha no modo --windowed.
        def _qr_handler(c: NewClient, data_qr: bytes):
            """Handler de QR Code que recebe raw bytes do neonize."""
            global current_qr_code, _last_pairing
            _last_pairing = "qr"
            try:
                _log(f"QR Event recebido! data type={type(data_qr)} len={len(data_qr) if data_qr else 0}")

                # data_qr são os raw bytes do QR string
                if isinstance(data_qr, bytes):
                    qr_string = data_qr.decode('utf-8', errors='ignore')
                else:
                    qr_string = str(data_qr)

                current_qr_code = qr_string
                _log(f"QR code string: {current_qr_code[:80]}...")

                b64 = _gerar_qr_base64(current_qr_code)
                _log(f"QR b64 gerado: {b64 is not None}, callback registrado: {on_qr_callback is not None}")

                if on_qr_callback:
                    try:
                        on_qr_callback(current_qr_code, b64)
                        _log("QR callback executado com sucesso")
                    except Exception as e:
                        _log(f"ERRO no QR callback: {e}\n{traceback.format_exc()}")
            except Exception as e:
                _log(f"ERRO CRITICO no _qr_handler: {e}\n{traceback.format_exc()}")

        # Registrar o handler via event.qr() - substitui o default do neonize
        client.event.qr(_qr_handler)
        _log("QR handler registrado via client.event.qr()")

        # Também registrar via @client.event(QREv) como fallback
        # (este recebe QREv protobuf via list_func/execute)
        @client.event(QREv)
        def on_qr_event(c: NewClient, evt: QREv):
            global current_qr_code
            try:
                _log(f"QREv protobuf recebido (fallback)")
                code = getattr(evt, "Codes", None) or getattr(evt, "codes", None) or ""
                if isinstance(code, bytes):
                    code = code.decode('utf-8', errors='ignore')
                qr_str = str(code)

                # Se o _qr_handler já processou, não duplicar
                if current_qr_code and current_qr_code == qr_str:
                    _log("QREv: já processado pelo _qr_handler, ignorando")
                    return

                current_qr_code = qr_str
                b64 = _gerar_qr_base64(current_qr_code)
                if on_qr_callback:
                    on_qr_callback(current_qr_code, b64)
                    _log("QREv fallback: callback executado")
            except Exception as e:
                _log(f"ERRO no QREv fallback: {e}\n{traceback.format_exc()}")

        @client.event(ConnectedEv)
        def on_connected(c: NewClient, evt: ConnectedEv):
            global current_qr_code, _last_pairing
            _last_pairing = "connected"
            current_qr_code = ""
            _log("CONECTADO com sucesso!")
            if on_connected_callback:
                on_connected_callback()

        @client.event(MessageEv)
        def on_message(c: NewClient, evt: MessageEv):
            if on_message_callback:
                on_message_callback(evt)

        def _run():
            try:
                _log(f"Thread _run iniciando client.connect() em {BOT_NAME}")
                client.connect()
                _log("client.connect() retornou, entrando em event.wait()")
                event.wait()
            except Exception as e:
                _log(f"ERRO na conexão: {e}\n{traceback.format_exc()}")
                if on_disconnected_callback:
                    on_disconnected_callback()

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        return True

    except Exception as e:
        _log(f"ERRO ao criar NewClient: {e}\n{traceback.format_exc()}")
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