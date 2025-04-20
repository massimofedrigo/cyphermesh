import shutil
from pathlib import Path
import argparse
from cyphermesh.logger import logger

CONFIG_DIR = Path.home() / ".cyphermesh"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", action="store_true", help="Rimuovi solo config")
    p.add_argument("--db",     action="store_true", help="Rimuovi solo DB")
    p.add_argument("--all",    action="store_true", help="Rimuovi tutto")
    args = p.parse_args()

    if args.all:
        shutil.rmtree(CONFIG_DIR, ignore_errors=True)
        logger.info("Tutto ~/.cyphermesh rimosso")
        return

    if args.db:
        db = CONFIG_DIR / "cyphermesh.db"
        if db.exists(): db.unlink()
        logger.info("Database rimosso")

    if args.config:
        for fn in ["peer_config.json", "discovery_server_config.json"]:
            f = CONFIG_DIR/ fn
            if f.exists(): f.unlink()
        logger.info("File di configurazione rimossi")

    if not (args.all or args.db or args.config):
        logger.error("Specifica almeno --all, --config o --db")


if __name__ == "__main__":
    main()
