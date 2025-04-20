import sqlite3
from pathlib import Path

# Percorso per la directory dell'utente (~/.cyphermesh)
BASE_DIR = Path.home() / ".cyphermesh"

# Crea la cartella se non esiste
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Percorso del database
DB_PATH = BASE_DIR / "cyphermesh.db"


def init_db():
    """Inizializza il database e crea le tabelle necessarie."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Tabella per eventi
    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        source_ip TEXT,
        threat_type TEXT,
        severity TEXT,
        timestamp TEXT,
        reporter_pubkey TEXT,
        signature TEXT,
        valid_signature INTEGER
    )
    """)

    # Tabella reputazione per ogni chiave pubblica
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reputation (
        pubkey TEXT PRIMARY KEY,
        score INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()


def save_event(event: dict, valid: bool):
    """Salva un evento nel database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT OR IGNORE INTO events (id, source_ip, threat_type, severity, timestamp, reporter_pubkey, signature, valid_signature)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event["id"],
        event["source_ip"],
        event["threat_type"],
        event["severity"],
        event["timestamp"],
        event["reporter_pubkey"],
        event["signature"],
        int(valid)
    ))
    conn.commit()
    conn.close()


def update_reputation(pubkey: str, delta: int):
    """Aggiorna la reputazione di una chiave pubblica nel database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO reputation (pubkey, score) VALUES (?, 0)", (pubkey,))
    cur.execute("UPDATE reputation SET score = score + ? WHERE pubkey = ?", (delta, pubkey))
    conn.commit()
    conn.close()


def get_reputation(pubkey: str) -> int:
    """Recupera la reputazione di una chiave pubblica dal database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT score FROM reputation WHERE pubkey = ?", (pubkey,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else 0


def get_reputations():
    """Recupera tutte le reputazioni dal database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM reputation")
    reps = cur.fetchall()
    conn.close()
    return reps


def get_events():
    """Recupera tutti gli eventi dal database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, source_ip, threat_type, severity, timestamp, reporter_pubkey, valid_signature
        FROM events
        ORDER BY timestamp DESC
    """)
    events = cur.fetchall()
    conn.close()
    return events
