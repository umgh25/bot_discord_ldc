import sqlite3
from sqlite3 import Error
import os

def create_connection():
    try:
        # Utiliser le chemin persistant sur Render
        db_path = '/data/bot_database.db' if os.path.exists('/data') else 'bot_database.db'
        conn = sqlite3.connect(db_path)
        return conn
    except Error as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return None

def init_database():
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            
            # Création de la table des votes
            c.execute('''
                CREATE TABLE IF NOT EXISTS votes (
                    user_id TEXT,
                    match_id TEXT,
                    team TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, match_id)
                )
            ''')
            
            # Création de la table des points
            c.execute('''
                CREATE TABLE IF NOT EXISTS points (
                    user_id TEXT,
                    match_id TEXT,
                    points INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, match_id)
                )
            ''')
            
            conn.commit()
            print("Base de données initialisée avec succès")
        except Error as e:
            print(f"Erreur lors de la création des tables : {e}")
        finally:
            conn.close()

def save_vote(user_id, match_id, team):
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO votes (user_id, match_id, team)
                VALUES (?, ?, ?)
            ''', (str(user_id), str(match_id), team))
            conn.commit()
            return True
        except Error as e:
            print(f"Erreur lors de l'enregistrement du vote : {e}")
            return False
        finally:
            conn.close()

def get_user_votes(user_id):
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute('SELECT match_id, team FROM votes WHERE user_id = ?', (str(user_id),))
            votes = dict(c.fetchall())
            return votes
        except Error as e:
            print(f"Erreur lors de la récupération des votes : {e}")
            return {}
        finally:
            conn.close()

def get_all_votes():
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute('SELECT user_id, match_id, team FROM votes')
            votes = {}
            for user_id, match_id, team in c.fetchall():
                if user_id not in votes:
                    votes[user_id] = {}
                votes[user_id][match_id] = team
            return votes
        except Error as e:
            print(f"Erreur lors de la récupération de tous les votes : {e}")
            return {}
        finally:
            conn.close()

def save_points(user_id, match_id, points):
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO points (user_id, match_id, points)
                VALUES (?, ?, ?)
            ''', (str(user_id), str(match_id), points))
            conn.commit()
            return True
        except Error as e:
            print(f"Erreur lors de l'enregistrement des points : {e}")
            return False
        finally:
            conn.close()

def get_user_points(user_id):
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute('SELECT SUM(points) FROM points WHERE user_id = ?', (str(user_id),))
            total = c.fetchone()[0]
            return total if total is not None else 0
        except Error as e:
            print(f"Erreur lors de la récupération des points : {e}")
            return 0
        finally:
            conn.close()

def get_all_points():
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute('''
                SELECT user_id, SUM(points) as total
                FROM points
                GROUP BY user_id
                ORDER BY total DESC
            ''')
            return dict(c.fetchall())
        except Error as e:
            print(f"Erreur lors de la récupération de tous les points : {e}")
            return {}
        finally:
            conn.close()
