from flask import Flask, render_template
from cyphermesh.db import init_db, get_events, get_reputations
import logging

# Configura logger per Flask
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)

app = Flask(__name__)

# --- FIX: Inizializzazione "Lazy" o all'avvio ---
# Eseguiamo l'init del DB subito, una volta sola, quando il modulo viene caricato.
try:
    init_db()
    print(" [WEB] Database collegato e inizializzato.")
except Exception as e:
    print(f" [WEB] Errore init DB: {e}")

@app.route("/")
def index():
    # Qui leggiamo solo i dati
    events = get_events()
    reps = get_reputations()
    return render_template("index.html", events=events, reps=reps)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
    