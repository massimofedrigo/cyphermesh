from flask import Flask, render_template
from cyphermesh.web.db import init_db, get_events, get_reputations

app = Flask(__name__)


@app.route("/")
def index():
    # 🔧 Inizializza il DB
    init_db()
    events = get_events()
    reps = get_reputations()
    return render_template("index.html", events=events, reps=reps)


if __name__ == "__main__":
    app.run(debug=True)
