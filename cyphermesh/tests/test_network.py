import subprocess
import time
import json

from cyphermesh.protocol import make_message
from cyphermesh.crypto import generate_keypair, sign_data
from cyphermesh.peer.peer_communication import send_message_to_peer


def run_discovery_server():
    subprocess.Popen(["python", "discovery_server.py"])
    print("[🚀] Discovery server avviato")


def run_peer(port):
    subprocess.Popen(["python", "main.py", "127.0.0.1", str(port)])
    print(f"[👤] Peer avviato sulla porta {port}")


def send_threat_event(ip, port):
    print("[⚠️] Generazione e invio evento di minaccia...")

    # Genera chiavi temporanee per il peer che segnala la minaccia
    priv, pub = generate_keypair()

    # Costruisci evento
    event = {
        "id": "event-001",
        "type": "intrusion",
        "severity": "high",
        "timestamp": time.time(),
        "reporter_pubkey": pub.decode(),
    }

    # Firma
    event_json = json.dumps(event, sort_keys=True)
    signature = sign_data(event_json)

    # Aggiungi firma all'evento
    event["signature"] = signature

    # Impacchetta il messaggio
    msg = make_message("event", event)

    # Invia a uno dei peer
    send_message_to_peer(ip, port, msg)
    print("[✅] Evento inviato")


if __name__ == "__main__":
    # 1. Avvia discovery_server server
    run_discovery_server()

    time.sleep(1)  # Attendi che il discovery_server server sia pronto

    # 2. Avvia 3 peer
    peer_ports = [9101, 9102, 9103]
    for port in peer_ports:
        run_peer(port)

    # 3. Attendi che i peer si registrino e comunichino
    time.sleep(5)

    # 4. Invia un evento al primo peer
    send_threat_event("127.0.0.1", 9101)

    # 5. Mantieni vivo il test (CTRL+C per interrompere)
    print("[🔁] Test in esecuzione. Premi CTRL+C per uscire.")
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("[🛑] Test interrotto.")
