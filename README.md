# 🕸️ CypherMesh

## 🛡️ Your Zero-Conf P2P Threat Intelligence Network

**CypherMesh** is a decentralized peer-to-peer network designed for the sharing and verification of Cyber Threat Intelligence (CTI). It uses a mesh architecture where each node acts autonomously to discover peers, receive, sign, verify, and propagate security events.

Unlike traditional centralized systems, CypherMesh requires **no configuration**: just launch a node, and it will automatically discover other peers on the local network using UDP broadcasts.

---

## 📚 Key Features

* **Zero-Configuration**: Nodes automatically find each other via **UDP Discovery** (LAN).
* **Gossip Protocol**: Events are propagated across the network (Mesh) like a virus, ensuring total coverage even without direct connections to everyone.
* **Pure P2P**: No central server, no "Seed" nodes. All nodes are equal.
* **Docker-First**: Launch a fully functional node + dashboard with a single command.
* **Security**: RSA-2048 signatures on all events and automatic Reputation system.
* **Persistence**: SQLite database with WAL (Write-Ahead Logging) mode.
* **Web Dashboard**: Real-time visualization of attacks, peer status, and network logs.

---

## 🚀 Quick Start (Production)

This is the standard way to run a node for end-users. It starts **1 Node** and **1 Dashboard**.

### 1. Start the Node

```bash
# 1. Clone the repository
git clone https://github.com/massimofedrigo/cyphermesh.git
cd cyphermesh

# 2. Start everything in the background
docker compose up -d --build

```

Your system is now active:

* **Web Dashboard:** [http://localhost:5050](https://www.google.com/search?q=http://localhost:5050)
* **P2P TCP Port:** `9001` (Data exchange)
* **P2P UDP Port:** `9999` (Discovery)
* **Data:** Persisted in the `cyphermesh_data` Docker volume.

*Note: If you run multiple nodes on the same LAN, they will automatically connect to each other.*

---

## 🧪 Development Environment (Mesh Simulation)

Do you want to simulate a mesh network locally? The development compose file starts **two nodes** that will automatically discover each other.

```bash
# Starts Node-1 (9001) and Node-2 (9002) in the same virtual network
docker compose -f docker-compose.dev.yml up --build

```

**What happens next?**

1. **Node-1** starts and shouts "PING" via UDP.
2. **Node-2** hears it, replies "PONG", and initiates a TCP connection.
3. **Heartbeat** keeps the connection alive.

You can monitor the dashboard at [http://localhost:5050](https://www.google.com/search?q=http://localhost:5050).

---

## ⚙️ Power Users: Manual Execution

If you want to launch nodes manually using `docker run` (e.g., on different machines):

**Important:** You must map both the TCP port (default 9001) and the UDP port (default 9999).

```bash
# Launch a node
docker run -d \
  --name my-node \
  -p 9001:9001 \
  -p 9999:9999/udp \
  -v my_data:/root/.cyphermesh \
  cyphermesh-node:latest

```

*Since the node uses Zero-Conf, no arguments are needed. It will listen on 0.0.0.0:9001 by default.*

---

## 📁 Project Structure

| File | Purpose |
| --- | --- |
| `src/cyphermesh/core/node.py` | **The Brain**: Handles UDP Discovery, TCP Connections, and Gossip Logic. |
| `src/cyphermesh/models.py` | **Data Models**: `ThreatEvent` dataclass with self-validation methods. |
| `src/cyphermesh/core/protocol.py` | **Transport**: Length-prefixed framing for robust TCP streaming. |
| `docker-compose.yml` | **Prod Config** (Single Node). |
| `docker-compose.dev.yml` | **Dev Config** (Simulated Network of 2 nodes). |

---

## 🧠 Protocol & Mechanism

### 1. Discovery (UDP Broadcast)

* **Port:** 9999 UDP.
* **PING:** When a node starts (or feels lonely), it broadcasts a `PING` message to `255.255.255.255`.
* **PONG:** Any node receiving a PING replies with a `PONG` containing its TCP port.
* **Handshake:** The nodes establish a stable TCP connection.

### 2. Transport (TCP Framing)

Messages are exchanged via TCP using a **Length-Prefixed** framing protocol (4-byte header indicating payload size) to prevent packet fragmentation issues.

### 3. Gossip Protocol (Event Propagation)

When a node detects a threat (or receives one):

1. **Deduplication:** Checks DB. If the event ID exists, it stops (prevents loops).
2. **Verification:** Verifies RSA Signature and Sender Reputation.
3. **Storage:** Saves valid events to the local DB.
4. **Relay:** Forwards the event to **all** connected peers (except the sender).

### 4. Reputation System

* ✅ **Valid Signature**: Event saved, Reputation +1.
* ❌ **Invalid Signature**: Event discarded, Reputation -3.
* 🚫 **Ban**: If Reputation drops below -10, the peer is ignored.

---

## 🔮 Future Roadmap

* [ ] **Web Input**: Form to generate threat events directly from the Dashboard.
* [ ] **REST API**: Integration with external SIEMs (e.g., push events via API).
* [ ] **E2E Encryption**: TLS tunneling between nodes for privacy.
* [ ] **NAT Traversal**: UPnP or STUN support for over-the-internet discovery.

---

## 🧑‍💻 Author

Project designed to study P2P networks, mesh algorithms, security, and distributed reputation systems.