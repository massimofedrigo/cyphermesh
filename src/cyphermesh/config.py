import os
import json
import socket
from pathlib import Path
from cyphermesh.logger import logger

# --- CONSTANTS (Static) ---

ENV_DATA_DIR = os.environ.get("CYPHER_DATA_DIR")

if ENV_DATA_DIR:
    BASE_DIR = Path(ENV_DATA_DIR)
else:
    BASE_DIR = Path.home() / ".cyphermesh"

KEY_DIR = BASE_DIR / "keys"
PRIVATE_KEY_PATH = KEY_DIR / "private_key.pem"
PUBLIC_KEY_PATH = KEY_DIR / "public_key.pem"
DB_PATH = BASE_DIR / "cyphermesh.db"
PEER_CONFIG_PATH = BASE_DIR / "peer_config.json"

# Create base folder if it does not exist
try:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass


# --- CONFIGURATION LOGIC (Dynamic) ---

def get_local_ip():
    """Tries to obtain the local IP used to exit the Internet."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Non invia dati reali, serve solo a calcolare il routing
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def resolve_node_identity(cli_ip=None, cli_port=None):
    """
    Set final node IP and port following this priorities:
    1. CLI srguments (max priority)
    2. Env variables (Docker)
    3. JSON configuration file (persistence)
    4. Auto-detect / Default (fallback)

    Save new configuration if it has changed.
    
    Returns:
        tuple: (ip, port)
    """
    # 1. Load existing configuration
    file_config = {}
    if PEER_CONFIG_PATH.exists():
        try:
            file_config = json.loads(PEER_CONFIG_PATH.read_text())
        except Exception:
            logger.warning("Corrupted configuration file. Ignored.")

    # 2. IP resolution
    # CLI > ENV > File > Auto-detect
    final_ip = (
        cli_ip 
        or os.environ.get("CYPHER_IP")
        or file_config.get("ip")
        or get_local_ip()
    )

    # 3. Port resolution
    # CLI > ENV > File > Default (9001)
    raw_port = (
        cli_port 
        or os.environ.get("CYPHER_PORT")
        or file_config.get("port")
        or 9001
    )

    try:
        final_port = int(raw_port)
    except ValueError:
        logger.error(f"Not valid port: {raw_port}. Use default 9001.")
        final_port = 9001

    # 4. Save configuration (sticky config)
    new_config = {"ip": final_ip, "port": final_port}

    # Write only if file does not exist or if configuration has changed
    should_save = not PEER_CONFIG_PATH.exists() or file_config != new_config

    if should_save:
        try:
            with open(PEER_CONFIG_PATH, "w") as f:
                json.dump(new_config, f, indent=2)
            logger.info(f"Configuration saved in {PEER_CONFIG_PATH}.")
        except Exception as e:
            logger.warning(f"Impossible to save configuration: {e}.")

    return final_ip, final_port
