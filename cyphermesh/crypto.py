from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
import base64
import os
from pathlib import Path

from cyphermesh.logger import logger

# Imposta la directory delle chiavi all'interno della cartella ~/.cyphermesh/keys
KEY_DIR = Path.home() / ".cyphermesh" / "keys"
KEY_DIR.mkdir(parents=True, exist_ok=True)  # Crea la cartella se non esiste

# Usa str(KEY_DIR) per ottenere il percorso in formato stringa
PRIVATE_KEY_PATH = os.path.join(str(KEY_DIR), "private_key.pem")
PUBLIC_KEY_PATH = os.path.join(str(KEY_DIR), "public_key.pem")


def ensure_keys_exist():
    if not (os.path.exists(PRIVATE_KEY_PATH) and os.path.exists(PUBLIC_KEY_PATH)):
        logger.info("[*] Chiavi RSA non trovate. Le sto generando...")
        generate_keys()
        logger.info("[✓] Chiavi generate in 'keys/'.")


def generate_keys():
    """Genera una coppia di chiavi RSA e le salva in ~/.cyphermesh/keys/"""
    # Se la cartella delle chiavi non esiste, la crea (già fatto sopra con mkdir)
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with open(PRIVATE_KEY_PATH, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    public_key = private_key.public_key()
    with open(PUBLIC_KEY_PATH, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))


def load_private_key():
    """Carica la chiave privata da ~/.cyphermesh/keys/private_key.pem."""
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def load_public_key():
    """Carica la chiave pubblica da ~/.cyphermesh/keys/public_key.pem."""
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return serialization.load_pem_public_key(f.read())


def sign_data(data: str) -> str:
    """Firma i dati forniti utilizzando la chiave privata e restituisce la firma codificata in base64."""
    private_key = load_private_key()
    signature = private_key.sign(
        data.encode(),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()


def verify_signature(data: str, signature: str, pubkey_pem: bytes) -> bool:
    """Verifica la firma dei dati utilizzando la chiave pubblica fornita in formato PEM."""
    try:
        pubkey = serialization.load_pem_public_key(pubkey_pem)
        pubkey.verify(
            base64.b64decode(signature),
            data.encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False
