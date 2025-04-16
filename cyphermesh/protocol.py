import json
import uuid
from datetime import datetime


def generate_id() -> str:
    """Genera un ID univoco per ogni messaggio/evento utilizzando UUID4."""
    return str(uuid.uuid4())


def current_timestamp() -> str:
    """
    Restituisce l'ora attuale in formato ISO 8601 (UTC),
    per esempio: "2025-04-16T14:30:00Z".
    """
    return datetime.utcnow().isoformat() + "Z"


def make_message(type: str, payload: dict = None, msg_id: str = None) -> bytes:
    """
    Crea un messaggio standardizzato in formato JSON.

    Il messaggio contiene i seguenti campi:
      - type: Il tipo del messaggio (es. "JOIN", "HELLO", "GET_NODES", "NODE_LIST", ecc.).
      - id: Un identificatore univoco per il messaggio. Se non viene fornito, viene generato automaticamente.
      - payload: I dati specifici del messaggio. Se non fornito, viene usato un dizionario vuoto.
      - timestamp: La data e l'ora (UTC) in cui il messaggio è stato creato in formato ISO 8601.

    :param type: Il tipo del messaggio.
    :param payload: Il payload (dati) del messaggio.
    :param msg_id: Un identificatore univoco per il messaggio.
    :return: Il messaggio codificato in bytes (JSON).
    """
    if payload is None:
        payload = {}
    message = {
        "type": type,
        "id": msg_id or generate_id(),
        "payload": payload,
        "timestamp": current_timestamp()
    }
    return json.dumps(message).encode()


def parse_message(raw: bytes) -> dict:
    """
    Decodifica un messaggio da bytes a dictionary.

    Il messaggio deve contenere le chiavi "type", "id", "payload" e "timestamp".

    :param raw: Il messaggio in formato bytes.
    :return: Il dizionario risultante con le informazioni del messaggio.
    :raises ValueError: Se il messaggio non è valido.
    """
    try:
        message = json.loads(raw.decode())
        required_keys = ("type", "id", "payload", "timestamp")
        if not all(key in message for key in required_keys):
            raise ValueError(f"Messaggio mancante di uno dei campi obbligatori: {required_keys}")
        return message
    except Exception as e:
        raise ValueError(f"Messaggio non valido: {e}")
