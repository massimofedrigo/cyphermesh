import socket
import time
from cyphermesh.db import get_all_peers, add_or_update_peer
from cyphermesh.logger import logger
from cyphermesh.protocol import make_message, parse_message


class Peer:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

    def address(self) -> str:
        return f"{self.ip}:{self.port}"

    def to_dict(self) -> dict:
        return {"ip": self.ip, "port": self.port}

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d["ip"], d["port"])

    def __eq__(self, other): return isinstance(other, Peer) and self.address() == other.address()

    def __hash__(self):    return hash(self.address())


def send_message(other: Peer, msg: bytes):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((other.ip, other.port))
            s.sendall(msg)
    except Exception as e:
        logger.error(f"[SEND -> {other.address()}] {e}")


def handle_received_message(me: Peer, data: bytes):
    try:
        m = parse_message(data)
        t = m["type"]
        p = m["payload"]
        other = Peer.from_dict(p["peer_server"])

        if t == "HELLO":
            logger.info(f"[RECV <- {other.address()}] HELLO")
            add_or_update_peer(other.ip, other.port)
            logger.info(f"[DB] Peer aggiunto con successo: {other.address()}")

            # rispondo con HELLO_ACK + lista:
            hello_ack(me, other)

        elif t == "HELLO_ACK":
            peers = p.get("peer_list", [])
            logger.info(f"[RECV <- {other.address()}] HELLO_ACK: lista={peers}")
            for p in peers:
                add_or_update_peer(p["ip"], p["port"])
                logger.info(f"[DB] Peer aggiunto con successo: {p['ip']}:{p['port']}")

        else:
            logger.warning(f"[RECV <- {other.address()}] Tipo non gestito: [{t}]")

    except Exception as e:
        logger.error(f"[RECV <- {other.address()}] {e}")


def hello(me: Peer, other: Peer):
    # Protezione anti–self in un unico punto:
    if me.address() == other.address():
        logger.debug(f"[SEND -> {other.address()}] Skip self-HELLO.")
        return

    msg = make_message("HELLO", {"peer_server": me.to_dict()})
    send_message(other, msg)
    logger.info(f"[SEND -> {other.address()}] HELLO")


def hello_loop(me: Peer):
    while True:
        for row in get_all_peers():
            peer = Peer.from_dict(row)
            if peer.address() != me.address():
                hello(me, peer)
        time.sleep(30)


def hello_ack(me: Peer, other: Peer):
    rows = [row for row in get_all_peers()]
    ack = make_message("HELLO_ACK", {"peer_server": me.to_dict(), "peer_list": rows})
    send_message(other, ack)
    logger.info(f"[SEND -> {other.address()}] HELLO_ACK")


def run_peer_server(me: Peer):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((me.ip, me.port))
    s.listen()
    logger.info(f"[✓] Peer in ascolto su {me.address()}...")

    while True:
        conn, addr = s.accept()              # addr è (ip, porta) del mittente
        data = conn.recv(4096)
        if data:
            handle_received_message(me, data)
        conn.close()


def bootstrap(me: Peer, mode: str):
    """Modalità di bootstrap iniziale."""
    if mode == "1":  # manual
        ip = input("IP peer bootstrap: ").strip()
        port = int(input("Porta [9000]: ").strip() or 9000)
        seed = Peer(ip, port)
        add_or_update_peer(ip, port)
        logger.info(f"[BOOT] Peer aggiunto con successo: {seed.address()}")
    elif mode == "2":  # from file
        # bootstrap_from_file(my_ip, my_port)
        return

    elif mode == "3":  # dns
        # bootstrap_from_dns(my_ip, my_port)
        return

    elif mode == "4":  # broadcast
        # bootstrap_broadcast(my_ip, my_port)
        return
    else:
        logger.error("[BOOT] Modalità non implementata.")
