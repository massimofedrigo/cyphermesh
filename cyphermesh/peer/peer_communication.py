import socket
import time

from cyphermesh.db.known_nodes import get_known_peers, add_or_update_node, get_all_nodes
from cyphermesh.logger import logger
from cyphermesh.node import Node
from cyphermesh.protocol import make_message, parse_message


def handle_peer_message(this_peer: Node, data: bytes):
    """Gestisce un messaggio ricevuto da un altro peer."""
    try:
        message = parse_message(data)

        if message["type"] == "HELLO":
            # Aggiungi peer che ci ha contattato
            new_peer = Node.from_dict(message["payload"])
            add_or_update_node(new_peer)

            # Rispondi con la lista dei peer conosciuti
            node_list = get_all_nodes()
            response = make_message(type="HERE_THE_NODES", payload=node_list)
            send_message_to_peer(new_peer, response)

        elif message["type"] == "HELLO_RESPONSE":
            # Aggiungi tutti i peer ricevuti
            for peer in payload["peers"]:
                add_peer(peer)

        elif msg_type == "peer_notify":
            # Aggiungi un peer che ci è stato notificato
            add_peer(payload["new_peer"])

    except Exception as e:
        logger.error(f"Errore nella gestione del messaggio da {addr}: {e}")


def send_message_to_peer(peer: Node, message: bytes):
    """Invia un messaggio a un singolo peer."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((peer.ip, peer.port))
            s.sendall(message)
    except Exception as e:
        logger.error(f"Errore invio a {peer.address()} -> {e}")


def broadcast_message(message: bytes, exclude=None):
    """Invia un messaggio a tutti i peer, con possibilità di escludere uno."""
    for peer in get_peers():
        if peer == exclude:
            continue
        try:
            ip, port = peer.split(":")
            send_message_to_peer(ip, int(port), message)
        except Exception:
            continue


def notify_new_peer(this_peer: Node):
    """Invia una notifica a tutti i peer su un nuovo peer conosciuto."""
    msg = make_message("peer_notify", {"new_peer": new_peer})
    broadcast_message(msg, exclude=this_peer)


def hello(this_peer: Node, other_peer: Node):
    """Invia un messaggio peer_hello ad un peer per iniziare la comunicazione."""
    message = make_message("HELLO", this_peer.to_dict())
    send_message_to_peer(other_peer, message)


def hello_loop(this_peer: Node):
    while True:
        peers = get_known_peers()
        for peer in peers:
            hello(this_peer, peer)
        time.sleep(30)


def run_peer_server(this_peer: Node):
    """Avvia il server per ascoltare i messaggi dai peer."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((this_peer.ip, this_peer.port))
    s.listen()
    logger.info(f"[✓] Peer in ascolto su {this_peer.address()}...")

    while True:
        conn, addr = s.accept()
        data = conn.recv(1024)
        if data:
            handle_peer_message(this_peer, data)
        conn.close()
