import json
import base58
from solders.keypair import Keypair

wallets = []
for i in range(100):
    kp = Keypair()
    wallets.append({
        "pub": str(kp.pubkey()),
        "priv": base58.b58encode(bytes(kp)).decode('utf-8')
    })
print(json.dumps(wallets))
