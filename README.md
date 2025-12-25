# 🕸️ CypherMesh

## 🛡️ Zero-Conf P2P Threat Intelligence Network

**CypherMesh** is a distributed, peer-to-peer system designed to simulate the autonomous sharing and verification of Cyber Threat Intelligence (CTI). It implements a **mesh architecture** where independent nodes automatically discover each other via UDP, establish stable TCP connections, and propagate security events using a Gossip protocol.

> **⚠️ Project Status:** This project is a **Proof of Concept (PoC)** and an educational exploration of distributed systems, socket programming, and mesh networking. It is designed to demonstrate complex networking concepts in Python and is not intended for production security environments.

---

## 🏗️ Architecture & Key Technical Features

CypherMesh solves specific distributed computing challenges without relying on a central server.

### 1. Zero-Configuration Discovery (UDP)

* **Challenge:** How do nodes find each other without a hardcoded list of IPs or a central Seed server?
* **Solution:** Nodes listen on `UDP:9999`. Upon startup, a node broadcasts a `PING` packet to the local subnet (`255.255.255.255`). Any active peer replies with a `PONG` containing its TCP address, initiating a handshake.

### 2. Robust Transport (TCP Framing)

* **Challenge:** TCP is a stream protocol; packets can be fragmented or coalesced, breaking standard JSON parsers.
* **Solution:** Implemented a custom **Length-Prefixed Framing** protocol. Every message is preceded by a 4-byte Big-Endian header indicating the payload size, ensuring atomic message processing.

### 3. Gossip Protocol (Flood-Fill)

* **Challenge:** How to ensure a message reaches every node in a mesh without direct connections to everyone?
* **Solution:** When a node receives a valid threat event:
1. **Deduplication:** Checks the SQLite DB to see if the Event ID is already known.
2. **Verification:** Validates the RSA-2048 signature of the reporter.
3. **Relay:** If valid and new, it forwards the message to all connected peers (excluding the sender) to prevent loops.



---

## 🚀 Quick Start (Docker)

The project is "Docker-First". You can spin up a fully functional mesh network in seconds.

### 1. Start the Network

This command builds the image and starts a single node with its web dashboard.

```bash
git clone https://github.com/massimofedrigo/cyphermesh.git
cd cyphermesh
docker compose up -d --build

```

* **Dashboard:** [http://localhost:5050](https://www.google.com/search?q=http://localhost:5050)
* **TCP Port:** `9001`
* **UDP Port:** `9999`

### 2. Simulate a Mesh Network

To see the auto-discovery in action, run the development composition which spawns **two nodes** in the same virtual network.

```bash
docker compose -f docker-compose.dev.yml up --build

```

**What to observe:**

1. Check the logs: `docker compose logs -f`.
2. You will see `Node-1` broadcasting a PING.
3. `Node-2` will respond, and they will automatically establish a TCP connection without manual config.

---

## 🧠 Project Design & Limitations

While technically functional within a controlled environment (Docker/LAN), this architecture highlights several real-world distributed system constraints.

### 🛑 Architectural Limitations

1. **The Byzantine Generals Problem:**
In a pure P2P network without a consensus algorithm (like PoW or Raft) or a central Trust Authority, the network is vulnerable to **poisoning**. A malicious node could broadcast false threats (e.g., "Block Google DNS") which would be propagated as valid signed messages.
2. **Network Boundaries (NAT):**
The current UDP Broadcast discovery mechanism works exclusively within a **LAN** or **VPN**. It cannot traverse the public Internet without implementing complex techniques like STUN/TURN or hole-punching.
3. **Agent Performance:**
A production endpoint security agent must be invisible and low-latency. Python, while excellent for prototyping this logic, introduces significant memory and CPU overhead compared to systems languages like **Rust** or **Go**.

### 🎯 Purpose of Study

This project was built to master the following engineering concepts:

* **Asynchronous Networking:** Handling non-blocking sockets and race conditions.
* **Protocol Design:** Implementing binary framing and custom headers on top of TCP.
* **Cryptography:** Applied RSA signing and verification for data integrity.
* **Containerization:** Orchestrating a distributed environment using Docker Compose and virtual networks.

---

## 📁 Project Structure

| File | Component | Description |
| --- | --- | --- |
| `src/cyphermesh/core/node.py` | **Core Logic** | Manages the main loop, UDP listener, TCP server, and Gossip routing. |
| `src/cyphermesh/core/protocol.py` | **Transport** | Low-level socket handling (`send_message`, `receive_message`) with byte packing. |
| `src/cyphermesh/models.py` | **Data** | `ThreatEvent` dataclass with built-in serialization and RSA signature logic. |
| `src/cyphermesh/db/` | **Persistence** | SQLite wrapper with WAL mode for high-concurrency writing. |
| `src/cyphermesh/web/` | **UI** | Flask-based dashboard to visualize network state and logs. |

---

## 🧑‍💻 Author

**Massimo Fedrigo**
*Project developed as a study on P2P architectures and distributed systems.*