# 📍 CypherMesh - Roadmap di Sviluppo

### Ultimo aggiornamento: aprile 2025

## ✅ Versione 1.0.0 - Obiettivi principali

    Obiettivo: funzionalità base stabili per peer-to-peer threat sharing + installazione semplice

### 🧱 Infrastruttura di base

- ✅ Logging strutturato (logging)
- Miglior gestione errori e messaggi 
- Validazione file .json di configurazione 
- Backup semplice del database locale (magari backup distribuito nella rete P2P)
- ⚠️ Sistema di memoria basato su database
- Ricerca di discovery server nella rete locale (LAN), quindi aggiungere messaggi di tipo "ARE_YOU_DISCOVERY?" per capire se un host è un discovery

### 🔐 Sicurezza

- Firme digitali obbligatorie per tutti i messaggi
- Cifratura database (opzionale)
- Cifratura peer-to-peer (E2E o TLS)

### 🌐 Network

- Rimozione automatica dei peer inattivi 
- Aggiornamento periodico lista peer 
- Heartbeat e monitoraggio disponibilità 
- ✅ Auto-rilevamento IP locale

### 🖥 Web GUI

- Dashboard eventi in tempo reale 
- Visualizzazione reputazioni 
- Form per l’invio manuale eventi 
- Pagina di configurazione

### ⚙️ Usabilità

- ✅ Installazione tramite cyphermesh-install 
- Comandi CLI documentati 
- Script setup offline 
- ✅ README aggiornato

## 🔄 Versione 1.1.0 - Espansione rete

### 🌍 Scalabilità e interoperabilità

- Supporto multi-discovery server 
- Federazione discovery 
- Integrazione con MISP / OpenCTI 
- Esportazione eventi in STIX / CSV

## 🧪 Versioni future

### 🧠 Analisi & reputazione avanzata

- Modelli reputazionali più complessi 
- Pattern recognition tra peer 
- Machine learning sulla rete eventi

### 🕵️ Privacy & anonimato

- Comunicazione via TOR/I2P 
- Peer nascosti / modalità stealth

### 🔌 Plugin system

- Moduli estendibili per parser e notifiche 
- Script custom all’arrivo di eventi

### 🧰 Sviluppo & Test

- Copertura test ≥ 80% 
- Continuous Integration (GitHub Actions)
- Profilazione delle performance 
- Documentazione interna del codice