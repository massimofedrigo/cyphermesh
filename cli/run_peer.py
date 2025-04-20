import json, sys, threading, argparse, socket
from pathlib import Path
from cyphermesh.crypto      import ensure_keys_exist
from cyphermesh.logger      import logger
from cyphermesh.peer.peer   import Peer, run_peer_server, hello_loop, bootstrap
from cyphermesh.db.peers    import get_all_peers

CONFIG_PATH = Path.home() / ".cyphermesh" / "peer_config.json"


def prompt_for_missing(ip, port):
    if not ip:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            default_ip = s.getsockname()[0]; s.close()
        except:
            default_ip = "127.0.0.1"
        ip = input(f"Inserisci IP [default {default_ip}]: ").strip() or default_ip

    if not port:
        port_str = input("Inserisci porta [default 9001]: ").strip() or "9001"
        try:
            port = int(port_str)
        except ValueError:
            logger.error("Porta non valida, uso 9001")
            port = 9001

    return ip, port


def prompt_peer_config(initial_ip=None, initial_port=None):
    ip, port = prompt_for_missing(initial_ip, initial_port)
    # Salvo la config **solo** se non esiste:
    if not CONFIG_PATH.exists():
        cfg = {"ip": ip, "port": port}
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump(cfg, f, indent=2)
        logger.info(f"[✓] Config salvata in {CONFIG_PATH}")
    else:
        logger.info("Config già esistente, non riscritta")
    return {"ip": ip, "port": port}


def load_config():
    try:
        cfg = json.loads(CONFIG_PATH.read_text())
        logger.info(f"[✓] Configurazione caricata da {CONFIG_PATH}")
        return cfg
    except Exception as e:
        logger.error(f"Errore caricamento config: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(prog="cyphermesh-peer",
        description="Avvia un nodo Peer CypherMesh")
    parser.add_argument("--config",  "-c", help="Path al peer_config.json",
                        default=str(CONFIG_PATH))
    parser.add_argument("--ip",     help="Override IP del peer")
    parser.add_argument("--port",   type=int, help="Override porta del peer")
    parser.add_argument("--bootstrap", "-b",
                        choices=["1","2","3","4"],
                        help="Modalità di bootstrap (opzionale)")
    args = parser.parse_args()

    ensure_keys_exist()

    # --- Determino IP/PORTA finale ---
    if args.ip or args.port:
        ip, port = prompt_for_missing(args.ip, args.port)
    else:
        cfg_path = Path(args.config)
        if cfg_path.exists():
            cfg = load_config()
            ip, port = cfg["ip"], cfg["port"]
        else:
            cfg = prompt_peer_config(None, None)
            ip, port = cfg["ip"], cfg["port"]

    me = Peer(ip, port)

    # --- BOOTSTRAP se DB vuoto o se forzato da --bootstrap ---
    known = [p for p in get_all_peers() if Peer.from_dict(p).address() != me.address()]  # lista di Peer già in DB
    if not known or args.bootstrap:
        # se c'è --bootstrap lo uso, altrimenti chiedo un prompt
        mode = args.bootstrap or input(
            "DB vuoto, scegli modalità bootstrap [1=manual,2=dns,3=broadcast,4=file]: "
        ).strip()
        bootstrap(me, mode)

    # --- Avvio server e loop HELLO ---
    logger.info(f"[*] Avvio Peer su {me.address()}")
    threading.Thread(target=run_peer_server, args=(me,), daemon=True).start()
    threading.Thread(target=hello_loop,      args=(me,), daemon=True).start()

    try:
        while True: pass
    except KeyboardInterrupt:
        logger.info("Peer arrestato")


if __name__ == "__main__":
    main()
