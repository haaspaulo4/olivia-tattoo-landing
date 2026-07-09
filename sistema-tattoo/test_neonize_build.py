import sys
import os
import traceback

print("Testing neonize connect...")
try:
    from neonize.client import NewClient
    from neonize.events import QREv
    print("Neonize imported successfully!")
    
    bot_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_bot")
    print(f"Creating client at {bot_name}...")
    client = NewClient(bot_name)
    print("Client created successfully!")
    
    @client.event(QREv)
    def on_qr(c: NewClient, evt: QREv):
        print("QR Event fired!")
        c.disconnect()

    print("Connecting...")
    client.connect()
    
except Exception as e:
    print("Failed:")
    traceback.print_exc()

print("Done.")
