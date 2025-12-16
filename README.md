# 🕸️ CypherMesh

## 🛡️ La tua P2P Threat Intelligence Network

Una rete peer-to-peer decentralizzata per la condivisione e verifica di segnalazioni di minacce informatiche. Ogni nodo può ricevere, firmare, condividere e verificare eventi di sicurezza, aggiornando dinamicamente la reputazione dei peer.

---

## 📚 Descrizione

Questo progetto crea una rete P2P in cui ogni peer:
- Si registra presso un discovery server centrale (facoltativo)
- Comunica con altri peer tramite messaggi TCP
- Invia e riceve eventi di minacce firmati digitalmente
- Gestisce un database locale per eventi e reputazione
- Verifica le firme e regola il comportamento dei peer

---

## 🚀 Come funziona

1. **Registrazione**: il peer si registra presso il discovery server.
2. **Scoperta**: il peer invia un `peer_hello` per ottenere la lista degli altri nodi.
3. **Verifica**: alla ricezione di un messaggio `event`, verifica la firma con la chiave pubblica del mittente.
4. **Reputazione**: aggiorna la reputazione del mittente in base alla validità della firma.

---

## 🧠 Tipi di Messaggi Supportati

| Tipo         | Payload                               | Scopo                                                   |
|--------------|----------------------------------------|----------------------------------------------------------|
| `peer_hello` | `{ "port": int }`                      | Annuncia la presenza di un nuovo peer                   |
| `peer_list`  | `{ "peers": ["IP:PORT", ...] }`        | Invia la lista dei peer conosciuti                      |
| `peer_notify`| `{ "new_peer": "IP:PORT" }`            | Notifica un nuovo peer alla rete                        |
| `event`      | `{ id, type, severity, ..., signature }` | Invia un evento firmato                                 |

---

## 📁 Struttura dei File

| File/Cartella                | Descrizione                                                                 |
|------------------------------|-----------------------------------------------------------------------------|
| `cyphermesh/crypto.py`       | Generazione delle chiavi RSA, firma e verifica digitale                     |
| `cyphermesh/event.py`        | Creazione e identificazione univoca degli eventi di sicurezza               |
| `cyphermesh/protocol.py`     | Costruzione e parsing dei messaggi JSON scambiati tra peer                  |
| `cyphermesh/db/peers.py`     | Gestione della rubrica dei peer (SQLite) e bootstrap iniziale               |
| `cyphermesh/db/events.py`    | Persistenza di eventi e reputazioni nel database SQLite                     |
| `cyphermesh/peer/peer.py`    | Server TCP del peer, gestione HELLO/HELLO_ACK e aggiornamento dei peer      |
| `cyphermesh/peer/threat_handler.py` | Verifica delle firme degli eventi e aggiornamento reputazioni        |
| `cyphermesh/web/app.py`      | Piccola dashboard Flask per visualizzare eventi e reputazioni               |
| `cli/run_peer.py`            | CLI per avviare un peer locale                                              |
| `cli/add_peer.py`            | CLI per aggiungere manualmente un peer al database locale                   |
| `cli/reset.py`               | CLI per ripulire configurazione e database                                  |

---

## 🔐 Sicurezza

- **Firma digitale**: ogni evento viene firmato dal mittente con una chiave RSA privata
- **Verifica**: la rete verifica la firma con la chiave pubblica del mittente
- **Reputazione**: peer con reputazione troppo bassa vengono ignorati

| Azione                 | Effetto |
|------------------------|---------|
| Firma valida           | `+1`    |
| Firma non valida       | `-3`    |
| Reputazione < -10      | Ignorato |

---

## 🚀 Installazione

### 1. **Clona il repository**
```bash
git clone https://github.com/tuo-utente/cyphermesh.git
cd cyphermesh
```

### 2. (Opzionale) Crea ambiente virtuale
```bash
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate
```

### 3. Installa il pacchetto localmente
```bash
pip install .
```
Questo comando installerà `cyphermesh` e renderà disponibili i seguenti comandi CLI:

- `cyphermesh-run-peer`: avvia un peer locale
- `cyphermesh-add-peer`: aggiunge un peer alla rubrica locale (es. dopo il bootstrap)
- `cyphermesh-reset`: pulisce configurazione e database in `~/.cyphermesh`

## ⚙️ Utilizzo

### 🤝 Avvio di un Peer
Per avviare un peer locale (con salvataggio della configurazione in `~/.cyphermesh/peer_config.json` se mancante):
```bash
cyphermesh-run-peer --ip 127.0.0.1 --port 9001
```
Il comando gestisce automaticamente la generazione delle chiavi RSA e il bootstrap verso eventuali peer già presenti nel database.

### ➕ Aggiungere manualmente un peer conosciuto
Se conosci l'indirizzo di un altro nodo, puoi inserirlo nella rubrica locale con:
```bash
cyphermesh-add-peer 10.0.0.42:9001
```

### ♻️ Pulizia rapida
Per eliminare configurazione e database locale (utile durante i test):
```bash
cyphermesh-reset --all
```

## 🛠️ Requisiti

- Python 3.8+
- cryptography (`pip install cryptography`)

## 🧑‍Autore

Progetto ideato e realizzato con ❤️ per studiare reti P2P, sicurezza e reputazione distribuita.