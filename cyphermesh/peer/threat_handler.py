import json
from cyphermesh.crypto import verify_signature
from cyphermesh.web.db import save_event, update_reputation, get_reputation
from cyphermesh.logger import logger


# Supponiamo che i messaggi di tipo "event" siano già decodificati da protocol.py
def handle_event_message(event):
    """
    Gestisce un evento di minaccia:
    - Verifica la firma
    - Aggiorna il database e la reputazione
    - Ritorna True se l'evento è valido, altrimenti False.
    """
    event_id = event.get("id")

    # Rimuoviamo la firma per la verifica
    signature = event.pop("signature", None)
    pubkey = event.get("reporter_pubkey")
    event_str = json.dumps(event, sort_keys=True)

    is_valid = verify_signature(event_str, signature, pubkey.encode())
    rep = get_reputation(pubkey)

    if rep < -10:
        logger.info(f"[THREAT] Ignorato: reputazione troppo bassa per {pubkey[:30]} ({rep})")
        return False

    # Reinseriamo la firma
    event["signature"] = signature

    save_event(event, is_valid)

    if is_valid:
        logger.info(f"[THREAT] Evento valido ricevuto da {pubkey[:30]} | Reputazione: {rep}")
        update_reputation(pubkey, +1)
    else:
        logger.info(f"[THREAT] Evento non valido da {pubkey[:30]} | Reputazione: {rep}")
        update_reputation(pubkey, -3)

    return is_valid
