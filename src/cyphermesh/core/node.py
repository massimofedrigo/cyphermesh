import socket
import threading
import logging
import time
from typing import List

# Importiamo il modello
from cyphermesh.models import ThreatEvent
# IMPORTANTE: Usiamo le funzioni robuste per il framing
from cyphermesh.core.protocol import send_message, receive_message
# Importiamo funzioni DB
from cyphermesh.db.events import save_event, update_reputation, get_reputation
from cyphermesh.db.peers import add_or_update_peer, remove_node # Aggiungi remove_node

class Node:
    def __init__(self, ip: str, port: int, bootstrap_mode="SEED", seed_ip=None, seed_port=None):
        self.ip = ip
        self.port = port
        self.bootstrap_mode = bootstrap_mode
        self.seed_ip = seed_ip
        self.seed_port = seed_port
        
        self.peers: List[socket.socket] = []
        self.running = False
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f"Node-{port}")

    def start(self):
        """Avvia il nodo, il server e i thread di manutenzione."""
        self.running = True
        
        # 1. Avvia Server TCP (In ascolto)
        server_thread = threading.Thread(target=self._listen_incoming, daemon=True)
        server_thread.start()
        self.logger.info(f"Nodo attivo su {self.ip}:{self.port}")

        # 2. Avvia Heartbeat Loop (Il cuore che batte!)
        hb_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        hb_thread.start()

        # 3. Bootstrap (connessione iniziale)
        if self.bootstrap_mode == "CONNECT" and self.seed_ip:
            time.sleep(1) 
            self.connect_to_peer(self.seed_ip, self.seed_port)

        # 4. Loop principale
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        for sock in self.peers:
            try:
                sock.close()
            except:
                pass
        self.logger.info("Nodo arrestato.")

    def connect_to_peer(self, target_host: str, target_port: int):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0) # Timeout per la connessione
            sock.connect((target_host, target_port))
            sock.settimeout(None) # Rimettiamo in blocking mode per il loop
            
            self.peers.append(sock)
            add_or_update_peer(target_host, target_port)
            
            threading.Thread(target=self._handle_peer_connection, args=(sock,), daemon=True).start()
            self.logger.info(f"Connesso a peer: {target_host}:{target_port}")
            
        except Exception as e:
            self.logger.error(f"Errore connessione a {target_host}:{target_port}: {e}")

    def broadcast_event(self, event: ThreatEvent):
        """Invia evento a tutti usando il protocollo sicuro."""
        payload = event.to_json()
        self.logger.info(f"Broadcasting evento {event.threat_type}...")

        # Iteriamo su una copia della lista per evitare problemi di concorrenza
        for peer in list(self.peers):
            try:
                send_message(peer, "event", payload, msg_id=event.id)
            except Exception:
                self.logger.warning("Peer disconnesso durante broadcast")
                self._remove_peer(peer)

    def _heartbeat_loop(self):
        """Invia un messaggio HELLO a tutti i peer ogni 30 secondi."""
        while self.running:
            time.sleep(30)
            if not self.peers:
                continue
                
            self.logger.debug(f"Invio Heartbeat a {len(self.peers)} nodi...")
            
            # Usiamo list(self.peers) per creare una copia sicura su cui iterare
            for peer in list(self.peers):
                try:
                    send_message(peer, "HELLO")
                except Exception:
                    self.logger.warning("Rilevato nodo morto durante Heartbeat.")
                    self._remove_peer(peer)

    def _remove_peer(self, sock):
        """Rimuove un socket dalla lista e lo chiude in modo sicuro."""
        if sock in self.peers:
            self.peers.remove(sock)
        try:
            sock.close()
        except:
            pass

    def _listen_incoming(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", self.port))
        server.listen(5)

        while self.running:
            try:
                client_sock, addr = server.accept()
                self.peers.append(client_sock)
                self.logger.info(f"Nuova connessione da {addr}")
                threading.Thread(target=self._handle_peer_connection, args=(client_sock,), daemon=True).start()
            except OSError:
                break

    def _handle_peer_connection(self, connection: socket.socket):
        """Loop di ricezione messaggi robusto."""
        addr = "Sconosciuto"
        try:
            addr = connection.getpeername()
        except:
            pass

        while self.running:
            try:
                # 1. RICEZIONE CON FRAMING (Bloccante)
                message_wrapper = receive_message(connection)
                
                if message_wrapper is None:
                    self.logger.info(f"Connessione chiusa da {addr}")
                    break 

                msg_type = message_wrapper.get("type")
                payload = message_wrapper.get("payload")

                # 2. Routing
                if msg_type == "event":
                    self._handle_threat_event(payload)
                elif msg_type == "HELLO":
                    # Non facciamo nulla, serve solo a tenere viva la connessione TCP
                    # e a non far fallire receive_message
                    self.logger.debug(f"Ricevuto Heartbeat da {addr}")
                else:
                    self.logger.warning(f"Tipo messaggio sconosciuto: {msg_type}")

            except Exception as e:
                self.logger.error(f"Errore loop ricezione {addr}: {e}")
                break
        
        self._remove_peer(connection)

    def _handle_threat_event(self, payload_dict: dict):
        try:
            event = ThreatEvent.from_dict(payload_dict)
            is_valid = event.verify()
            
            reporter = event.reporter_pubkey
            current_rep = get_reputation(reporter)

            if current_rep < -10:
                self.logger.warning(f"Evento ignorato (Reputazione bassa): {reporter[:10]}...")
                return

            save_event(event)

            if is_valid:
                self.logger.info(f"✅ VALIDATO da {reporter[:10]}... (+1 Rep)")
                update_reputation(reporter, 1)
            else:
                self.logger.warning(f"❌ FIRMA INVALIDA da {reporter[:10]}... (-3 Rep)")
                update_reputation(reporter, -3)

        except Exception as e:
            self.logger.error(f"Errore processamento evento: {e}")
            