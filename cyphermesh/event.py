import json
import time
import hashlib
from cyphermesh.crypto import sign_data, PUBLIC_KEY_PATH


def load_own_pubkey_str() -> str:
    """
    Carica la chiave pubblica (in formato PEM) come stringa.

    :return: La chiave pubblica in formato stringa.
    """
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return f.read().decode()


def generate_event_id(event_data: dict) -> str:
    """
    Genera un ID univoco basato sull'hash SHA256 dei dati dell'evento.
    L'hash viene calcolato sui dati ordinati (escludendo la firma).

    :param event_data: I dati dell'evento senza il campo "signature".
    :return: Una stringa rappresentante l'hash dell'evento.
    """
    event_json = json.dumps(event_data, sort_keys=True)
    return hashlib.sha256(event_json.encode()).hexdigest()


def create_event(source_ip: str, threat_type: str, severity: str) -> dict:
    """
    Crea un evento firmato, pronto per essere condiviso nella rete.

    L'evento contiene:
      - source_ip: l'indirizzo dell'host interessato.
      - threat_type: il tipo di minaccia (es. "port_scan", "malware", ecc.).
      - severity: il livello di gravità ("low", "medium", "high", ecc.).
      - timestamp: il momento della creazione dell'evento.
      - reporter_pubkey: la chiave pubblica del peer che genera l'evento.
      - id: un ID univoco generato in base all'hash dei dati.
      - signature: la firma digitale dell'evento (apposta sul JSON dei dati, in ordine).

    :param source_ip: L'IP dell'host interessato.
    :param threat_type: Il tipo di minaccia.
    :param severity: La gravità della minaccia.
    :return: Un dizionario contenente l'evento completo.
    """
    reporter_pubkey = load_own_pubkey_str()

    event_data = {
        "source_ip": source_ip,
        "threat_type": threat_type,
        "severity": severity,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "reporter_pubkey": reporter_pubkey,
    }

    # Genera l'ID basato sui dati dell'evento (prima di aggiungere la firma)
    event_id = generate_event_id(event_data)
    event_data["id"] = event_id

    # Firma il contenuto (senza il campo signature, che verrà aggiunto dopo)
    event_str = json.dumps(event_data, sort_keys=True)
    signature = sign_data(event_str)
    event_data["signature"] = signature

    return event_data
