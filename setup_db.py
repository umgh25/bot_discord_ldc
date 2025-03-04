# setup_db.py

import sqlite3


def create_db():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()

    # Table pour stocker les votes
    c.execute('''CREATE TABLE IF NOT EXISTS votes (
        user_id INTEGER PRIMARY KEY,
        match_id TEXT,
        choice TEXT
    )''')

    # Table pour stocker les points des utilisateurs
    c.execute('''CREATE TABLE IF NOT EXISTS leaderboard (
        user_id INTEGER PRIMARY KEY,
        points INTEGER DEFAULT 0
    )''')

    # Table pour stocker le canal de votes
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY,
        channel_id TEXT
    )''')

    conn.commit()
    conn.close()
    print("Base de données créée avec succès.")


if __name__ == "__main__":
    create_db()
