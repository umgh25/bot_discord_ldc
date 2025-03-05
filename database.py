import sqlite3
from sqlite3 import Error
import os
from typing import List, Tuple
from pathlib import Path

# Créer un dossier data dans le répertoire du projet
DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / 'data'
DB_PATH = DATA_DIR / 'votes.db'

def create_connection():
    try:
        # Utiliser le chemin persistant sur Render
        db_path = '/data/bot_database.db' if os.path.exists('/data') else 'bot_database.db'
        conn = sqlite3.connect(db_path)
        return conn
    except Error as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return None

def ensure_data_dir():
    try:
        DATA_DIR.mkdir(exist_ok=True)
        print(f"Dossier data créé/vérifié: {DATA_DIR}")
        print(f"Permissions du dossier: {oct(os.stat(DATA_DIR).st_mode)[-3:]}")
        return True
    except Exception as e:
        print(f"Erreur création dossier: {e}")
        return False

def init_db():
    ensure_data_dir()
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            match_id TEXT NOT NULL,
            team TEXT NOT NULL,
            UNIQUE(user_id, match_id)
        )
        """)
        
        conn.commit()
        print(f"Base de données initialisée: {DB_PATH}")
        print(f"Permissions DB: {oct(os.stat(DB_PATH).st_mode)[-3:]}")
        return True
    except Exception as e:
        print(f"Erreur initialisation DB: {e}")
        return False
    finally:
        if conn:
            conn.close()

def save_vote(user_id: str, match_id: str, team: str) -> bool:
    if not DB_PATH.exists():
        init_db()
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT OR REPLACE INTO votes (user_id, match_id, team)
        VALUES (?, ?, ?)
        """, (user_id, match_id, team))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur sauvegarde vote: {e}")
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
    print("DEBUG - Tentative de récupération de tous les votes")  # Debug
    try:
        conn = sqlite3.connect('votes.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM votes")
        votes = cursor.fetchall()
        print(f"DEBUG - Votes récupérés : {votes}")  # Debug
        return votes
    except Exception as e:
        print(f"DEBUG - Erreur de récupération : {str(e)}")  # Debug
        return []
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

# Initialiser la DB au démarrage
init_db()
