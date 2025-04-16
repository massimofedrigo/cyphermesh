import threading
import time
from cyphermesh.logger import logger
from cyphermesh.node import Node
from cyphermesh.web.db import init_db
from cyphermesh.discovery_client import get_nodes_loop
from cyphermesh.peer.peer_communication import run_peer_server, hello_loop


def start_peer(this_peer: Node):
    """Avvia completamente il nodo peer, compresa la registrazione al discovery_server server."""

    # 1. Inizializza il database
    init_db()

    # 4. Avvia il server in un thread
    threading.Thread(target=run_peer_server, args=(this_peer), daemon=True).start()

    threading.Thread(target=hello_loop, args=(this_peer,), daemon=True).start()
    threading.Thread(target=get_nodes_loop, args=(this_peer,), daemon=True).start()



