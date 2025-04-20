import sys
import argparse
from cyphermesh.db.peers import add_or_update_peer
from cyphermesh.logger import logger


def main():
    parser = argparse.ArgumentParser(
        prog="cyphermesh-add-peer",
        description="Aggiunge manualmente un peer peer alla lista"
    )
    parser.add_argument(
        "peer",
        help="Indirizzo del peer peer da aggiungere, nel formato IP:PORT (es. 192.168.0.5:9001)"
    )
    args = parser.parse_args()

    # parsing IP e porta
    try:
        ip, port = args.peer.split(":")
        port = int(port)
    except Exception:
        logger.error("[DB] Formato peer non valido. Usare IP:PORT (es. 10.0.0.42:9001)")
        sys.exit(1)

    # inserimento nel database
    add_or_update_peer(ip, port)
    logger.info(f"[DB] Peer aggiunto con successo: {ip}:{port}")


if __name__ == "__main__":
    main()
