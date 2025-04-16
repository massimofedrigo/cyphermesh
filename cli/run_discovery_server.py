import json
import sys
from pathlib import Path
from cyphermesh.crypto import ensure_keys_exist
from cyphermesh.discovery_server.discovery_server import start_discovery_server
from cyphermesh.logger import logger

CONFIG_PATH = Path.home() / ".cyphermesh" / "discovery_server_config.json"


def main():
    ensure_keys_exist()

    if not CONFIG_PATH.exists():
        logger.error(f"Configurazione discovery server non trovata in {CONFIG_PATH}. Esegui prima cyphermesh-install.")
        sys.exit(1)

    with open(CONFIG_PATH) as f:
        config = json.load(f)

    host = config.get("HOST", "127.0.0.1")
    port = config.get("PORT", 9000)

    logger.info(f"[*] Avvio Discovery Server su {host}:{port}...")
    start_discovery_server(host, port)


if __name__ == "__main__":
    main()
