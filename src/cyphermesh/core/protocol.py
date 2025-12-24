import json
import uuid
import struct
import socket
from datetime import datetime
from typing import Optional


def generate_id() -> str:
    """Genera un ID univoco per ogni messaggio/evento utilizzando UUID4."""
    return str(uuid.uuid4())


def current_timestamp() -> str:
    """
    Restituisce l'ora attuale in formato ISO 8601 (UTC),
    per esempio: "2025-04-16T14:30:00Z".
    """
    return datetime.utcnow().isoformat() + "Z"


def send_message(sock: socket.socket, msg_type: str, payload: dict = None, msg_id: str = None):
    """
    Invia un messaggio con header di lunghezza (4 bytes big-endian).
    Evita la frammentazione TCP.
    """
    if payload is None: payload = {}
    
    message = {
        "type": msg_type,
        "id": msg_id or str(uuid.uuid4()),
        "payload": payload,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    json_bytes = json.dumps(message).encode('utf-8')
    
    # Pack 4 bytes: Lunghezza del messaggio (unsigned int, big-endian)
    header = struct.pack('>I', len(json_bytes))
    
    # Invia Header + Body
    sock.sendall(header + json_bytes)


def receive_message(sock: socket.socket) -> Optional[dict]:
    """
    Legge esattamente un messaggio completo gestendo il framing.
    Restituisce None se la connessione è chiusa.
    """
    # 1. Leggi i primi 4 byte (Header Lunghezza)
    header_data = _read_n_bytes(sock, 4)
    if not header_data:
        return None
        
    msg_length = struct.unpack('>I', header_data)[0]
    
    # 2. Leggi esattamente 'msg_length' bytes (Body)
    body_data = _read_n_bytes(sock, msg_length)
    if not body_data:
        return None
        
    try:
        return json.loads(body_data.decode('utf-8'))
    except json.JSONDecodeError:
        return None


def _read_n_bytes(sock: socket.socket, n: int) -> Optional[bytes]:
    """Helper per leggere esattamente n bytes dal socket."""
    data = b''
    while len(data) < n:
        try:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        except socket.error:
            return None
    return data
