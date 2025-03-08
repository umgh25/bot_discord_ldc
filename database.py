import sqlite3
import os

# Définir le chemin de la base de données
DB_PATH = os.path.join(os.getenv('RENDER_DB_PATH', '.'), 'bot_database.db')

def create_db():
    # Vérifie si la base de données existe déjà
    if os.path.exists(DB_PATH):
        return  # Si elle existe, ne rien faire
        
    # Créer la base de données seulement si elle n'existe pas
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Créer les tables
    c.execute('''CREATE TABLE IF NOT EXISTS votes (
        user_id INTEGER PRIMARY KEY,
        match_id TEXT,
        choice TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS leaderboard (
        user_id INTEGER PRIMARY KEY,
        points INTEGER DEFAULT 0
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY,
        channel_id TEXT
    )''')
    
    conn.commit()
    conn.close()

def save_vote(user_id, match_id, choice):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO votes (user_id, match_id, choice) VALUES (?, ?, ?)''',
              (user_id, match_id, choice))
    conn.commit()
    conn.close()

# Fonction pour récupérer les votes d'un match


def get_votes(match_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        '''SELECT user_id, choice FROM votes WHERE match_id = ?''', (match_id,))
    results = c.fetchall()
    conn.close()
    return results

# Fonction pour ajouter des points


def add_points(user_id, points):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO leaderboard (user_id, points) 
                 VALUES (?, ?) 
                 ON CONFLICT(user_id) 
                 DO UPDATE SET points = points + ?''',
              (user_id, points, points))
    conn.commit()
    conn.close()

# Fonction pour récupérer le classement


def get_leaderboard():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT user_id, points FROM leaderboard ORDER BY points DESC''')
    results = c.fetchall()
    conn.close()
    return results

# Fonction pour enregistrer le canal de votes


def set_channel(channel_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        '''INSERT OR REPLACE INTO settings (id, channel_id) VALUES (1, ?)''', (channel_id,))
    conn.commit()
    conn.close()

# Fonction pour récupérer l'ID du canal de votes


def get_channel():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT channel_id FROM settings WHERE id = 1''')
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


# Création de la base de données au lancement
create_db()
