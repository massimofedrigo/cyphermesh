import socket
import time
from cyphermesh.logger import logger
from cyphermesh.protocol import make_message, parse_message
from cyphermesh.db.known_nodes import add_or_update_node, get_known_peers, get_known_discoveries
from cyphermesh.node import Node, NodeType
from cyphermesh.peer.peer_communication import hello


def register_with_discovery(this_node: Node, discovery_node: Node):
    """
    Registra this_node presso il discovery node:
     - Invia JOIN tramite send_join.
     - Richiede la lista dei nodi tramite send_get_nodes.
     - Per ogni nodo ricevuto:
         - Se il nodo è diverso da this_node, lo registra nel database.
         - Se entrambi sono peer, invia un messaggio HELLO.
         - Se il nodo è di tipo discovery (o bootstrap), esegue una registrazione ricorsiva.

    :param this_node: Istanza di Node che si registra.
    :param discovery_node: Istanza di Node da cui ottenere la lista dei nodi.
    """
    try:
        if not join(this_node, discovery_node):
            return
        node_list = get_nodes(this_node, discovery_node)
        for raw_node in node_list:
            # raw_node dovrebbe essere un dizionario, ad es. {"ip": "192.168.1.10", "port": 9001, "type": "peer"}
            node = Node.from_dict(raw_node)
            if node.address() != this_node.address():
                add_or_update_node(node)
                if node.type == NodeType.PEER.value and this_node.type == NodeType.PEER.value:
                    hello(this_node, node)
                elif node.type == NodeType.DISCOVERY.value:
                    # Effettua la registrazione ricorsiva per i nodi di tipo discovery/boostrap
                    register_with_discovery(this_node, node)
    except Exception as e:
        logger.error(f"[DISCOVERY_CLIENT] Errore in register_with_discovery: {e}")


def get_nodes_loop(this_peer: Node):
    while True:
        discovery_nodes = get_known_discoveries()
        for discovery in discovery_nodes:
            nodes = get_nodes(this_peer, discovery)
            for node in nodes:
                add_or_update_node(node)
                if node.is_peer():
                    send_hello(this_peer, node)
        time.sleep(120)


def join(this_node: Node, discovery_node: Node) -> bool:
    """
    Registra this_node presso il discovery_node.
    Invia un messaggio di tipo JOIN con le informazioni di this_node.

    :param this_node: Istanza di Node che si registra.
    :param discovery_node: Istanza di Node a cui ci connettiamo.
    :return: True se la registrazione ha avuto successo, False altrimenti.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((discovery_node.ip, discovery_node.port))
        # Prepara il messaggio JOIN con le informazioni di this_node
        message = make_message(type='JOIN', payload=this_node.to_dict())
        s.send(message)
        # Ricevi la risposta dal discovery node e decodificala
        response_data = s.recv(1024)
        s.close()
        response = parse_message(response_data)
        if response["type"] != "JOIN_APPROVED":
            logger.error(
                f"[DISCOVERY_CLIENT] La risposta dal discovery node {discovery_node.address()} non è JOIN_APPROVED.")
            return False
        # Salva il discovery node nel database (assumendo add_or_update_node accetti ip, port, type)
        add_or_update_node(discovery_node.ip, discovery_node.port, discovery_node.type)
        logger.info(f"[DISCOVERY_CLIENT] Registrato {this_node.address()} presso {discovery_node.address()}")
        return True
    except Exception as e:
        logger.error(f"[DISCOVERY_CLIENT] Errore in join: {e}")
        return False


def get_nodes(this_peer: Node, discovery_node: Node) -> list:
    """
    Richiede al discovery node la lista dei nodi registrati.

    :param this_peer: Istanza di Node per identificare la richiesta.
    :param discovery_node: Istanza di Node a cui inviare la richiesta.
    :return: Una lista di dizionari (ogni dizionario rappresenta un nodo), o una lista vuota in caso di errore.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((discovery_node.ip, discovery_node.port))
        message = make_message('WANT_NODES', payload=this_peer.to_dict())
        s.send(message)
        data = s.recv(4096)
        s.close()
        response = parse_message(data)
        if response["type"] != "HERE_THE_NODES":
            logger.error(f"[DISCOVERY_CLIENT] Risposta inattesa dal discovery node: {response['type']}")
            return []
        nodes = response["payload"].get("nodes", [])
        logger.info(f"[DISCOVERY_CLIENT] HERE_THE_NODES ricevuti: {nodes}")
        return nodes
    except Exception as e:
        logger.error(f"[DISCOVERY_CLIENT] Errore in send_get_nodes: {e}")
        return []
