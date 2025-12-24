import socket
import threading
import logging
import time
import json
import uuid
from typing import List

# Importiamo il modello
from cyphermesh.models import ThreatEvent
# Importiamo le funzioni robuste per il framing TCP
from cyphermesh.core.protocol import send_message, receive_message
# Importiamo funzioni DB
from cyphermesh.db.events import save_event, update_reputation, get_reputation
from cyphermesh.db.peers import add_or_update_peer, remove_node
from cyphermesh.db.core import db_cursor

# Costante per la Discovery sulla rete locale
UDP_BROADCAST_PORT = 9999

class Node:
    def __init__(self, ip: str, port: int):
        """
        Inizializza un nodo P2P Zero-Conf.
        Non servono più seed_ip o bootstrap_mode: il nodo si autoconfigura.
        """
        self.ip = ip
        self.port = port
        
        # ID univoco per evitare di rispondere ai propri messaggi UDP
        self.node_id = str(uuid.uuid4())
        
        self.peers: List[socket.socket] = []
        self.running = False
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f"Node-{port}")

    def start(self):
        """Avvia il nodo, i server TCP/UDP e i thread di manutenzione."""
        self.running = True
        
        # 1. Avvia Server TCP (In ascolto per connessioni stabili)
        server_thread = threading.Thread(target=self._listen_incoming, daemon=True)
        server_thread.start()
        self.logger.info(f"Nodo attivo su TCP {self.ip}:{self.port}")

        # 2. Avvia UDP Discovery Listener (Ascolta "Chi c'è?")
        udp_thread = threading.Thread(target=self._udp_listener_loop, daemon=True)
        udp_thread.start()

        # 3. Avvia Heartbeat Loop (Mantiene vive le connessioni TCP)
        hb_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        hb_thread.start()

        # 4. Broadcast Iniziale: "SONO QUI!"
        # Aspettiamo un attimo che il listener sia su
        time.sleep(2)
        self._send_udp_broadcast(msg_type="PING")

        # 5. Loop principale (mantiene vivo il processo)
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
        """Tenta di stabilire una connessione TCP con un peer scoperto."""
        # Evitiamo di connetterci a noi stessi (Localhost)
        if target_host == "127.0.0.1" and target_port == self.port:
            return
        
        # Evitiamo di connetterci al nostro stesso IP pubblico/LAN
        if target_host == self.ip and target_port == self.port:
            return

        # Evitiamo duplicati (controllo semplice basato su socket esistenti)
        for p in self.peers:
            try:
                if p.getpeername() == (target_host, target_port):
                    return # Già connesso
            except:
                pass

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0) # Timeout breve per la connessione
            sock.connect((target_host, target_port))
            sock.settimeout(None) # Rimettiamo in blocking mode per il loop dati
            
            self.peers.append(sock)
            add_or_update_peer(target_host, target_port)
            
            # Avvia il gestore dedicato per questo peer
            threading.Thread(target=self._handle_peer_connection, args=(sock,), daemon=True).start()
            self.logger.info(f"🔗 Connesso a peer: {target_host}:{target_port}")
            
        except Exception as e:
            # Silenziamo errori comuni durante la discovery per pulizia log
            pass

    def broadcast_event(self, event: ThreatEvent):
        """API Pubblica: Invia un evento generato localmente a tutti i peer."""
        payload = event.to_json()
        self.logger.info(f"Broadcasting evento locale {event.threat_type}...")
        
        for peer in list(self.peers):
            try:
                send_message(peer, "event", payload, msg_id=event.id)
            except Exception:
                self._remove_peer(peer)

    # --- UDP DISCOVERY SECTION ---

    def _udp_listener_loop(self):
        """Ascolta messaggi broadcast UDP sulla porta 9999."""
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            # Su alcuni OS (Linux/Mac) serve SO_REUSEPORT per far ascoltare più processi sulla stessa porta
            udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass 

        udp_sock.bind(('', UDP_BROADCAST_PORT))
        self.logger.info(f"UDP Discovery in ascolto su porta {UDP_BROADCAST_PORT}")

        while self.running:
            try:
                data, addr = udp_sock.recvfrom(1024)
                message = json.loads(data.decode())
                
                # Ignora i propri messaggi (echo)
                if message.get('node_id') == self.node_id:
                    continue

                msg_type = message.get('type')
                remote_tcp_port = message.get('tcp_port')
                remote_ip = addr[0] # L'IP da cui arriva il pacchetto UDP

                if msg_type == "PING":
                    self.logger.debug(f"🔍 Ricevuto PING da {remote_ip}. Rispondo PONG.")
                    # 1. Rispondi "Ci sono io!"
                    self._send_udp_broadcast(msg_type="PONG")
                    # 2. Prova a connetterti a lui (bidirezionale aggressivo)
                    self.connect_to_peer(remote_ip, remote_tcp_port)

                elif msg_type == "PONG":
                    self.logger.debug(f"💡 Ricevuto PONG da {remote_ip}. Mi connetto.")
                    self.connect_to_peer(remote_ip, remote_tcp_port)

            except Exception as e:
                self.logger.error(f"Errore UDP Listener: {e}")

    def _send_udp_broadcast(self, msg_type="PING"):
        """Invia un pacchetto JSON in broadcast sulla rete locale."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        message = {
            "type": msg_type,
            "node_id": self.node_id,
            "tcp_port": self.port # Diciamo agli altri su quale porta TCP ascoltiamo
        }
        
        try:
            sock.sendto(json.dumps(message).encode(), ('<broadcast>', UDP_BROADCAST_PORT))
        except Exception as e:
            self.logger.error(f"Errore invio UDP Broadcast: {e}")
        finally:
            sock.close()

    # --- END UDP SECTION ---

    def _heartbeat_loop(self):
        """Invia messaggi HELLO o PING UDP periodicamente."""
        while self.running:
            time.sleep(30)
            
            # Se siamo soli, proviamo a urlare di nuovo sulla rete UDP
            if not self.peers:
                self._send_udp_broadcast(msg_type="PING")
                continue
            
            # Altrimenti manteniamo vive le connessioni TCP esistenti
            for peer in list(self.peers):
                try:
                    send_message(peer, "HELLO")
                except Exception:
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
        """Server TCP principale."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", self.port))
        server.listen(5)

        while self.running:
            try:
                client_sock, addr = server.accept()
                self.peers.append(client_sock)
                # self.logger.info(f"Nuova connessione TCP da {addr}")
                threading.Thread(target=self._handle_peer_connection, args=(client_sock,), daemon=True).start()
            except OSError:
                break

    def _handle_peer_connection(self, connection: socket.socket):
        """Gestisce il flusso dati TCP da un singolo peer."""
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
                    break 

                msg_type = message_wrapper.get("type")
                payload = message_wrapper.get("payload")

                # 2. Routing messaggi
                if msg_type == "event":
                    # Passiamo il socket per evitare l'eco nel gossip
                    self._handle_threat_event(payload, sender_socket=connection)
                elif msg_type == "HELLO":
                    pass # Keep-alive, non serve logica
            except Exception:
                break
        
        self._remove_peer(connection)

    def _handle_threat_event(self, payload_dict: dict, sender_socket: socket.socket = None):
        """
        Logica centrale: Deduplica -> Valida -> Salva -> Gossip.
        """
        try:
            event = ThreatEvent.from_dict(payload_dict)
            
            # A. DEDUPLICAZIONE: Lo conosciamo già?
            if self._event_exists(event.id):
                return

            # B. Controllo Reputazione mittente (Anti-Spam)
            if get_reputation(event.reporter_pubkey) < -10:
                return

            # C. Validazione Crittografica
            is_valid = event.verify()
            
            # D. Salvataggio
            save_event(event)

            # E. Aggiornamento Reputazione e GOSSIP
            if is_valid:
                self.logger.info(f"✅ VALIDATO e PROPAGATO evento da {event.reporter_pubkey[:10]}...")
                update_reputation(event.reporter_pubkey, 1)
                # GOSSIP: Inoltra agli altri
                self._gossip_event(event, exclude_sock=sender_socket)
            else:
                self.logger.warning(f"❌ FIRMA INVALIDA da {event.reporter_pubkey[:10]}...")
                update_reputation(event.reporter_pubkey, -3)

        except Exception as e:
            self.logger.error(f"Errore processamento evento: {e}")

    def _event_exists(self, event_id: str) -> bool:
        """Controlla nel DB se un evento esiste già."""
        with db_cursor() as cur:
            cur.execute("SELECT 1 FROM events WHERE id = ?", (event_id,))
            return cur.fetchone() is not None

    def _gossip_event(self, event: ThreatEvent, exclude_sock: socket.socket = None):
        """
        Invia l'evento a tutti i peer TRANNE quello da cui l'abbiamo ricevuto.
        """
        payload = event.to_json()
        for peer in list(self.peers):
            if peer == exclude_sock: continue
            try:
                send_message(peer, "event", payload, msg_id=event.id)
            except Exception:
                pass
            