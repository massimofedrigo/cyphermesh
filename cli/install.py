import os
import json
from pathlib import Path
import socket
from cyphermesh.logger import logger

CONFIG_DIR = Path.home() / ".cyphermesh"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

DISCOVERY_SERVER_CONFIG_PATH = CONFIG_DIR / "discovery_server_config.json"
PEER_CONFIG_PATH = CONFIG_DIR / "peer_config.json"


def ask_role():
    print("Benvenuto in cyphermesh Setup!")
    print("Che ruolo vuoi assegnare a questo nodo?")
    print("1. Discovery Server")
    print("2. Peer")
    print("3. Entrambi")
    choice = input("Scelta [1/2/3]: ").strip()
    return choice


def ask_local_ip_choice():
    # Ottieni l'IP locale automaticamente
    my_ip = get_local_ip()
    logger.info(f"IP locale rilevato automaticamente: {my_ip}")

    # Chiedi conferma o modifica dell'IP locale
    use_default_ip = input(
        f"Vuoi usare questo IP [{my_ip}] per l'host? (Premi Invio per confermare o inserisci un altro IP): ").strip()
    if use_default_ip:
        my_ip = use_default_ip

    return my_ip


def setup_discovery_server_config():
    print("📡 Configurazione Discovery Host")
    my_ip = ask_local_ip_choice()
    port = input("Inserisci la porta per il Discovery Server [9000]: ").strip() or "9000"
    config = {
        "HOST": my_ip,
        "PORT": int(port)
    }
    with open(DISCOVERY_SERVER_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)
    logger.info(f"[✓] Configurazione Discovery Server salvata in {DISCOVERY_SERVER_CONFIG_PATH}")


def get_local_ip():
    """Restituisce l'IP locale del dispositivo (IP della rete)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connessione a un server remoto
        ip = s.getsockname()[0]  # Ottiene l'indirizzo IP locale
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"  # In caso di errore, torna il valore predefinito (localhost)


def setup_peer_config(both=False):
    print("🤝 Configurazione Peer")
    # Ottieni l'IP locale automaticamente
    my_ip = ask_local_ip_choice()

    # Chiedi all'utente la porta del peer
    port = input("Inserisci la porta per il peer [9001]: ").strip() or "9001"

    # Chiedi l'IP del discovery_server server
    default_discovery_ip = my_ip if both else "127.0.0.1"

    discovery_ip = input(f"IP del discovery_server server [{default_discovery_ip}]: ").strip() or default_discovery_ip

    # Chiedi la porta del discovery_server server
    discovery_port = input("Porta del discovery_server server [9000]: ").strip() or "9000"

    # Crea il dizionario di configurazione
    config = {
        "MY_HOST": my_ip,  # Aggiungi l'IP dell'host
        "MY_PORT": int(port),
        "DISCOVERY_HOST": discovery_ip,
        "DISCOVERY_PORT": int(discovery_port)
    }

    # Salva la configurazione nel file
    os.makedirs(os.path.dirname(PEER_CONFIG_PATH), exist_ok=True)  # Crea la cartella se non esiste
    with open(PEER_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

    logger.info(f"[✓] Configurazione peer salvata in {PEER_CONFIG_PATH}")



def main():
    choice = ask_role()

    if choice == "1":
        setup_discovery_server_config()
    elif choice == "2":
        setup_peer_config()
    elif choice == "3":
        setup_discovery_server_config()
        setup_peer_config(True)
    else:
        print("Scelta non valida. Riprova.")


if __name__ == "__main__":
    main()
