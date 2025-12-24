import sqlite3
from pathlib import Path
from contextlib import contextmanager
from cyphermesh.logger import logger
from cyphermesh.config import *
import os

def init_db():
    """
    Inizializza il database, crea le tabelle e abilita WAL mode.
    Da chiamare all'avvio dell'applicazione.
    """
    try:
        with get_db_connection() as conn:
            # Abilita Write-Ahead Logging per migliore concorrenza
            conn.execute("PRAGMA journal_mode=WAL;")

            # Tabella Peers
            conn.execute("""
                CREATE TABLE IF NOT EXISTS peers (
                    ip TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (ip, port)
                )
            """)

            # Tabella Eventi
            conn.execute("""
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

            # Tabella Reputazione
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reputation (
                    pubkey TEXT PRIMARY KEY,
                    score INTEGER DEFAULT 0
                )
            """)
            logger.info("[DB] Database inizializzato (WAL mode enabled).")
    except Exception as e:
        logger.error(f"[DB INIT ERROR] {e}")


def get_db_connection():
    """
    Restituisce una connessione configurata con timeout alto e Row factory.
    """
    # timeout=30.0 significa che aspetterà fino a 30 secondi se il file è
    # bloccato prima di lanciare un errore.
    conn = sqlite3.connect(str(DB_PATH), timeout=30.0)

    # Permette di accedere alle colonne per nome (row['ip'])
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_cursor(commit=False):
    """
    Helper per gestire apertura/chiusura e commit automatici.
    Uso:
    with db_cursor(commit=True) as cur:
        cur.execute(...)
    """
    conn = get_db_connection()
    try:
        yield conn.cursor()
        if commit:
            conn.commit()
    except Exception as e:
        if commit:
            conn.rollback()
        logger.error(f"[DB QUERY ERROR] {e}")
        raise e
    finally:
        conn.close()
