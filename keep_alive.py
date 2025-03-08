import sqlite3
from flask import Flask, jsonify
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

# Route pour voir les votes
@app.route('/votes')
def get_votes():
    conn = sqlite3.connect("bot_database.db")  # Assure-toi du bon chemin
    c = conn.cursor()
    c.execute("SELECT * FROM votes")
    data = c.fetchall()
    conn.close()
    
    # Formater les données en JSON
    votes_list = [{"user_id": row[0], "match_id": row[1], "choice": row[2]} for row in data]
    return jsonify(votes_list)

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
