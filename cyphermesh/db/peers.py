import sqlite3
from datetime import datetime
from pathlib import Path

from cyphermesh.logger import logger

# Percorso ~/.cyphermesh
CYPHERMESH_DIR = Path.home() / ".cyphermesh"
CYPHERMESH_DIR.mkdir(parents=True, exist_ok=True)

# Percorso del database SQLite
DB_PATH = CYPHERMESH_DIR / "cyphermesh.db"


def create_table():
    """
    Crea la tabella peers per memorizzare i nodi noti (peer e discovery).
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS peers (
                ip TEXT NOT NULL,
                port INTEGER NOT NULL,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (ip, port)
            )
        """)
        conn.commit()


def add_or_update_peer(ip: str, port: int):
    """
    Inserisce o aggiorna un nodo nel database.
    Aggiorna il campo last_seen in caso di conflitto.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO peers (ip, port, last_seen)
            VALUES (?, ?, ?)
            ON CONFLICT(ip, port)
            DO UPDATE SET last_seen = CURRENT_TIMESTAMP
        """, (ip, port, datetime.now()))
        conn.commit()

def remove_node(ip: str, port: int):
    """
    Rimuove un nodo specifico dal database.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM peers WHERE ip = ? AND port = ?", (ip, port))
        conn.commit()


def get_all_peers():
    """
    Restituisce tutti i nodi noti dal database come oggetti Node.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ip, port FROM peers")
        rows = cursor.fetchall()
        return [{"ip": row[0], "port": row[1]} for row in rows]


# Esegui la creazione della tabella all'import
create_table()
