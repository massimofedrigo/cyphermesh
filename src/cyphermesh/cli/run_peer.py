import sys
import argparse
from cyphermesh.core.node import Node
from cyphermesh.config import resolve_node_identity


def main():
    parser = argparse.ArgumentParser(
        prog="cyphermesh-run-peer",
        description="Run a P2P node (Zero-Conf mode)"
    )
    # Opzionale: lasciamo solo la possibilità di stampare la versione o help
    args = parser.parse_args()

    # 1. Config resolution (Environment variables or Default)
    # Non passiamo più argomenti CLI, lasciamo fare a config.py
    ip, port = resolve_node_identity()

    # 2. Core start
    # Niente più bootstrap_mode o seed_ip
    node = Node(ip=ip, port=port)

    try:
        node.start()
    except KeyboardInterrupt:
        node.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
    