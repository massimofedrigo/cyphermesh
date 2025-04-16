import logging
import sys

USE_EMOJI = False  # Cambia questo a False se vuoi log senza emoji

# Emoji map (per livelli di log)
EMOJIS = {
    "INFO": "ℹ️" if USE_EMOJI else "",
    "DEBUG": "🐞" if USE_EMOJI else "",
    "WARNING": "⚠️" if USE_EMOJI else "",
    "ERROR": "❌" if USE_EMOJI else "",
    "CRITICAL": "🔥" if USE_EMOJI else ""
}


class CustomFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        # Se le emoji sono attivate, usa solo l'emoji, altrimenti usa il formato tradizionale
        if USE_EMOJI:
            emoji = EMOJIS.get(levelname, "")
            record.msg = f"{emoji} {record.msg}"
            return super().format(record)  # Usa il formato del messaggio con l'emoji
        else:
            record.msg = f"[{levelname}] {record.msg}"  # Usa il formato tradizionale con il livello
            return super().format(record)


# Logger setup
logger = logging.getLogger("cyphermesh")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
formatter = CustomFormatter("%(message)s")  # Mostra solo il messaggio (con o senza emoji)
handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(handler)
