from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
import base64
import os
from cyphermesh.config import *
from pathlib import Path
from cyphermesh.logger import logger


def ensure_keys_exist():
    if not (os.path.exists(PRIVATE_KEY_PATH) and os.path.exists(PUBLIC_KEY_PATH)):
        logger.info("[*] RSA keys not found. Generating...")
        generate_keys()
        logger.info("[✓] Keys generated in 'keys/'.")


def generate_keys():
    """Generate a couple of RSA keys and saves them in ~/.cyphermesh/keys/"""
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
    """Load private key from ~/.cyphermesh/keys/private_key.pem."""
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def load_public_key():
    """Load public key from ~/.cyphermesh/keys/public_key.pem."""
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return serialization.load_pem_public_key(f.read())


def sign_data(data: str) -> str:
    """Sign provided data using private key and return signature encoded in base64."""
    private_key = load_private_key()
    signature = private_key.sign(
        data.encode(),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()


def verify_signature(data: str, signature: str, pubkey_pem: bytes) -> bool:
    """Verify data signature using public key provided in PEM format."""
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

# --- QUESTA È LA FUNZIONE CHE MANCAVA ---
def load_own_pubkey_str() -> str:
    """
    Helper function: legge la chiave pubblica dal disco e la restituisce come stringa.
    Usata da models.py per popolare il campo 'reporter_pubkey'.
    """
    ensure_keys_exist() # Assicuriamoci che esistano prima di leggere
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return f.read().decode('utf-8')
    