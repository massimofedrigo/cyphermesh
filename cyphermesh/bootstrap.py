from cyphermesh.discovery_client import register_with_discovery, get_peer_list, get_node_list
from cyphermesh.logger import logger
from cyphermesh.node import Node, NodeType


def bootstrap(this_peer: Node, bootstrap_mode: str):
    """
    Avvia il bootstrap del nodo, aggiungendo discovery server e peer al database.
    """
    if bootstrap_mode == "1":  # manual
        bootstrap_manual(this_peer)
    elif bootstrap_mode == "2":  # from file
        return
        # bootstrap_from_file(my_ip, my_port)
    elif bootstrap_mode == "3":  # dns
        return
        # bootstrap_from_dns(my_ip, my_port)
    elif bootstrap_mode == "4":  # broadcast
        return
        # bootstrap_broadcast(my_ip, my_port)
    else:
        logger.error(f"[BOOTSTRAP] Modalità di bootstrap non riconosciuta: {bootstrap_mode}")


def bootstrap_manual(this_node: Node):
    """
    L'utente inserisce manualmente IP e porta di un discovery server.
    """
    discovery_ip = input("Inserisci l'IP del discovery server: ").strip()
    discovery_port = int(input("Inserisci la porta del discovery server [9000]: ").strip() or 9000)

    discovery_node = Node(discovery_ip, discovery_port, NodeType.DISCOVERY)

    register_with_discovery(this_node, discovery_node)

