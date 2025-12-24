# 🕸️ CypherMesh

## 🛡️ Your P2P Threat Intelligence Network

**CypherMesh** is a decentralized peer-to-peer network designed for the sharing and verification of Cyber Threat Intelligence (CTI). Each node acts autonomously to receive, sign, share, and verify security events, dynamically updating peer reputation based on the cryptographic validity of their reports.

---

## 📚 Key Features

* **Pure P2P**: No central server. The network survives as long as nodes are active.
* **Docker-First**: Launch a node and dashboard with a single command.
* **Security**: RSA-2048 signatures on all events and automatic Reputation system.
* **Persistence**: SQLite database with WAL (Write-Ahead Logging) mode.
* **Web Dashboard**: Real-time visualization of attacks and peer status.

---

## 🚀 Quick Start (Production)

This is the standard way to run a node for end-users. It starts **1 Node** and **1 Dashboard**.

### 1. Start the Node

```bash
# 1. Clone the repository
git clone https://github.com/massimofedrigo/cyphermesh.git
cd cyphermesh

# 2. Start everything in the background
docker compose up -d

```

Your system is now active:

* **Web Dashboard:** [http://localhost:5050](https://www.google.com/search?q=http://localhost:5050)
* **P2P Port:** `9001` (TCP) - *Make sure to forward this port if you are behind NAT.*
* **Data:** Persisted in the `cyphermesh_data` Docker volume.

### 2. Join the Network

By default, the node starts in `SEED` mode (passive/waiting). To connect to another user's node (e.g., IP `192.168.1.50` on port `9001`):

```bash
docker exec -it cyphermesh-node cyphermesh-add-peer 192.168.1.50:9001

```

---

## 🧪 Development Environment (Network Simulation)

Do you want to simulate a local network with two nodes automatically connected? Use the development compose file.

```bash
# Starts a Seed (9001) and a Peer (9002) connected to each other
docker compose -f docker-compose.dev.yml up --build

```

* **Seed Dashboard:** [http://localhost:5050](https://www.google.com/search?q=http://localhost:5050)
* You will see the peer appear automatically in the seed's list.

---

## ⚙️ Power Users: Manual Multi-Node Execution

If you need to launch extra nodes manually without using Compose, you can use `docker run`.
**Important Rule:** The External Port must match the Internal Port via the environment variable.

```bash
# Launch a node on port 9005
docker run -d \
  --name extra-node \
  -p 9005:9005 \
  -e CYPHER_PORT=9005 \
  -v extra_data:/root/.cyphermesh \
  cyphermesh-node:latest \
  --bootstrap CONNECT --seed-ip 172.17.0.1

```

---

## 📁 Project Structure

| File | Purpose |
| --- | --- |
| `src/` | Python source code. |
| `docker-compose.yml` | **Production Config** (Single Node + Dashboard). |
| `docker-compose.dev.yml` | **Dev Config** (Simulated Network: Seed + Peer). |
| `docker-entrypoint.sh` | Container startup script (Auto-configures ports). |
| `Dockerfile` | Docker image definition. |

---

## 🧠 Protocol & Mechanism

Messages are exchanged via TCP with a 4-byte header (payload length).

1. **Bootstrap**: On startup, the node loads config. If set to `CONNECT` mode, it contacts a Seed.
2. **Heartbeat**: Periodically sends `HELLO` messages to known peers to maintain the connection.
3. **Threat Sharing**: When a threat is detected, the node broadcasts a signed `event` packet.
4. **Verification**:
* ✅ **Valid Signature**: Event saved, Reputation +1.
* ❌ **Invalid Signature**: Event discarded, Reputation -3.
* 🚫 **Ban**: If Reputation drops below -10, the peer is ignored.



---

## 🔮 Future Roadmap

* [ ] **Auto Discovery**: UDP Broadcast for LAN peer discovery.
* [ ] **Gossip Protocol**: Epidemic event propagation.
* [ ] **REST API**: Integration with external SIEMs.
* [ ] **E2E Encryption**: TLS tunneling between nodes.

---

## 🧑‍💻 Author

Project designed to study P2P networks, security, and distributed reputation systems.