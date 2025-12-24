from dataclasses import dataclass, asdict
from typing import Optional
import json
import time
import hashlib
# Importiamo le primitive crypto esistenti
from cyphermesh.crypto import sign_data, verify_signature, load_own_pubkey_str

@dataclass
class ThreatEvent:
    id: str
    source_ip: str
    threat_type: str
    severity: str
    timestamp: str
    reporter_pubkey: str
    signature: Optional[str] = None
    valid_signature: bool = False

    def to_json(self) -> dict:
        """Restituisce il dict pulito (senza campi interni python-only)."""
        d = asdict(self)
        # Rimuoviamo il flag di validità locale, non si trasmette in rete
        d.pop('valid_signature', None)
        return d

    def get_canonical_payload(self) -> str:
        """
        Crea la stringa JSON canonica per la firma (senza il campo signature).
        """
        data = self.to_json()
        data.pop('signature', None) # La firma non firma se stessa
        return json.dumps(data, sort_keys=True)

    def sign(self):
        """Calcola e applica la firma all'oggetto corrente."""
        payload = self.get_canonical_payload()
        self.signature = sign_data(payload)
    
    def verify(self) -> bool:
        """Verifica la firma dell'oggetto corrente."""
        if not self.signature or not self.reporter_pubkey:
            return False
        
        payload = self.get_canonical_payload()
        # Usa la funzione crypto esistente convertendo la key in bytes
        try:
            is_valid = verify_signature(
                data=payload, 
                signature=self.signature, 
                pubkey_pem=self.reporter_pubkey.encode()
            )
            self.valid_signature = is_valid
            return is_valid
        except Exception:
            return False

    @classmethod
    def create_new(cls, source_ip: str, threat_type: str, severity: str):
        """Factory method per creare un nuovo evento da zero (uso locale)."""
        # Carica la chiave pubblica dell'utente
        pub_key = load_own_pubkey_str()
        
        # Struttura temporanea per calcolare l'ID
        temp_data = {
            "source_ip": source_ip,
            "threat_type": threat_type,
            "severity": severity,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), # O ISO format
            "reporter_pubkey": pub_key
        }
        # Calcolo ID deterministico (hash del contenuto base)
        temp_json = json.dumps(temp_data, sort_keys=True)
        event_id = hashlib.sha256(temp_json.encode()).hexdigest()

        instance = cls(
            id=event_id,
            **temp_data
        )
        # Firma automatica alla creazione
        instance.sign()
        return instance

    @classmethod
    def from_dict(cls, data: dict):
        """Deserializza da JSON ricevuto via rete."""
        # Filtra chiavi sconosciute per evitare crash
        valid_keys = cls.__annotations__.keys()
        clean_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**clean_data)
    