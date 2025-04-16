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

| File                  | Descrizione                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| `core.py`             | Punto di partenza per avviare un peer                                      |
| `peer_network.py`     | Logica di rete tra peer: invio, ricezione, gestione connessioni            |
| `discovery_server.py` | Server centrale per registrare i peer (opzionale ma consigliato)         |
| `discovery_client.py` | Client per registrazione e aggiornamento dal discovery server            |
| `threat_handler.py`   | Verifica eventi firmati, aggiorna reputazione                             |
| `db.py`               | Gestione del database SQLite (eventi e reputazione)                        |
| `crypto.py`           | Generazione chiavi RSA, firma e verifica digitale                          |
| `protocol.py`         | Costruzione e parsing dei messaggi JSON                                    |
| `event.py`            | Struttura dati degli eventi di minaccia                                    |
| `test_network.py`     | Esegue una simulazione completa: discovery + peer + evento                 |

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

- `cyphermesh-install`
- `cyphermesh-peer`
- `cyphermesh-discovery-server`

## ⚙️ Utilizzo

### 🔧 Avvio della procedura guidata
Per configurare l'applicazione (come discovery server o peer):
```bash
cyphermesh-install
```

### 📡 Avvio del Discovery Server
Dopo la configurazione, per avviare il discovery server:
```bash
cyphermesh-discovery_server-server
```
Assicurati che il file `discovery_server_config.json` sia presente nella directory corrente.

### 🤝 Avvio di un Peer
Dopo aver configurato il peer con il relativo file `peer_config.json`, puoi avviarlo con:
```bash
cyphermesh-peer
```
Il peer si registrerà automaticamente al discovery server e inizierà a comunicare con la rete.

## 🛠️ Requisiti

- Python 3.8+
- Criptography (`pip install criptography`)

## 🧑‍Autore

Progetto ideato e realizzato con ❤️ per studiare reti P2P, sicurezza e reputazione distribuita.