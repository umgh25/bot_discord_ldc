from flask import Flask, jsonify
from threading import Thread
from database import supabase  # Importez le client Supabase

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

@app.route('/votes')
def get_votes():
    try:
        result = supabase.table("votes").select("*").execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)})

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

