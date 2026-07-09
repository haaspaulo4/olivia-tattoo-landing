"""
Diagnóstico completo do envio de mensagens WhatsApp via neonize.
Roda com o sistema aberto (usa a sessão já conectada).
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from neonize.client import NewClient
from neonize.events import ConnectedEv, QREv, event
from neonize.utils import build_jid

BOT_NAME = "olivia_tattoo"
NUMERO_TESTE = "5544998463463"  # Troque se quiser

print("=" * 60)
print("  DIAGNÓSTICO DE ENVIO - NEONIZE")
print("=" * 60)

# 1. Iniciar o cliente usando a sessão existente
print("\n[1/5] Iniciando cliente com sessão existente...")
client = NewClient(BOT_NAME)

connected_event = False

@client.event(ConnectedEv)
def on_connected(c, evt):
    global connected_event
    connected_event = True
    print("[OK] Conectado com sucesso!")

@client.event(QREv)
def on_qr(c, evt):
    print("[AVISO] QR Code recebido - sessão NÃO está autenticada!")
    print("        Escaneie o QR Code no app e rode novamente.")

import threading
def _run():
    client.connect()
    event.wait()

t = threading.Thread(target=_run, daemon=True)
t.start()

# Esperar conexão
for i in range(15):
    time.sleep(1)
    if connected_event or client.is_connected:
        break
    print(f"  Aguardando conexão... {i+1}s")

if not client.is_connected:
    print("\n[ERRO] Não conseguiu conectar em 15s. Saindo.")
    sys.exit(1)

print(f"  client.is_connected = {client.is_connected}")

# 2. Verificar se o número existe no WhatsApp
print(f"\n[2/5] Verificando se {NUMERO_TESTE} está no WhatsApp...")
try:
    resultados = client.is_on_whatsapp(NUMERO_TESTE)
    for r in resultados:
        print(f"  Query: {r.Query}")
        print(f"  JID:   {r.JID}")
        print(f"  IsIn:  {r.IsIn}")
        if not r.IsIn:
            print("\n  [ERRO CRÍTICO] Este número NÃO está registrado no WhatsApp!")
            print("  A mensagem NUNCA será entregue. Verifique o número.")
except Exception as e:
    print(f"  [ERRO] Falha ao verificar número: {e}")

# 3. Testar build_jid
print(f"\n[3/5] Testando construção do JID...")
jid = build_jid(NUMERO_TESTE)
print(f"  JID User:   {jid.User}")
print(f"  JID Server: {jid.Server}")

# 4. Verificar se is_on_whatsapp retorna um JID diferente
print(f"\n[4/5] Comparando JID do build_jid vs is_on_whatsapp...")
try:
    resultados = client.is_on_whatsapp(NUMERO_TESTE)
    for r in resultados:
        if r.IsIn:
            correto_jid = r.JID
            print(f"  JID correto (is_on_whatsapp): User={correto_jid.User} Server={correto_jid.Server}")
            print(f"  JID usado   (build_jid):      User={jid.User} Server={jid.Server}")
            if correto_jid.User != jid.User or correto_jid.Server != jid.Server:
                print("\n  [PROBLEMA ENCONTRADO] Os JIDs são DIFERENTES!")
                print("  Você deve usar o JID retornado por is_on_whatsapp!")
            else:
                print("  [OK] JIDs são iguais.")
except Exception as e:
    print(f"  [ERRO] {e}")

# 5. Tentar enviar e inspecionar o retorno
print(f"\n[5/5] Tentando enviar mensagem de teste...")
try:
    # Usar o JID correto do is_on_whatsapp se disponível
    resultados = client.is_on_whatsapp(NUMERO_TESTE)
    jid_envio = None
    for r in resultados:
        if r.IsIn:
            jid_envio = r.JID
            break

    if jid_envio is None:
        print("  [ERRO] Número não encontrado no WhatsApp. Usando build_jid...")
        jid_envio = build_jid(NUMERO_TESTE)

    print(f"  Enviando para: User={jid_envio.User} Server={jid_envio.Server}")
    response = client.send_message(jid_envio, "🔧 Teste de diagnóstico - Olivia Tattoo Sistema")
    print(f"  [RESPOSTA DO SERVIDOR]")
    print(f"    Timestamp: {response.Timestamp}")
    print(f"    ID:        {response.ID}")
    print(f"    ServerID:  {getattr(response, 'ServerID', 'N/A')}")
    print(f"    DebugTimings: {getattr(response, 'DebugTimings', 'N/A')}")
    print(f"\n  [SUCESSO] Mensagem enviada! Verifique no celular se chegou.")

except Exception as e:
    print(f"\n  [ERRO NO ENVIO] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("  DIAGNÓSTICO CONCLUÍDO")
print("=" * 60)
input("\nPressione ENTER para sair...")
