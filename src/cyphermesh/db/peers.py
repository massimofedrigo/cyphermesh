from datetime import datetime
from cyphermesh.db.core import db_cursor


def add_or_update_peer(ip: str, port: int):
    """
    Inserisce o aggiorna un nodo. Thread-safe grazie al locking di SQLite + timeout.
    """
    with db_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO peers (ip, port, last_seen)
            VALUES (?, ?, ?)
            ON CONFLICT(ip, port)
            DO UPDATE SET last_seen = ?
        """, (ip, port, datetime.now(), datetime.now()))

def remove_node(ip: str, port: int):
    with db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM peers WHERE ip = ? AND port = ?", (ip, port))

def get_all_peers():
    """
    Restituisce una lista di dizionari {'ip': ..., 'port': ...}
    """
    with db_cursor(commit=False) as cur:
        cur.execute("SELECT ip, port FROM peers ORDER BY last_seen DESC")
        rows = cur.fetchall()
        # Convertiamo sqlite3.Row in dict puro
        return [{"ip": r["ip"], "port": r["port"]} for r in rows]
