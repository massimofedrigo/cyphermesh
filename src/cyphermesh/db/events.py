from cyphermesh.db.core import db_cursor
from cyphermesh.models import ThreatEvent


def save_event(event: ThreatEvent):
    """
    Salva un oggetto ThreatEvent nel database.
    La proprietà valid_signature deve essere già stata settata.
    """
    with db_cursor(commit=True) as cur:
        cur.execute("""
        INSERT OR IGNORE INTO events (
            id, source_ip, threat_type, severity, timestamp,
            reporter_pubkey, signature, valid_signature
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.id,
            event.source_ip,
            event.threat_type,
            event.severity,
            event.timestamp,
            event.reporter_pubkey,
            event.signature,
            int(event.valid_signature) # SQLite non ha bool nativo
        ))


def update_reputation(pubkey: str, delta: int):
    """Aggiorna la reputazione atomicamente."""
    with db_cursor(commit=True) as cur:
        # Assicuriamo che la riga esista
        cur.execute("INSERT OR IGNORE INTO reputation (pubkey, score) VALUES (?, 0)", (pubkey,))
        # Aggiorniamo
        cur.execute("UPDATE reputation SET score = score + ? WHERE pubkey = ?", (delta, pubkey))


def get_reputation(pubkey: str) -> int:
    with db_cursor(commit=False) as cur:
        cur.execute("SELECT score FROM reputation WHERE pubkey = ?", (pubkey,))
        result = cur.fetchone()
        return result["score"] if result else 0


def get_reputations():
    with db_cursor(commit=False) as cur:
        cur.execute("SELECT pubkey, score FROM reputation ORDER BY score DESC")
        rows = cur.fetchall()
        # Nota: per compatibilità con il template HTML esistente che usa
        # indici (row[0]), restituiamo tuple o lasciamo Row accessibili per indice.
        # Qui convertiamo in tuple per sicurezza.
        return [(r["pubkey"], r["score"]) for r in rows]


def get_events():
    with db_cursor(commit=False) as cur:
        cur.execute("""
            SELECT id, source_ip, threat_type, severity, timestamp, reporter_pubkey, valid_signature
            FROM events
            ORDER BY timestamp DESC
            LIMIT 100
        """)
        rows = cur.fetchall()
        # Ritorniamo i Row objects, che nel template HTML possono essere accessi sia come dict che come tuple
        return rows
