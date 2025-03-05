import sqlite3
from sqlite3 import Error
import os
from typing import List, Tuple

# Définir le chemin absolu de la base de données
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'votes.db')

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

def save_vote(user_id: str, match_id: str, team: str) -> bool:
    print(f"DEBUG - Début save_vote avec : {user_id}, {match_id}, {team}")
    conn = None
    try:
        print(f"DEBUG - Chemin DB : {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Supprimer l'ancien vote s'il existe
        cursor.execute("DELETE FROM votes WHERE user_id = ? AND match_id = ?", 
                      (user_id, match_id))
                      
        # Insérer le nouveau vote
        cursor.execute("INSERT INTO votes (user_id, match_id, team) VALUES (?, ?, ?)",
                      (user_id, match_id, team))
        
        conn.commit()
        print("DEBUG - Vote sauvegardé avec succès")
        return True
        
    except Exception as e:
        print(f"DEBUG - Erreur détaillée dans save_vote : {str(e)}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
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

def get_all_votes() -> List[Tuple]:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM votes")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erreur de lecture : {e}")
        return []
    finally:
        if conn:
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

# Fonction d'initialisation de la base de données
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Créer la table si elle n'existe pas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            user_id TEXT,
            match_id TEXT,
            team TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, match_id)
        )
        """)
        
        conn.commit()
        print(f"Base de données initialisée à : {DB_PATH}")
    except sqlite3.Error as e:
        print(f"Erreur d'initialisation : {e}")
    finally:
        if conn:
            conn.close()
