import sys
import argparse
import os
from cyphermesh.core.node import Node
from cyphermesh.config import resolve_node_identity


def main():
    parser = argparse.ArgumentParser(
        prog="cyphermesh-run-peer",
        description="Run a peer node"
    )
    # Node identity
    parser.add_argument("--ip", help="Override peer IP")
    parser.add_argument("--port", type=int, help="Override peer port")

    # Bootstrap e Seed
    parser.add_argument("--bootstrap", "-b",
                        choices=["CONNECT", "SEED"],
                        help="Bootstrap: CONNECT=connect to a node, SEED=wait for entrying connections")

    parser.add_argument("--seed-ip", help="Seed IP to connect to (only SEED mode)")
    parser.add_argument("--seed-port", type=int, help="Seed port (only SEED mode)")

    args = parser.parse_args()

    # 1. Config resolution (delegated to config.py)
    ip, port = resolve_node_identity(args.ip, args.port)

    # 2. Bootstrap variables resolution
    mode = args.bootstrap or os.environ.get("BOOTSTRAP_MODE") or "SEED"
    seed_ip = args.seed_ip or os.environ.get("SEED_IP")
    seed_port = args.seed_port or os.environ.get("SEED_PORT") or "9001"

    # 3. Core start
    node = Node(
        ip=ip,
        port=port,
        bootstrap_mode=mode,
        seed_ip=seed_ip,
        seed_port=int(seed_port)
    )

    try:
        node.start()
    except KeyboardInterrupt:
        node.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
