"""
Teste direto da neonize para ver como o QR Code é capturado
"""
from neonize.client import NewClient
from neonize.events import QREv, ConnectedEv
import threading
import time

qr_data = []

def on_qr(client, evt):
    qr = evt.Codes
    qr_str = str(qr) if qr else ""
    print(f"EVENTO QR RECEBIDO! Tamanho: {len(qr_str)}")
    print(f"QR (primeiros 80): {qr_str[:80]}")
    qr_data.append(qr_str)

def on_connected(client, evt):
    print("EVENTO CONECTADO!")

client = NewClient("teste_qr")
client.event(QREv)(on_qr)
client.event(ConnectedEv)(on_connected)

def run():
    print("Conectando...")
    client.connect()

t = threading.Thread(target=run, daemon=True)
t.start()

# Espera um pouco
for i in range(10):
    time.sleep(1)
    if qr_data:
        print(f"QR capturado com sucesso! Total: {len(qr_data)}")
        break
    if client.is_connected:
        print("Ja conectado!")
        break

if not qr_data:
    print("Nenhum QR recebido pelo evento")
    # Tenta acessar atributos internos
    print(f"client.__dict__ keys: {[k for k in dir(client) if not k.startswith('_')]}")

print("Teste finalizado")