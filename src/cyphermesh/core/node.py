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
from cyphermesh.db.peers import add_or_update_peer, remove_node
# Import necessario per _event_exists
from cyphermesh.db.core import db_cursor

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
        """Invia evento a tutti (API Pubblica / Origine locale)."""
        payload = event.to_json()
        self.logger.info(f"Broadcasting evento locale {event.threat_type}...")

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
                    # MODIFICATO: Passiamo la connessione per sapere chi è il mittente (per il gossip)
                    self._handle_threat_event(payload, sender_socket=connection)
                elif msg_type == "HELLO":
                    self.logger.debug(f"Ricevuto Heartbeat da {addr}")
                else:
                    self.logger.warning(f"Tipo messaggio sconosciuto: {msg_type}")

            except Exception as e:
                self.logger.error(f"Errore loop ricezione {addr}: {e}")
                break
        
        self._remove_peer(connection)

    def _handle_threat_event(self, payload_dict: dict, sender_socket: socket.socket = None):
        """
        Logica centrale: Riceve -> Deduplica -> Valida -> Salva -> Propaga (Gossip).
        """
        try:
            event = ThreatEvent.from_dict(payload_dict)
            
            # A. DEDUPLICAZIONE: Lo conosciamo già?
            # Se è già nel DB, fermiamo la propagazione per evitare loop infiniti.
            if self._event_exists(event.id):
                # self.logger.debug(f"Evento {event.id[:8]} già presente. Ignorato.")
                return

            # B. Validazione Crittografica
            is_valid = event.verify()
            
            reporter = event.reporter_pubkey
            
            # Controllo reputazione minima per evitare spam
            if get_reputation(reporter) < -10:
                self.logger.warning(f"Evento ignorato (Reputazione bassa): {reporter[:10]}...")
                return

            # C. Salvataggio
            save_event(event)

            # D. Aggiornamento Reputazione e GOSSIP
            if is_valid:
                self.logger.info(f"✅ VALIDATO da {reporter[:10]}... (+1 Rep)")
                update_reputation(reporter, 1)
                
                # RE-BROADCASTING (Gossip Protocol)
                # Se l'evento è valido e nuovo, dillo a tutti gli altri amici!
                self.logger.info(f"📡 Propagazione (Gossip) evento {event.id[:8]}...")
                self._gossip_event(event, exclude_sock=sender_socket)
            else:
                self.logger.warning(f"❌ FIRMA INVALIDA da {reporter[:10]}... (-3 Rep)")
                update_reputation(reporter, -3)
                # Nota: Non propaghiamo eventi invalidi!

        except Exception as e:
            self.logger.error(f"Errore processamento evento: {e}")

    # --- NUOVI METODI HELPER PER IL GOSSIP ---

    def _event_exists(self, event_id: str) -> bool:
        """Controlla velocemente se un evento è già nel DB."""
        with db_cursor() as cur:
            cur.execute("SELECT 1 FROM events WHERE id = ?", (event_id,))
            return cur.fetchone() is not None

    def _gossip_event(self, event: ThreatEvent, exclude_sock: socket.socket = None):
        """Invia l'evento a tutti i peer TRANNE quello da cui l'abbiamo ricevuto."""
        payload = event.to_json()
        
        for peer in list(self.peers):
            if peer == exclude_sock:
                continue # Non rispedire al mittente!
            
            try:
                send_message(peer, "event", payload, msg_id=event.id)
            except Exception:
                pass
            