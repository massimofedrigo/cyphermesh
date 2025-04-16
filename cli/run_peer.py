import json
import sys
from pathlib import Path
from cyphermesh.crypto import ensure_keys_exist
from cyphermesh.logger import logger
from cyphermesh.bootstrap import bootstrap
from cyphermesh.node import Node, NodeType
from cyphermesh.peer.peer import start_peer

CONFIG_PATH = Path.home() / ".cyphermesh" / "peer_config.json"


def prompt_peer_config():
    print("🤝 Configurazione Peer")

    # Ottieni l'IP locale automaticamente
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        default_ip = s.getsockname()[0]
        s.close()
    except Exception:
        default_ip = "127.0.0.1"

    ip = input(f"Inserisci l'IP del tuo host o premi invio per utilizzare l'IP rilevato automaticamente [{default_ip}]: ").strip() or default_ip
    port = input("Inserisci la porta per il peer [9001]: ").strip() or "9001"

    # Modalità bootstrap
    print("Scegli la modalità di bootstrap:")
    print("1. Statico - Inserisci manualmente un Discovery Server")
    print("2. DNS Seed - Inserisci un record DNS per risolvere i discovery server")
    print("3. Broadcast Locale - Usa la scoperta via broadcast sulla LAN")
    print("4. Lista di Seed - Carica una lista di Discovery Server da un file")
    bootstrap_choice = input("Scelta [1/2/3/4]: ").strip()
    while bootstrap_choice not in ["1", "2", "3", "4"]:
        logger.error("Scelta di bootstrap non valida.")
        bootstrap_choice = input("Scelta [1/2/3/4]: ").strip()

    # Salva il file di configurazione per il peer (non include la modalità bootstrap)
    config = {
        "ip": ip,
        "port": int(port),
    }
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)
    logger.info(f"[✓] Configurazione peer salvata in {CONFIG_PATH}")

    # La logica di bootstrap (scelta modalità, contatto discovery, ecc.) verrà gestita separatamente,
    # per esempio in una funzione come `choose_discovery_server(config, bootstrap_choice)`.
    # Se necessiti, puoi passare bootstrap_choice a quella funzione.

    return config, bootstrap_choice


def load_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                config = json.load(f)
            logger.info("Configurazione peer trovata.")
            # Non richiede bootstrap_mode, poiché si assume che i discovery server già memorizzati nel database gestiranno l'update.
            return config, None
        except Exception as e:
            logger.error(f"Errore nel caricamento della configurazione: {e}")
            sys.exit(1)
    else:
        return prompt_peer_config()


def main():

    ensure_keys_exist()
    config, bootstrap_choice = load_config()
    this_peer = Node(config["ip"], config["port"], NodeType.PEER)

    # Se bootstrap_choice è disponibile, usala per determinare il discovery server da utilizzare.
    # Altrimenti, se già esiste la configurazione, presupponiamo che l'informazione sui discovery server sia già nel database.
    if bootstrap_choice:
        bootstrap(this_peer, bootstrap_choice)

    logger.info("[*] Avvio Peer...")
    start_peer(this_peer)


if __name__ == "__main__":
    main()
