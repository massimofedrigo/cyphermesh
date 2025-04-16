import socket
import threading
from cyphermesh.logger import logger


# Set di peer conosciuti (formato "IP:PORT")
PEERS = set()


def handle_client(conn, addr):
    """
    Gestisce la comunicazione con un peer connesso.
    Se il messaggio inizia con "JOIN", registra il peer.
    Se il messaggio è "GET_PEERS", invia la lista dei peer.
    """
    logger.info(f"[✓] Nuovo peer connesso: {addr[0]}:{addr[1]}")
    try:
        data = conn.recv(1024)
        if data:
            message = data.decode().strip()
            if message.startswith("JOIN"):
                parts = message.split()
                if len(parts) >= 2:
                    peer = parts[1]
                    PEERS.add(peer)
                    logger.info(f"[+] Peer aggiunto: {peer}")
            elif message == "GET_PEERS":
                # Invia la lista dei peer, separata da newline
                peers_list = "\n".join(PEERS)
                conn.send(peers_list.encode())
                logger.info(f"[✓] Inviata lista dei peer: {PEERS}")
    except Exception as e:
        logger.error("Errore durante la gestione del peer", exc_info=e)
    finally:
        conn.close()


def start_discovery_server(host: str, port: int):
    """
    Avvia il discovery_server server in ascolto sull'interfaccia e porta specificata.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen()
    logger.info(f"[✓] Discovery Server attivo su {host}:{port}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    # Il server ascolta su tutte le interfacce sulla porta 9000
    start_discovery_server("0.0.0.0", 9000)
