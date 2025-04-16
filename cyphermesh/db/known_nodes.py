import sqlite3
from datetime import datetime
from pathlib import Path

from cyphermesh.node import Node, NodeType

# Percorso ~/.cyphermesh
CYPHERMESH_DIR = Path.home() / ".cyphermesh"
CYPHERMESH_DIR.mkdir(parents=True, exist_ok=True)

# Percorso del database SQLite
DB_PATH = CYPHERMESH_DIR / "cyphermesh.db"


def create_table():
    """
    Crea la tabella known_nodes per memorizzare i nodi noti (peer e discovery).
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS known_nodes (
                ip TEXT NOT NULL,
                port INTEGER NOT NULL,
                type TEXT CHECK(type IN ('peer', 'discovery')) DEFAULT 'peer',
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (ip, port)
            )
        """)
        conn.commit()


def add_or_update_node(node: Node):
    """
    Inserisce o aggiorna un nodo nel database.
    Aggiorna il campo last_seen e type in caso di conflitto.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO known_nodes (ip, port, type, last_seen)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(ip, port)
            DO UPDATE SET last_seen = CURRENT_TIMESTAMP,
                          type = excluded.type
        """, (node.ip, node.port, node.type.value, datetime.now()))
        conn.commit()


def remove_node(ip: str, port: int):
    """
    Rimuove un nodo specifico dal database.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM known_nodes WHERE ip = ? AND port = ?", (ip, port))
        conn.commit()


def get_all_nodes():
    """
    Restituisce tutti i nodi noti dal database come oggetti Node.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ip, port, type FROM known_nodes")
        rows = cursor.fetchall()
        return [Node(ip=row[0], port=row[1], type=row[2]) for row in rows]


def get_known_peers():
    """
    Restituisce tutti i nodi di tipo 'peer' dal database.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ip, port, type FROM known_nodes WHERE type = ?", (NodeType.PEER.value,))
        rows = cursor.fetchall()
        return [Node(ip=row[0], port=row[1], type=row[2]) for row in rows]


def get_known_discoveries():
    """
    Restituisce tutti i nodi di tipo 'discovery' dal database.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ip, port, type FROM known_nodes WHERE type = ?", (NodeType.DISCOVERY.value,))
        rows = cursor.fetchall()
        return [Node(ip=row[0], port=row[1], type=row[2]) for row in rows]


# Esegui la creazione della tabella all'import
create_table()
